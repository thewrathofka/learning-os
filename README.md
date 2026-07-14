# Learning OS

Six Claude Code slash commands, backed by NotebookLM session memory and a 13-database
Notion workspace, for structured self-directed learning: courses and textbooks you're
working through, lessons and skills you're building, projects you've shipped, and a daily
log tying it all together.

Every command remembers your last few sessions (via NotebookLM), teaches at a level
calibrated to a profile you control, and — where it makes sense — pushes what you did into
the Notion workspace so you have a durable record instead of a scattered chat history.

## The core loop

```
Learning Layer → Course → Lesson → Skills (via Bridge) → Practical Projects → Learning Log
```

Layers are big multi-month arcs ("Building with LLMs & Agents"). Courses and Textbooks sit
inside a Layer. Lessons sit inside a Course. The Lesson-Skill Bridge tracks required vs.
current mastery per skill per lesson — that gap is the whole point of the system. Projects
(software or hardware) and daily Learning Log entries close the loop back to real work.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full relationship map and
[docs/NOTION_SCHEMA.md](docs/NOTION_SCHEMA.md) for every database's exact fields.

`/learning-os-setup` also creates a "Master Learning Roadmap" child page under the dashboard,
containing a general **Four Layers** framework (Use & Build → Build Better → Understand →
Root Knowledge) for thinking about where a given Course or Lesson sits on the
beginner-to-foundational spectrum — see the child-page section of
[docs/NOTION_SCHEMA.md](docs/NOTION_SCHEMA.md) for the full text.

## Commands

| Command | What it does |
|---|---|
| `/learning-os-setup` | One-time setup — builds your Notion workspace and writes local config |
| `/tutor` | AI/ML concept tutor — layered explanations (intuitive → technical → ceiling), from a textbook |
| `/coursetutor` | AI concept tutor with real code walkthroughs, plus a step-by-step project-build mode that ships to GitHub |
| `/mathtutor` | Math for ML — every concept grounded in a real system (Spotify, GPS, Netflix...) with symbolic math and 2D/3D visualizations |
| `/hardwaretutor` | Hands-on Arduino/Raspberry Pi mentor — wiring photo review, code debugging, circuit simulation, build-along project mode |
| `/problemoftheday` | Adaptive daily problem-solving coach, levels 1-10, ML-engineering-biased problem selection |
| `code-explainer` (Skill, auto-triggers) | Explains existing code via inline teaching comments, a README with an analogy, and a Mermaid diagram |

## Prerequisites

- **Python 3.9+** — used by `scripts/setup_notion.py` and `scripts/notion_push.py` (stdlib only, no pip installs needed for those two)
- **A Notion account** and an [internal integration](https://www.notion.so/my-integrations) — see [docs/SETUP.md](docs/SETUP.md)
- **[notebooklm-py](https://pypi.org/project/notebooklm-py/)** — install it, then run `notebooklm login`
- **[GitHub CLI](https://cli.github.com/)** (`gh`) + `gh auth login` — only needed if you use `/hardwaretutor` or `/coursetutor`'s project-completion flow
- Per-command extras: `sympy`/`numpy`/`matplotlib`/`plotly` for `/mathtutor`; `arduino-cli`, `Schemdraw`, `PySpice`+`ngspice`, `PlatformIO` for `/hardwaretutor`; `graphviz` (optional) for `/problemoftheday`

## Setup

See [docs/SETUP.md](docs/SETUP.md) for the full walkthrough. Short version:

```bash
git clone <this-repo> ~/projects/learning-os
# add ~/projects/learning-os as a Claude Code plugin (or copy commands/ into ~/.claude/commands/)
```

Then in Claude Code, run `/learning-os-setup` and follow the prompts — it builds the 13
Notion databases and dashboard page in your own workspace via the Notion API (no manual
"duplicate this template" step, no dependency on anyone else's shared page) and writes
`~/.learning-os/config.env`.

## Personalizing

Every command reads an optional `$LEARNING_OS_USER_PROFILE_PATH` markdown file to calibrate
depth and tone — see [config/USER_PROFILE.example.md](config/USER_PROFILE.example.md). If you
skip it, each command falls back to a sensible default profile.

## Known rough edges

- The Notion API deprecated `Notion-Version: 2022-06-28` (what this project pins to) as of a
  2025-09-03 upgrade that introduced a `data_sources` layer. It still works for the
  single-data-source databases this setup creates, but Notion could sunset it — see the
  header comment in `scripts/setup_notion.py` before upgrading.
- Newly created databases are requested as inline (`is_inline: true`) so they render embedded
  in the dashboard page rather than as separate subpage links. If they show up as subpages
  instead, drag them inline manually in Notion — a one-time fix.

## License

MIT — see [LICENSE](LICENSE).
