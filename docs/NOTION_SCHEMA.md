# Notion Schema Reference

Human-readable mirror of `scripts/notion_schema.json`, the single source of truth
`setup_notion.py` builds from. If you'd rather build this by hand in Notion's UI
instead of running `/learning-os-setup`, this is the exact reference to build against.

Notion API version: `2022-06-28` (see the risk note in `scripts/setup_notion.py`'s header).

## Databases (in creation order)

### Learning Layers

Config variable: `NOTION_DB_LEARNING_LAYERS`

| Property | Type | Notes |
|---|---|---|
| Layer Name | title |  |
| Layer Number | number |  |
| Description | rich_text |  |
| Start Date | date |  |
| Target Completion Date | date |  |
| Status | select | Active, In Progress, Completed |
| Related Skills | relation (two-way) | ↔ Skills Master Library.Related Layers |

### Courses

Config variable: `NOTION_DB_COURSES`

| Property | Type | Notes |
|---|---|---|
| Course Name | title |  |
| Course URL | url |  |
| Description | rich_text |  |
| Priority | select | Right Away, Next, For Later Layers, Queued |
| Start Date | date |  |
| Topic | select | Math for AI, RAG, Problem Solving, Programming, LLMs & Agents, Statistics & Probability |
| NotebookLM URL | url |  |
| Status | select | Queued, In Progress, Completed, Backlog |
| Textbooks | relation (two-way) | ↔ Textbooks.Related Courses |
| Lessons | relation (two-way) | ↔ Lessons.Parent Course |
| Related Skills | relation (two-way) | ↔ Skills Master Library.Related Courses |
| Parent Layer | relation (one-way) | → Learning Layers (no reciprocal property) |

### Lessons

Config variable: `NOTION_DB_LESSONS`

| Property | Type | Notes |
|---|---|---|
| Lesson Name | title |  |
| Rabbit Holes Encountered | rich_text |  |
| Textbook Chapters | rich_text |  |
| Topic | select | Math for AI, RAG, Problem Solving, Programming, LLMs & Agents, Statistics & Probability |
| Priority | select | Right Away, Next, For Later Layers, Queued |
| Date Started | date |  |
| Status | select | In Progress, Completed, Derailed |
| Resources | relation (two-way) | ↔ Lesson Resources.Lesson |
| Textbooks | relation (two-way) | ↔ Textbooks.Related Lessons |
| Related Skills | relation (two-way) | ↔ Skills Master Library.Related Lessons |
| Parent Layer | relation (one-way) | → Learning Layers (no reciprocal property) |
| Parent Course | relation (auto-created) | created automatically as the reciprocal of courses.Lessons — do not create independently |

### Skills Master Library

Config variable: `NOTION_DB_SKILLS_MASTER`

| Property | Type | Notes |
|---|---|---|
| Skill Name | title |  |
| Skill Level | select | Zero, I don't get it, I should get it, I am familiar, I get it, Forgot everything, Pretty Pretty Pretty Good |
| Knowledge in Layer | number |  |
| Parent Skill | relation (two-way) | ↔ Skills Master Library.Sub-skills |
| Hardware Projects | relation (two-way) | ↔ Practical Projects - Hardware.Technologies / Skills Used |
| Software Projects | relation (one-way) | → Practical Projects - Software (no reciprocal property) |
| Related Layers | relation (auto-created) | created automatically as the reciprocal of learning_layers.Related Skills |
| Related Courses | relation (auto-created) | created automatically as the reciprocal of courses.Related Skills |
| Related Lessons | relation (auto-created) | created automatically as the reciprocal of lessons.Related Skills |

### Lesson-Skill Bridge

Config variable: `NOTION_DB_LESSON_SKILL_BRIDGE`

| Property | Type | Notes |
|---|---|---|
| Bridge Entry | title |  |
| Importance | select | Primary, Secondary, Foundational |
| Discovery Date | date |  |
| Required Mastery Level | number |  |
| Current Mastery Level | number |  |
| Lesson | relation (one-way) | → Lessons (no reciprocal property) |
| Skill | relation (one-way) | → Skills Master Library (no reciprocal property) |

### Practical Projects - Software

Config variable: `NOTION_DB_PROJECTS_SOFTWARE`

| Property | Type | Notes |
|---|---|---|
| Project Name | title |  |
| Description | rich_text |  |
| GitHub / Code Link | url |  |
| Key Learnings | rich_text |  |
| Start Date | date |  |
| Completion Date | date |  |
| Status | select | Completed, In Progress |
| Software Projects | relation (auto-created) | no reciprocal — skills_master_library.Software Projects is single_property, so this database intentionally has no relation column pointing back |

### Practical Projects - Hardware

Config variable: `NOTION_DB_PROJECTS_HARDWARE`

| Property | Type | Notes |
|---|---|---|
| Project Name | title |  |
| Description | rich_text |  |
| Materials / Components Needed | rich_text |  |
| Key Learnings | rich_text |  |
| Start Date | date |  |
| Completion Date | date |  |
| Status | select | Planning, In Progress, Completed, On Hold |
| Related Course | relation (one-way) | → Courses (no reciprocal property) |
| Parent Layer | relation (one-way) | → Learning Layers (no reciprocal property) |
| Related Lessons | relation (one-way) | → Lessons (no reciprocal property) |
| Technologies / Skills Used | relation (auto-created) | created automatically as the reciprocal of skills_master_library.Hardware Projects |

### Learning Log

Config variable: `NOTION_DB_LEARNING_LOG`

| Property | Type | Notes |
|---|---|---|
| Log Entry | title |  |
| Discoveries | rich_text |  |
| Date | date |  |
| Rabbit Hole Encountered | checkbox |  |
| Notes / Reflections | rich_text |  |
| Time Spent (hrs) | number |  |
| Progress on Mastery Levels | rich_text |  |
| Rabbit Hole Description | rich_text |  |
| Software Project Worked On | relation (one-way) | → Practical Projects - Software (no reciprocal property) |
| Skills Practiced Today | relation (one-way) | → Skills Master Library (no reciprocal property) |
| Course Worked On | relation (one-way) | → Courses (no reciprocal property) |
| Layer Worked On | relation (one-way) | → Learning Layers (no reciprocal property) |
| Textbooks | relation (one-way) | → Textbooks (no reciprocal property) |
| Hardware Project Worked On | relation (one-way) | → Practical Projects - Hardware (no reciprocal property) |
| Lesson Worked On | relation (one-way) | → Lessons (no reciprocal property) |

### Lesson Resources

Config variable: `NOTION_DB_LESSON_RESOURCES`

| Property | Type | Notes |
|---|---|---|
| Resource Name | title |  |
| Notes | rich_text |  |
| Type | select | Article, Documentation, Video, Tool, Book, Other |
| URL | url |  |
| Date Added | date |  |
| File / Attachment | files |  |
| Review Status | select | Should Review, Reviewed |
| Lesson | relation (auto-created) | created automatically as the reciprocal of lessons.Resources |

### Textbooks

Config variable: `NOTION_DB_TEXTBOOKS`

| Property | Type | Notes |
|---|---|---|
| Book Name | title |  |
| Topic | select | Math for AI, RAG, Problem Solving, Programming, LLMs & Agents, Statistics & Probability |
| Date Started | date |  |
| Pages Completed | number |  |
| Priority | select | Right Away, Next, For Later Layers |
| Total Pages | number |  |
| Author | rich_text |  |
| Status | select | Not Started, In Progress, Completed |
| NotebookLM URL | url |  |
| Related Skills | relation (one-way) | → Skills Master Library (no reciprocal property) |
| Parent Layer | relation (one-way) | → Learning Layers (no reciprocal property) |
| Related Courses | relation (auto-created) | created automatically as the reciprocal of courses.Textbooks |
| Related Lessons | relation (auto-created) | created automatically as the reciprocal of lessons.Textbooks |

### Textbook Resources

Config variable: `NOTION_DB_TEXTBOOK_RESOURCES`

| Property | Type | Notes |
|---|---|---|
| Resource Name | title |  |
| Description | rich_text |  |
| Chapter Pairing | rich_text |  |
| Resource Type | select | YouTube Video, YouTube Playlist, YouTube Channel, Guide/Article, Udemy Course |
| URL | url |  |
| Related Textbook | relation (one-way) | → Textbooks (no reciprocal property) |

### Chaos Hour

Config variable: `NOTION_DB_CHAOS_HOUR`

| Property | Type | Notes |
|---|---|---|
| Entry | title |  |
| Date & Time | date |  |
| Description | rich_text |  |
| Useful Learned | rich_text |  |
| Feeling Afterwards | select | Energized, Inspired, Focused, Neutral, Scattered, Drained, Frustrated |
| Action Necessary | checkbox |  |
| Hours | number |  |
| Action Steps | rich_text |  |

### Bootcamp

Config variable: `NOTION_DB_BOOTCAMP`

| Property | Type | Notes |
|---|---|---|
| Track Name | title |  |
| Current Position | rich_text |  |
| Progress Log | rich_text |  |
| Starting Position | rich_text |  |
| Category | select | Math, Applied Reading, Python, Terminal, Code Reading, Project, Slow Burn, CS Fundamentals, ML Certification, Algorithms |
| Source | select | /mathtutor, /tutor, /coursetutor, /code-explainer, /problemoftheday, Kaggle, YouTube, Book, Manual, Coursera |
| Status | select | Not Started, In Progress, Completed, Blocked |
| Hours Logged | number |  |
| Day 5 Goal | rich_text |  |
| Related Textbook | relation (one-way) | → Textbooks (no reciprocal property) |
| Related Course | relation (one-way) | → Courses (no reciprocal property) |

## Dashboard page

Title: **Learning OS**, with child page(s): Master Learning Roadmap.

### Dashboard page content (verbatim)

> **🔄 Learning Loop**

---

> "The more I learn, the more I realize how much I don't know." — Einstein. Guy had a point.

This is Kali's Learning Operating System — a fully relational system for tracking skill mastery across layers, courses, lessons, projects, and daily log entries.

---

#### How This Works

> **💡 The Core Loop: Layer → Course → Lesson → Skills (via Bridge) → Practical Projects → Daily Log. Everything is connected. Nothing lives in a silo.**

---

#### 📂 The Databases

*(all 13 databases embedded here, in creation order)*

---

#### 🔗 Relationship Map

```
🗂️ Learning Layers (1)
 ├── 📚 Courses (many)
 │    └── 📝 Lessons (many)
 │         └── 🔗 Bridge → 🧠 Skills
 ├── 💻 Software Projects (many) → 🧠 Skills
 └── 🔧 Hardware Projects (many) → 🧠 Skills

🧠 Skills Master Library
 ↔ Lessons, Courses, Layers, Hardware Projects

📓 Learning Log
 → Layer + Course + Lesson + Software + Hardware + Skills
```

#### ✍️ Workflow (How to Actually Use This)

1. Add a Course in Courses, link it to the Layer
2. Create a Layer in Learning Layers (e.g. Layer 1 — Building with LLMs & Agents)
3. Add Lessons inside that Course, link to Layer too
4. Add Skills to the Skills Master Library with a Skill Level
5. Create Bridge entries to track required vs. current mastery per lesson

#### ⚠️ Things Worth Knowing

- Sub-skills on the Skills Library is a relation, not a text field — use it for genuine skill hierarchies.
- The Bridge Table is where theory meets reality — required mastery vs. current mastery tells you exactly where the gap is.
- The Learning Log links out to Layer/Course/Lesson/Software/Hardware/Skills but none of those databases link back — the Log is a one-way daily record, not a two-way lookup.
- Rabbit Holes live in two places: Lessons (notes on what derailed you) and the Log (checkbox + description). Both matter.

### Child page: Master Learning Roadmap

*Generic Four Layers framework only. The original personal roadmap this was extracted from also had a daily schedule, a course-enrollment stack, and an unrelated business project section — intentionally left out of the public template as too personal/specific to ship.*

> The pyramid doesn't care how fast you climb it — it cares whether you actually built something on each level.

---

#### The Big Idea

This is a top-down learning pyramid built around immediate value. You start where you can build and earn from day one, then progressively go deeper toward foundational knowledge. Each layer makes you better at the layers above it. You never stop being a builder — you just become a more powerful one.

Each layer has two parallel tracks (adapt these to your own domains — the example below is AI + hardware, but the pyramid works for any two tracks you want to build across):

- AI Play — software, models, agents, automation
- Hardware Play — Arduino → Raspberry Pi → bridging the two

---

#### The Four Layers

##### Layer 1 — Use & Build with AI

Be a power user. Master AI tools, prompting, and simple automations. Build without needing to code. The goal is fluency across the entire AI tool ecosystem — knowing which tool to reach for, how to talk to it, and how to string tools together into real workflows.

AI Play: Claude, ChatGPT, Gemini, Perplexity, NotebookLM, n8n, Make, Bolt.new, Lovable, v0.dev, Cursor, Replit, Midjourney, Flux, Runway, ElevenLabs, Suno, Descript, Apify, Relevance AI, Dust.tt

Hardware Play: Arduino starter projects — LED, sensors, servos, basic circuits

##### Layer 2 — Build Better

Add just enough technical skill to build real things. You become a builder, not just a user.

JSON, APIs, web basics, Python lite, SQL, n8n advanced, GitHub, terminal, web scraping, Claude Code, basic JavaScript.

AI Play: RAG systems, AI agents with tools, multi-agent workflows, skills and memory architecture

Hardware Play: Transition from Arduino to Raspberry Pi, first bridge projects between the two

##### Layer 3 — Understand

Go from building to understanding why things work. You can now reason about systems, not just use them.

Computer Science fundamentals, Data Science, SQL advanced, Python properly, JavaScript properly, software architecture, data engineering.

AI Play: Understanding how models work, fine-tuning concepts, production AI systems

Hardware Play: Raspberry Pi advanced projects, connecting hardware to AI software layer

##### Layer 4 — Root Knowledge

The foundation everything else sits on. Most people never come here — it separates engineers from scientists.

Math (linear algebra, probability, calculus), Electrical Engineering, Advanced Computer Science, genuine AI understanding at the model level.

AI Play: How neural networks actually work, training from scratch, AI research literacy

Hardware Play: Electronics fundamentals, circuit design, custom hardware

