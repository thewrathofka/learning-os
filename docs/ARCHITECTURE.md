# Architecture

## Two memory layers

**NotebookLM** is session memory — each command (except `code-explainer`, which uses a
shared "Code Reader" notebook, and `/coursetutor`, which lets you pick a notebook per
session) has one dedicated notebook. At the start of every session, the command asks that
notebook to summarize the last 3 sessions, so tutoring picks up where it left off without
you re-explaining context. At the end, the full transcript gets saved as a new source.

**Notion** is structured, queryable state — not a chat log, but a relational database of what
you're learning, why, and how far along you are. This is what makes "what have I actually
learned in the last 3 months" an answerable question instead of a chat-history archaeology
project.

## The Notion relationship map

```
🗂️ Learning Layers (1)
 ├── 📚 Courses (many)
 │    └── 📝 Lessons (many)
 │         └── 🔗 Bridge → 🧠 Skills
 ├── 💻 Practical Projects - Software (many) → 🧠 Skills
 └── 🔧 Practical Projects - Hardware (many) → 🧠 Skills

🧠 Skills Master Library
 ↔ Lessons, Courses, Layers, Hardware Projects
 (self-referencing: Parent Skill ↔ Sub-skills)

📓 Learning Log
 → Layer + Course + Lesson + Software + Hardware + Skills (one-way daily record)

📚 Textbooks ↔ Lessons, ↔ Courses
📎 Lesson Resources ↔ Lessons
📎 Textbook Resources → Textbooks
🌀 Chaos Hour (standalone — unstructured exploration log)
🏕️ Bootcamp → Textbooks, → Courses
```

Two things worth calling out because they're easy to get wrong when rebuilding this by hand:

1. **Most relations are one-directional (`single_property`), not two-way.** For example the
   Learning Log links out to Course/Layer/Lesson/etc., but none of those databases link back
   to the Log — it's a write-mostly daily record, not a lookup table. Only a handful of
   relations are genuinely two-way (`dual_property`): Layers↔Skills, Courses↔Textbooks,
   Courses↔Lessons, Courses↔Skills, Lessons↔Lesson Resources, Lessons↔Textbooks,
   Lessons↔Skills, and Skills↔Practical Projects (Hardware). See
   [NOTION_SCHEMA.md](NOTION_SCHEMA.md) for the exact classification per relation — it was
   derived by cross-checking every database's live property list against every other's, not
   assumed.
2. **Skills Master Library's "Parent Skill" and "Sub-skills" are one self-referencing
   relation pair, not two independent relations.** Building them separately produces two
   pairs of columns that don't behave as inverses of each other.

## Why two memory layers instead of one

NotebookLM is good at "what did we talk about" — fuzzy, conversational recall. Notion is good
at "show me every course tagged Layer 2 that's still Queued" — precise, structured queries.
Collapsing these into one system loses one side or the other; keeping them separate and
cross-referencing (Notion pages can hold a "NotebookLM URL" property) gets both.

## Setup is API-driven, not template-duplication

Rather than distributing this as a Notion "duplicate this template" link — which requires the
recipient to already trust and click through someone else's shared page, and breaks if Notion
changes how template sharing works — `/learning-os-setup` drives `scripts/setup_notion.py` to
build the entire 13-database structure from scratch in *your own* workspace via the Notion
API, given your own integration token and a page you've shared with it. See
[NOTION_SCHEMA.md](NOTION_SCHEMA.md) for exactly what gets built and why the build has to
happen in two passes (databases first, then relations) plus a dashboard-page pass sandwiched
around database creation so the databases render as embedded blocks rather than subpage links.
