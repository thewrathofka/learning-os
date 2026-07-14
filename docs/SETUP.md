# Setup

Follow these in order. Each step unblocks the next.

## 1. Install the plugin

```bash
git clone <this-repo-url> ~/projects/learning-os
```

Two ways to actually get the commands into Claude Code:

- **As a Claude Code plugin**: add `~/projects/learning-os` as a plugin directory (it already
  has a `.claude-plugin/plugin.json` manifest). See Claude Code's plugin docs for the exact
  install command for your version.
- **Manual fallback** (guaranteed to work): copy everything in `commands/` into
  `~/.claude/commands/`, and `skills/code-explainer/` into `~/.claude/skills/code-explainer/`.
  Note: with the manual fallback, `${CLAUDE_PLUGIN_ROOT}` won't be set — replace it in each
  command file with the absolute path to wherever you cloned this repo (e.g.
  `~/projects/learning-os`).

## 2. Create a Notion integration

1. Go to https://www.notion.so/my-integrations
2. "New integration" → name it (e.g. "Learning OS") → pick your workspace
3. Copy the "Internal Integration Secret" — you'll paste this into `/learning-os-setup`

## 3. Create/choose a parent page and share it with the integration

Pick any page in your Notion workspace (or create a new blank one) to hold the Learning OS
databases. This step is the one thing the Notion API genuinely cannot do for you — Notion
requires a human to explicitly grant an integration access to a page.

1. Open the page in Notion
2. Click the "•••" menu, top right
3. "Add connections" → search for your integration by name → select it
4. Copy the page's URL (or just its ID from the URL) — you'll need it in `/learning-os-setup`

If you skip this step, `/learning-os-setup` will fail at its very first check with a clear
"parent page not found" error pointing you back here.

## 4. Run `/learning-os-setup`

In Claude Code:

```
/learning-os-setup
```

Paste the integration token and parent page from Steps 2-3 when asked. This builds all 13
databases, wires up their relations (including the two circular/self-referencing ones), and
builds the "Learning OS" dashboard page — takes a few minutes since it's roughly 40
sequential Notion API calls. It's resumable: if it's interrupted, running the same command
again picks up where it left off.

## 5. `notebooklm login`

```bash
pip install notebooklm-py
notebooklm login
```

`/learning-os-setup` will ask whether you already have notebooks to point at, or want fresh
ones created — either way it writes the resulting notebook IDs into your config.

## 6. `gh auth login`

Only required if you plan to use `/hardwaretutor` or `/coursetutor`'s project-completion
flow, which pushes finished projects to a new GitHub repo under your username.

```bash
gh auth login
```

## 7. (Optional) Set up your profile

```bash
cp config/USER_PROFILE.example.md ~/.learning-os/USER_PROFILE.md
```

Edit it to describe your own background, goals, and current ceiling. Every tutor command
reads this to calibrate depth and tone. Skip this step entirely if you're fine with each
command's built-in default profile.

## 8. Verify

Run any command, e.g. `/tutor`. If it complains that config is missing, re-check
`~/.learning-os/config.env` exists and has the variables `config/config.env.example`
describes. If it loads and greets you normally, you're done.
