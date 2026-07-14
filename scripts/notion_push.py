#!/usr/bin/env python3
"""
Shared helper for creating (or updating) a single Notion page, used by the tutor commands
instead of each repeating its own curl block. Centralizes the Notion-Version header (so
bumping it later is a one-line change) and 429/Retry-After handling.

Usage:
  python3 notion_push.py --database-id "$NOTION_DB_COURSES" --properties '{
    "Course Name": {"title": [{"text": {"content": "Example Course"}}]},
    "Priority": {"select": {"name": "Next"}}
  }'

Prints the created (or updated) page's bare id to stdout on success, so a calling command
can capture it for a later relation (e.g. linking a textbook to the course page just created):
  COURSE_ID=$(python3 notion_push.py --database-id "$NOTION_DB_COURSES" --properties '...')

On failure, prints the Notion error to stderr and exits non-zero.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"  # kept in sync with setup_notion.py — see that file's header
                                # comment for the 2025-09-03 deprecation risk note.
API_ROOT = "https://api.notion.com/v1"


def notion_request(token, method, path, body=None, max_retries=5):
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
                print(f"rate limited, sleeping {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            raise RuntimeError(f"Notion API error {e.code} on {method} {path}: {payload}")
    raise RuntimeError(f"Exceeded retries on {method} {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--token", default=os.environ.get("NOTION_API_TOKEN"),
                         help="Notion integration token (or set NOTION_API_TOKEN)")
    parser.add_argument("--database-id", help="Target database ID (for creating a new page)")
    parser.add_argument("--page-id", help="Existing page ID to update instead of creating a new one")
    parser.add_argument("--properties", required=True, help="JSON object of Notion page properties")
    args = parser.parse_args()

    if not args.token:
        print("Error: no Notion token. Pass --token or set NOTION_API_TOKEN.", file=sys.stderr)
        sys.exit(1)
    if not args.database_id and not args.page_id:
        print("Error: pass either --database-id (create) or --page-id (update).", file=sys.stderr)
        sys.exit(1)

    try:
        properties = json.loads(args.properties)
    except json.JSONDecodeError as e:
        print(f"Error: --properties is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.page_id:
            result = notion_request(args.token, "PATCH", f"/pages/{args.page_id}", {"properties": properties})
        else:
            result = notion_request(args.token, "POST", "/pages", {
                "parent": {"database_id": args.database_id},
                "properties": properties,
            })
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result["id"])


if __name__ == "__main__":
    main()
