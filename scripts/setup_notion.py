#!/usr/bin/env python3
"""
Builds the full Learning OS Notion workspace (14 databases + relations + dashboard page)
from scratch via the Notion API, driven by notion_schema.json.

Pass design, required because Notion won't let you point a relation property at a
database that doesn't exist yet, and several of these 14 databases reference each other
circularly (Courses <-> Lessons <-> Skills <-> Layers):

  Pass 0 - verify the given parent page is actually shared with the integration
  Pass 1 - build the dashboard page in one linear walk over its block list, creating each
           database (including Master Project Pipeline and the "Master Learning Roadmap"
           child page) exactly where its position marker sits, so page content order
           matches creation order (see pass1_build_dashboard). Non-relation properties only.
  Pass 2 - PATCH in every relation property now that all database IDs are known
  Pass 2.5 - verify each dual-relation's auto-created reciprocal property name matches
             the schema; rename it if Notion's auto-naming didn't match (unconfirmed
             from docs whether synced_property_name is honored on every account/version)
  Pass 4 - write every created ID into ~/.learning-os/config.env

Resumable: progress is checkpointed to a JSON file after every database/pass, so a
rate-limited or interrupted run can pick back up without recreating anything.

No third-party dependencies (stdlib only), so this works with a bare `python3`.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"  # deprecated by Notion as of 2025-09-03 but still functional
                                # for single-data-source databases, which is what this creates.
                                # Centralized here so bumping it later is a one-line change.
API_ROOT = "https://api.notion.com/v1"

DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notion_schema.json")
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.learning-os/config.env")
DEFAULT_PROGRESS_PATH = os.path.expanduser("~/.learning-os/.setup-progress.json")


def notion_request(token, method, path, body=None, max_retries=5):
    """Thin wrapper over urllib with Notion-Version pinned and 429/Retry-After handling."""
    url = f"{API_ROOT}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Notion-Version", NOTION_VERSION)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8")
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", "2"))
                print(f"  rate limited, sleeping {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            raise RuntimeError(f"Notion API error {e.code} on {method} {path}: {payload}")
    raise RuntimeError(f"Exceeded retries on {method} {path}")


def extract_page_id(raw):
    """Accepts a bare page ID (hyphenated or not) or a full Notion URL and returns a bare ID.
    Notion page URLs end in a 32-hex-char ID (hyphens optional) after a title slug, e.g.
    https://notion.so/My-Page-39d3435e71948194ae94f923ef6edc60 - so we pull the LAST 32
    contiguous hex characters found anywhere in the string, rather than splitting on "-",
    which would incorrectly break a plain hyphenated UUID passed in directly."""
    hex_only = re.sub(r"[^0-9a-fA-F]", "", raw)
    if len(hex_only) < 32:
        raise ValueError(f"Could not find a 32-character page ID in: {raw}")
    return hex_only[-32:]


def load_schema(schema_path):
    with open(schema_path) as f:
        return json.load(f)


def load_progress(progress_path):
    if os.path.exists(progress_path):
        with open(progress_path) as f:
            return json.load(f)
    return {"database_ids": {}, "relations_done": [], "reciprocal_checked": [], "dashboard_page_id": None}


def save_progress(progress_path, progress):
    os.makedirs(os.path.dirname(progress_path), exist_ok=True)
    with open(progress_path, "w") as f:
        json.dump(progress, f, indent=2)


def build_property_config(prop_def):
    """Translate our simplified schema property declaration into a Notion property config."""
    ptype = prop_def["type"]
    if ptype == "title":
        return {"title": {}}
    if ptype == "rich_text":
        return {"rich_text": {}}
    if ptype == "number":
        return {"number": {}}
    if ptype == "date":
        return {"date": {}}
    if ptype == "checkbox":
        return {"checkbox": {}}
    if ptype == "url":
        return {"url": {}}
    if ptype == "files":
        return {"files": {}}
    if ptype == "select":
        return {"select": {"options": [{"name": o} for o in prop_def.get("options", [])]}}
    raise ValueError(f"Unhandled property type in schema: {ptype}")


def pass0_verify_parent(token, parent_page_id):
    print(f"Pass 0: verifying parent page {parent_page_id} is shared with this integration...")
    result = notion_request(token, "POST", "/search", {
        "filter": {"property": "object", "value": "page"}
    })
    found_ids = {r["id"].replace("-", "") for r in result.get("results", [])}
    if parent_page_id.replace("-", "") not in found_ids:
        raise RuntimeError(
            "The parent page was not found via /v1/search with this integration token.\n"
            "This almost always means the page hasn't been shared with the integration yet.\n"
            "In Notion: open the page -> '...' menu (top right) -> Add connections -> "
            "select your integration by name, then re-run this script."
        )
    print("  OK - parent page is accessible.")


def create_one_database(token, schema, progress, db_key, databases_parent_id):
    """Creates a single database (non-relation properties only) as a child of
    databases_parent_id. is_inline renders it as an embedded child_database block in the
    page rather than a standalone subpage link — matches the original layout."""
    db_def = schema["databases"][db_key]
    properties = {name: build_property_config(p) for name, p in db_def["properties"].items()}
    body = {
        "parent": {"type": "page_id", "page_id": databases_parent_id},
        "title": [{"type": "text", "text": {"content": db_def["title"]}}],
        "properties": properties,
        "is_inline": True,
    }
    result = notion_request(token, "POST", "/databases", body)
    progress["database_ids"][db_key] = result["id"]
    print(f"  {db_key}: created ({result['id']})")


def pass1_create_databases_flat(token, schema, progress, progress_path, databases_parent_id, only=None):
    """Used only for --only smoke-testing or --skip-dashboard runs, where databases are
    created directly under the given parent page rather than positioned within dashboard
    content (see pass1_build_dashboard for the real, positioned build)."""
    print("Pass 1: creating databases (non-relation properties only)...")
    for db_key in schema["creation_order"]:
        if only and db_key not in only:
            continue
        if db_key in progress["database_ids"]:
            print(f"  {db_key}: already created ({progress['database_ids'][db_key]}), skipping")
            continue
        create_one_database(token, schema, progress, db_key, databases_parent_id)
        save_progress(progress_path, progress)


def pass2_patch_relations(token, schema, progress, progress_path, only=None):
    print("Pass 2: adding relation properties...")
    for db_key in schema["creation_order"]:
        if only and db_key not in only:
            continue
        db_def = schema["databases"][db_key]
        db_id = progress["database_ids"][db_key]
        for rel in db_def.get("relations", []):
            rel_type = rel["type"]
            if rel_type == "auto_created":
                continue  # informational only; Notion creates this as a side effect elsewhere
            marker = f"{db_key}.{rel['property']}"
            if marker in progress["relations_done"]:
                print(f"  {marker}: already patched, skipping")
                continue
            target_key = db_key if rel_type == "dual_self" else rel["target"]
            if only and target_key not in only:
                print(f"  {marker}: skipping (target '{target_key}' not in --only set)")
                continue

            target_id = progress["database_ids"][target_key]
            relation_config = {"database_id": target_id}
            if rel_type in ("dual", "dual_self"):
                relation_config["type"] = "dual_property"
                relation_config["dual_property"] = {"synced_property_name": rel["reciprocal_name"]}
            elif rel_type == "single":
                relation_config["type"] = "single_property"
                relation_config["single_property"] = {}
            else:
                raise ValueError(f"Unknown relation type '{rel_type}' on {marker}")

            body = {"properties": {rel["property"]: {"relation": relation_config}}}
            try:
                notion_request(token, "PATCH", f"/databases/{db_id}", body)
            except RuntimeError as e:
                if "synced_property_name" in str(e) or "dual_property" in str(e):
                    # Fallback: some API versions may reject synced_property_name.
                    # Retry with an empty dual_property and let Notion auto-name the
                    # reciprocal; Pass 2.5 below checks and renames it if needed.
                    print(f"  {marker}: retrying without synced_property_name ({e})")
                    relation_config["dual_property"] = {}
                    body = {"properties": {rel["property"]: {"relation": relation_config}}}
                    notion_request(token, "PATCH", f"/databases/{db_id}", body)
                else:
                    raise
            progress["relations_done"].append(marker)
            save_progress(progress_path, progress)
            print(f"  {marker}: patched -> {rel.get('target', db_key)}")


def pass2_5_verify_reciprocals(token, schema, progress, progress_path, only=None):
    """
    Confirms every dual/dual_self relation's auto-created reciprocal property landed with
    the exact name the schema expects, and renames it if Notion's auto-naming didn't match.
    This is the empirical check the plan flagged as unconfirmed from docs alone.
    """
    print("Pass 2.5: verifying auto-created reciprocal property names...")
    for db_key in schema["creation_order"]:
        if only and db_key not in only:
            continue
        db_def = schema["databases"][db_key]
        for rel in db_def.get("relations", []):
            if rel["type"] not in ("dual", "dual_self"):
                continue
            marker = f"{db_key}.{rel['property']}.reciprocal"
            if marker in progress["reciprocal_checked"]:
                continue
            target_key = db_key if rel["type"] == "dual_self" else rel["target"]
            if only and target_key not in only:
                continue
            target_id = progress["database_ids"][target_key]
            target_db = notion_request(token, "GET", f"/databases/{target_id}")
            expected_name = rel["reciprocal_name"]
            if expected_name in target_db["properties"]:
                print(f"  {marker}: OK ('{expected_name}' present on {target_key})")
            else:
                # Find the property that relates back to db_key's relation prop and rename it.
                actual_name = None
                for pname, pdef in target_db["properties"].items():
                    if pdef["type"] == "relation" and pdef["relation"].get("database_id", "").replace("-", "") == progress["database_ids"][db_key].replace("-", ""):
                        actual_name = pname
                        break
                if actual_name and actual_name != expected_name:
                    print(f"  {marker}: auto-named '{actual_name}', renaming to '{expected_name}'")
                    notion_request(token, "PATCH", f"/databases/{target_id}", {
                        "properties": {actual_name: {"name": expected_name}}
                    })
                else:
                    print(f"  {marker}: WARNING - could not locate reciprocal property on {target_key}, leaving as-is")
            progress["reciprocal_checked"].append(marker)
            save_progress(progress_path, progress)


def build_block(b):
    """Translate one schema dashboard-block declaration into a Notion API block object.
    The 'child_databases' marker is handled by the caller, not here — a child_database
    block can't be created directly via blocks.children.append; it only appears
    automatically when a database is created with this page as its parent."""
    if b["type"] == "callout":
        callout_obj = {"rich_text": [{"type": "text", "text": {"content": b["text"]}}]}
        if "icon" in b:
            callout_obj["icon"] = {"type": "emoji", "emoji": b["icon"]}
        return {"object": "block", "type": "callout", "callout": callout_obj}
    if b["type"] == "divider":
        return {"object": "block", "type": "divider", "divider": {}}
    if b["type"] == "quote":
        return {"object": "block", "type": "quote", "quote": {
            "rich_text": [{"type": "text", "text": {"content": b["text"]}}]
        }}
    if b["type"] == "paragraph":
        return {"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": b["text"]}}]
        }}
    if b["type"] == "heading_2":
        return {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": b["text"]}}]
        }}
    if b["type"] == "heading_3":
        return {"object": "block", "type": "heading_3", "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": b["text"]}}]
        }}
    if b["type"] == "code":
        return {"object": "block", "type": "code", "code": {
            "rich_text": [{"type": "text", "text": {"content": b["text"]}}],
            "language": b.get("language", "plain text"),
        }}
    if b["type"] == "table":
        # Unlike callouts, Notion requires a table's rows as "children" INLINE in the
        # same creation call — a follow-up children-append call is rejected with
        # "table.children should be defined". So rows go in here, not as a nested
        # 'children' schema key handled later by append_blocks_recursive.
        width = len(b["rows"][0]) if b["rows"] else 2
        return {"object": "block", "type": "table", "table": {
            "table_width": width,
            "has_column_header": b.get("has_column_header", True),
            "has_row_header": False,
            "children": build_table_row_blocks(b["rows"]),
        }}
    raise ValueError(f"Unhandled dashboard block type: {b['type']}")


def build_table_row_blocks(rows):
    return [
        {"object": "block", "type": "table_row", "table_row": {
            "cells": [[{"type": "text", "text": {"content": cell}}] for cell in row]
        }}
        for row in rows
    ]


def append_blocks_recursive(token, parent_id, schema_blocks):
    """Appends schema_blocks under parent_id, then recursively appends any nested 'children'
    a block declares (e.g. the numbered list nested inside the "Learning Loop" callout).
    That has to be a follow-up call per Notion's API, since block-append only returns IDs
    for the blocks you just created. Table rows are the one exception — Notion requires
    those inline in the same creation call, so build_block already embeds them; there's
    nothing left to do for tables here."""
    flat_blocks = []
    schema_refs = []  # parallel to flat_blocks; None for expanded list items (no further nesting)
    for b in schema_blocks:
        if b["type"] == "numbered_list":
            for item in b["items"]:
                flat_blocks.append({"object": "block", "type": "numbered_list_item", "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }})
                schema_refs.append(None)
        elif b["type"] == "bulleted_list":
            for item in b["items"]:
                flat_blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }})
                schema_refs.append(None)
        else:
            flat_blocks.append(build_block(b))
            schema_refs.append(b)

    for i in range(0, len(flat_blocks), 100):
        chunk_blocks = flat_blocks[i:i + 100]
        chunk_refs = schema_refs[i:i + 100]
        result = notion_request(token, "PATCH", f"/blocks/{parent_id}/children", {"children": chunk_blocks})
        for created, ref in zip(result["results"], chunk_refs):
            if not ref:
                continue
            if ref.get("children") and ref["type"] != "table":
                append_blocks_recursive(token, created["id"], ref["children"])


def pass1_build_dashboard(token, schema, progress, progress_path):
    """Creates the dashboard page, then walks dashboard.blocks in a single linear pass,
    appending normal content as a buffer and flushing it whenever a position marker is
    reached. Content order equals creation order by construction, so a database created at
    a 'child_database_single' marker (e.g. Master Project Pipeline) lands exactly where its
    heading says it should, instead of needing a separate workaround.

    Three markers, handled inline as they're reached:
      - child_pages_marker: create + populate child page(s) (e.g. Master Learning Roadmap)
      - child_database_single: create one specific named database here
      - child_databases: create every remaining not-yet-created database from creation_order

    Resumable via a cursor index into dashboard.blocks, checkpointed after each block/marker,
    so an interrupted or rate-limited run picks back up without recreating anything."""
    dash = schema["dashboard"]
    if not progress.get("dashboard_page_id"):
        print("Pass 1: creating the dashboard page...")
        page = notion_request(token, "POST", "/pages", {
            "parent": {"type": "page_id", "page_id": progress["parent_page_id"]},
            "properties": {"title": [{"type": "text", "text": {"content": dash["page_title"]}}]},
        })
        progress["dashboard_page_id"] = page["id"]
        progress["dashboard_cursor"] = 0
        save_progress(progress_path, progress)
    dashboard_id = progress["dashboard_page_id"]
    cursor = progress.get("dashboard_cursor", 0)

    buffer = []

    def flush(checkpoint_index):
        """Sends whatever's buffered, THEN advances the saved cursor. The order matters:
        a single blocks.children.append call is all-or-nothing (confirmed empirically —
        a batch that fails validation partway creates none of its blocks), so it's only
        safe to mark these blocks as done once the call actually succeeds. Advancing the
        cursor first (checkpointing "buffered" as if it were "sent") was the bug that let
        an earlier crash mid-flush silently drop everything sitting in the buffer at the
        time, since resume would skip past them without ever re-sending them."""
        if buffer:
            append_blocks_recursive(token, dashboard_id, buffer)
            buffer.clear()
        progress["dashboard_cursor"] = checkpoint_index
        save_progress(progress_path, progress)

    print("Pass 1: building dashboard content and databases in page order...")
    for i, b in enumerate(dash["blocks"]):
        if i < cursor:
            continue
        if b["type"] == "child_pages_marker":
            flush(i)
            if not progress.get("child_pages_done"):
                for child in dash.get("child_pages", []):
                    child_page = notion_request(token, "POST", "/pages", {
                        "parent": {"type": "page_id", "page_id": dashboard_id},
                        "properties": {"title": [{"type": "text", "text": {"content": child["title"]}}]},
                    })
                    if child.get("blocks"):
                        append_blocks_recursive(token, child_page["id"], child["blocks"])
                progress["child_pages_done"] = True
            progress["dashboard_cursor"] = i + 1
            save_progress(progress_path, progress)
        elif b["type"] == "child_database_single":
            flush(i)
            if b["database"] not in progress["database_ids"]:
                create_one_database(token, schema, progress, b["database"], dashboard_id)
            progress["dashboard_cursor"] = i + 1
            save_progress(progress_path, progress)
        elif b["type"] == "child_databases":
            flush(i)
            for db_key in schema["creation_order"]:
                if db_key not in progress["database_ids"]:
                    create_one_database(token, schema, progress, db_key, dashboard_id)
            progress["dashboard_cursor"] = i + 1
            save_progress(progress_path, progress)
        else:
            buffer.append(b)
            # Cursor deliberately NOT advanced here — only once flush() actually sends this block.

    flush(len(dash["blocks"]))
    print(f"  dashboard built: {dashboard_id}")
    return dashboard_id


def pass4_write_config(schema, progress, config_path):
    print(f"Pass 4: writing database IDs to {config_path}...")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    lines = []
    if os.path.exists(config_path):
        with open(config_path) as f:
            lines = f.readlines()

    def upsert(lines, key, value):
        prefix = f"{key}="
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                lines[i] = f"{prefix}{value}\n"
                return
        lines.append(f"{prefix}{value}\n")

    for db_key, db_id in progress["database_ids"].items():
        upsert(lines, schema["databases"][db_key]["config_var"], db_id)
    if progress.get("dashboard_page_id"):
        upsert(lines, "NOTION_DASHBOARD_PAGE_ID", progress["dashboard_page_id"])

    with open(config_path, "w") as f:
        f.writelines(lines)
    print("  done.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("NOTION_API_TOKEN"),
                         help="Notion integration token (or set NOTION_API_TOKEN)")
    parser.add_argument("--parent-page-id", required=True,
                         help="Page ID (or full URL) of a page you've shared with the integration")
    parser.add_argument("--schema-path", default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--progress-path", default=DEFAULT_PROGRESS_PATH)
    parser.add_argument("--only", default=None,
                         help="Comma-separated list of database keys to build, for smoke-testing "
                              "(e.g. --only learning_layers,skills_master_library). Omit for the full run.")
    parser.add_argument("--skip-dashboard", action="store_true",
                         help="Skip the dashboard page and create databases flat under --parent-page-id "
                              "instead — useful when smoke-testing with --only")
    args = parser.parse_args()

    if not args.token:
        print("Error: no Notion token. Pass --token or set NOTION_API_TOKEN.", file=sys.stderr)
        sys.exit(1)

    # Accept a pasted Notion URL as well as a bare page ID.
    parent_page_id = extract_page_id(args.parent_page_id)

    schema = load_schema(args.schema_path)
    progress = load_progress(args.progress_path)
    progress["parent_page_id"] = parent_page_id
    save_progress(args.progress_path, progress)

    only = set(args.only.split(",")) if args.only else None
    building_dashboard = not args.skip_dashboard and not only

    pass0_verify_parent(args.token, parent_page_id)

    if building_dashboard:
        # Single linear pass builds the dashboard page AND creates all databases in their
        # correct page-content position (see pass1_build_dashboard's docstring).
        pass1_build_dashboard(args.token, schema, progress, args.progress_path)
    else:
        pass1_create_databases_flat(args.token, schema, progress, args.progress_path, parent_page_id, only=only)

    pass2_patch_relations(args.token, schema, progress, args.progress_path, only=only)
    pass2_5_verify_reciprocals(args.token, schema, progress, args.progress_path, only=only)
    pass4_write_config(schema, progress, args.config_path)

    print("\nDone. Database IDs (and dashboard page ID, if built) written to", args.config_path)
    print("Remaining config vars (NotebookLM IDs, GitHub username, vault paths) still need to be filled in —")
    print("see config/config.env.example, or let /learning-os-setup prompt you for them.")


if __name__ == "__main__":
    main()
