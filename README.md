# Learning OS

> "The pyramid doesn't care how fast you climb it — it cares whether you actually built something on each level."

Learning OS is a philosophy about how to learn, backed by six Claude Code slash commands and
a 13-database Notion workspace that make the philosophy operational instead of aspirational.

## The philosophy: a top-down pyramid built around immediate value

Most self-directed learning plans start at the bottom — theory first, foundations first,
"you need to understand X before you can touch Y." This system inverts that. You start where
you can build and earn from day one, then progressively go deeper toward foundational
knowledge as you actually need it. Each layer makes you better at the layers above it. You
never stop being a builder — you just become a more powerful one.

### The Four Layers

Every layer runs two parallel tracks in this system's original form — **AI Play** (software,
models, agents, automation) and **Hardware Play** (Arduino → Raspberry Pi → bridging the
two) — though the pyramid works for any two tracks you want to build across.

1. **Layer 1 — Use & Build with AI.** Be a power user. Master AI tools, prompting, and simple
   automations. Build without needing to code. The goal is fluency across the entire tool
   ecosystem — knowing which tool to reach for, how to talk to it, and how to string tools
   together into real workflows.
2. **Layer 2 — Build Better.** Add just enough technical skill to build real things. You
   become a builder, not just a user — JSON, APIs, web basics, Python, SQL, GitHub, terminal.
3. **Layer 3 — Understand.** Go from building to understanding *why* things work. You can now
   reason about systems, not just use them — CS fundamentals, data engineering, software
   architecture, how the models you've been using actually work.
4. **Layer 4 — Root Knowledge.** The foundation everything else sits on. Most people never
   come here — it separates engineers from scientists. Math, electrical engineering, genuine
   model-level AI understanding.

`/learning-os-setup` builds this out as a real "Master Learning Roadmap" page in your Notion
workspace, not just a README description — see the child-page section of
[docs/NOTION_SCHEMA.md](docs/NOTION_SCHEMA.md) for the exact text it ships.

## The mechanism: a fully relational learning operating system

The six commands and the Notion workspace exist to make that philosophy trackable instead of
just aspirational — a place where "what have I actually learned, and where's the gap between
what a lesson requires and what I currently have" is an answerable question, not a feeling.

```
Learning Layer → Course → Lesson → Skills (via Bridge) → Practical Projects → Learning Log
```

Layers are the big multi-month arcs (Layer 1, Layer 2, ...). Courses and Textbooks sit inside
a Layer. Lessons sit inside a Course. The **Lesson-Skill Bridge** is the secret weapon — it's
where theory meets reality: required mastery vs. current mastery tells you exactly where the
gap is. Projects (software or hardware) and daily Learning Log entries close the loop back to
real work. Everything is connected. Nothing lives in a silo.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full relationship map and
[docs/NOTION_SCHEMA.md](docs/NOTION_SCHEMA.md) for every database's exact fields.

The six commands are how you actually interact with this day to day — each remembers your
last few sessions (via NotebookLM), teaches at a level calibrated to a profile you control,
and — where it makes sense — pushes what you did into the Notion workspace so you have a
durable record instead of a scattered chat history.

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
Notion databases, the dashboard page (with the philosophy above written into it, not just the
schema), and the Master Learning Roadmap page in your own workspace via the Notion API (no
manual "duplicate this template" step, no dependency on anyone else's shared page) and writes
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
- The original workspace this was extracted from also had a "Master Project Pipeline" section
  on the dashboard, pointing at a database that turned out to be empty and titleless when
  inspected — never actually built out. It's intentionally left out of the shipped template
  rather than replicated as broken.

## License

MIT — see [LICENSE](LICENSE).
