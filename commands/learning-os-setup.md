---
description: One-time Learning OS setup — builds the 13-database Notion workspace from scratch in your own account and writes ~/.learning-os/config.env for all six commands.
---

# Learning OS Setup

Walk the user through a one-time setup that builds their own copy of the Learning OS Notion
workspace and writes `~/.learning-os/config.env` so the other six commands work. This is
interactive — do not skip steps or guess values on the user's behalf.

## Step 1 — Check for existing config

```bash
test -f ~/.learning-os/config.env && echo "EXISTS" || echo "MISSING"
```

If it exists, show the user which variables are already set (names only, never print the
token value) and ask: "You already have a config. Re-run full setup, just fill in missing
values, or cancel?" Adjust the remaining steps to match their answer.

## Step 2 — Notion integration

Ask the user: "Have you already created a Notion integration?"

If not, walk them through it:
1. Go to https://www.notion.so/my-integrations
2. Click "New integration", give it any name (e.g. "Learning OS"), select your workspace
3. Copy the "Internal Integration Secret"

Ask the user to paste the token. Do not print it back in full once given.

## Step 3 — Parent page

Ask the user: "Pick (or create) a page in Notion where the Learning OS databases should
live, then share it with the integration: open the page, click the '•••' menu (top right),
Add connections, and select the integration you just created by name."

Once they confirm they've done this, ask for the page's URL or ID (either works — the
script accepts both).

## Step 4 — Verify access and build

Run the setup script with the token and parent page from Steps 2-3:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_notion.py" \
  --token "<TOKEN_FROM_STEP_2>" \
  --parent-page-id "<PAGE_ID_OR_URL_FROM_STEP_3>"
```

This is a multi-minute, ~40-request process (13 databases, ~20 relation properties, a
dashboard page). It's resumable — if it's interrupted or rate-limited, re-running the exact
same command picks up where it left off instead of duplicating anything.

If it fails at Pass 0 with "parent page was not found", the page wasn't actually shared with
the integration yet — send the user back to Step 3.

If it succeeds, tell the user: "Built. Open the 'Learning OS' page in Notion to see the 13
databases and the dashboard — worth a quick look to confirm everything landed where expected,
especially that the databases show up embedded in the page rather than as separate subpage
links. If they show up as subpage links instead of embedded tables, that's a known Notion API
nuance — drag them inline manually (drag the block by its handle) as a one-time fix."

## Step 5 — NotebookLM notebooks

Ask: "Do you already have `notebooklm login` set up?" If not, point them to notebooklm-py's
install/login instructions and wait.

Then: "Each tutor except /coursetutor saves to its own NotebookLM notebook. Do you have
existing notebooks to use, or should I create fresh ones?"

**If creating fresh ones:**
```bash
notebooklm create "AI Concept Tutor"
notebooklm create "Math for ML Tutor"
notebooklm create "Hardware Tutor"
notebooklm create "Problem of the Day"
notebooklm create "Code Reader"
```
Capture each returned notebook ID.

**If using existing ones:** ask the user for each of the 5 IDs (or notebook names, then
resolve to IDs via `notebooklm list --json`).

## Step 6 — GitHub username and paths

Ask for:
- GitHub username (used by `/hardwaretutor` and `/coursetutor`'s project-completion flow — skip if the user doesn't plan to use those)
- Where they keep notes/vault (default suggestion: `$HOME/life` — accept their answer or the default)
- Where they keep coding projects (default: `$HOME/projects`)
- Where problem-of-the-day session state should live (default: `$HOME/problem-sessions`)
- Where code-explainer sessions should be saved (default: `$HOME/study/AI & CS/code-reader`)

## Step 7 — Write the config file

Merge everything gathered (Notion DB IDs already written by the script in Step 4, plus the
NotebookLM IDs, GitHub username, and paths from Steps 5-6) into `~/.learning-os/config.env`.
Use `config/config.env.example` as the reference for variable names — don't invent new ones.

```bash
mkdir -p ~/.learning-os
# Update (don't fully overwrite) ~/.learning-os/config.env, preserving the NOTION_DB_* and
# NOTION_DASHBOARD_PAGE_ID values setup_notion.py already wrote in Step 4.
```

## Step 8 — Optional personalization

Ask: "Want to set up a personal profile now so the tutors calibrate depth/tone to you? (You
can skip this — each command has a sensible default.)"

If yes, copy `config/USER_PROFILE.example.md` to `~/.learning-os/USER_PROFILE.md` and help
the user fill in their own background/goals, replacing the worked example.

## Step 9 — Confirm

Report back:
- Which of the 13 databases + dashboard were created (link to the dashboard page if you have its URL)
- Which NotebookLM notebooks are wired up
- GitHub username and paths saved
- Whether a personal profile was set up
- Remind them: `notebooklm login` and `gh auth login` still need to be run once, if not done already
- Tell them they're ready to run `/tutor`, `/coursetutor`, `/mathtutor`, `/hardwaretutor`, or `/problemoftheday`
