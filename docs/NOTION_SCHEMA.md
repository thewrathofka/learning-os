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

Content order: callout → quote → paragraph → "How This Works" heading + callout →
"The Databases" heading followed by all 13 databases embedded inline (in creation
order) → "Relationship Map" heading + ASCII diagram → "Workflow" heading + numbered
steps → "Things Worth Knowing" heading + bulleted notes.

