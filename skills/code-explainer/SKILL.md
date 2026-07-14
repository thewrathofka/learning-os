---
name: code-explainer
description: Explain existing code through inline teaching comments, a README with a real-world analogy, and a Mermaid diagram matched to the code's shape (flowchart, sequence, class, state, or tree). Use when the user has existing code they want annotated and diagrammed rather than built from scratch. Make sure to use this skill whenever the user asks to "explain this code", "break this down", "walk me through this", "what does this do", "annotate this", "diagram this", "visualize this", or "teach me what Claude just made" — even if they don't explicitly say "explain". Also triggers on pasted code blocks without other context, since the most likely user intent is wanting it explained. Produces a session folder with commented code, original, and README, all saved to the Code Reader NotebookLM.
---

# Code Explainer

Explain a piece of code through inline teaching comments, a written README with a real-world analogy, and a visual Mermaid diagram — all saved to the study vault and pushed to the "Code Reader" NotebookLM.

## Workflow

1. **Identify the code to explain.**
   - If the user points at the file path, read it with the Read tool.
   - If the user pasted code in the chat, use that.
   - If the user says "this code" / "what Claude just made" / "what you just made", use the most recent code block in the conversation.
   - Ask the user to clarify only if the target is genuinely ambiguous.

2. **Read the code carefully before writing anything.**
   - Identify the language.
   - Identify the paradigm: pure logic, object-oriented, component tree (HTML/React), event/callback flow, state machine, data pipeline.
   - Decide which diagram type fits — use the mapping in the "Diagram type selection" section below.

3. **Create the session folder** at `$LEARNING_OS_CODE_READER_DIR/<YYYY-MM-DD>-<short-filename>/` (source `~/.learning-os/config.env` first; if it's missing, tell the user to run `/learning-os-setup` and fall back to `~/code-reader/<date>-<slug>/` for this session).
   - Use today's date and a short lowercase-hyphenated slug of the filename (e.g. `2026-04-20-login-form`).

4. **Write three files into that folder:**
   - `original.<ext>` — a pristine copy of the code, untouched. This is the reference version.
   - `<filename>-commented.<ext>` — a copy with teaching comments added (see "Commenting style" below).
   - `README.md` — the longer explanation (see "README structure" below).

5. **Push the session to NotebookLM.**
   - Notebook: `$NOTEBOOK_CODE_EXPLAINER` (from `~/.learning-os/config.env`).
   - Upload all three files using the `notebooklm` CLI.

6. **Report back to the user:**
   - One sentence on where the files live.
   - The analogy headline.
   - A pointer: "open the README in Obsidian to see the diagram rendered."

## Diagram type selection

Pick the diagram type that matches the *shape* of the code. Don't mix multiple types in one diagram — pick the one that best answers the user's "what is this code?" question.

| If the code is about... | Use this diagram | Mermaid keyword |
|---|---|---|
| Branching logic, if/else, loops, algorithm steps | Flowchart | `flowchart LR` or `flowchart TD` |
| Who calls who, in what order (HTTP requests, event handlers, API calls) | Sequence diagram | `sequenceDiagram` |
| Classes, objects, inheritance, data models | Class diagram | `classDiagram` |
| HTML structure, React component nesting, folder layout | Tree (top-down flowchart) | `flowchart TD` |
| UI states, form validation stages, game states | State diagram | `stateDiagram-v2` |
| Data pipelines, ETL, transformations left-to-right | Flowchart (LR) | `flowchart LR` |

**Why this mapping exists:** each diagram type answers a different question. A flowchart answers "what path does execution take?" A sequence diagram answers "what happens in what order?" A class diagram answers "how are things related?" Using the wrong type makes the diagram misleading even when the syntax is valid.

**Default if unsure:** `flowchart LR` — covers most procedural code.

## Commenting style

Teaching comments are different from production comments. Production code comments answer "why does this exist?" for a fellow engineer. Teaching comments answer "what is this and why does it work this way?" for someone still building their mental model of the language.

**Write teaching comments that:**

- **Name the concept.** If the line uses `for`, say "for loop — repeats for each item in the list." Don't assume the name is obvious.
- **Explain the syntax on first appearance.** First time a decorator, arrow function, destructuring, or list comprehension appears: name what it's called so the user can look it up.
- **Flag what's language-specific vs. universal.** "In Python, indentation groups code — the 4 spaces here matter." "Arrow functions are JavaScript shorthand for `function(){}`."
- **Connect back to the analogy.** If the README compares the code to a restaurant kitchen, reference that inside comments: `# the waiter hands the order to the kitchen`.
- **Say "why", not just "what".** Bad: `# sets x to 5`. Good: `# x holds the current score — we start at 5 because the game gives each player 5 free tries`.

**Don't:**

- Comment every line — only where something new or surprising appears.
- Restate trivially obvious code (`x = 1  # assigns 1 to x` is noise).
- Use jargon without a short definition in the comment itself.

**Syntax by language:**

| Language | Single-line | Multi-line |
|---|---|---|
| Python | `# comment` | `"""triple quoted"""` |
| JavaScript | `// comment` | `/* comment */` |
| HTML | `<!-- comment -->` | same |
| CSS | `/* comment */` | same |

**Example transformation (Python):**

Original:

```python
users = [u for u in all_users if u.active]
```

Commented:

```python
# list comprehension — shorthand for building a list
# reads as: "for every u in all_users, keep it if u.active is True"
# this is the same as a for loop with an if inside, just compressed
users = [u for u in all_users if u.active]
```

## README structure

The `README.md` in each session folder is the long-form explanation. It should read like a short tutorial written for the user, not like technical documentation.

**Use this exact template:**

```markdown
# <Filename>: <Analogy Headline>

*<Date> · <language> · <short description of what the code does>*

## The analogy

<One paragraph comparing this code to something in the real world. Pick something the user would already understand — a kitchen, a post office, a library, a coffee shop, an assembly line. The analogy should map onto the structure of the code, not just vibe with it.>

## What the code actually does

<One short paragraph in plain language — no jargon. If jargon is unavoidable, define it in the same sentence.>

## Diagram

​```mermaid
<the Mermaid diagram — type chosen from the Diagram type selection table>
​```

## Walkthrough

<Line-group-by-line-group, not line-by-line. Group related lines, explain the group, reference the analogy. Keep each group to 2–4 sentences.>

1. **<First logical chunk>** — <what it does in the analogy + in the code>
2. **<Second logical chunk>** — <…>
3. **<…>**

## Concepts introduced

- **<Concept 1>** — <one-line definition>. See also: [[relevant note in study vault]] if one exists.
- **<Concept 2>** — <…>

## What to explore next

<2–3 suggestions for related code or topics. These should feel like "if you liked this, you'll like…" — not homework.>
```

**Template rules:**

- **The analogy headline is the single most important line** — it's what the user will remember. Make it specific. "Login form: a bouncer checking IDs at the door" is good. "Login form: how authentication works" is generic and useless.
- **Use an analogy the user would plausibly encounter in daily life.** Avoid metaphors that require explanation of the metaphor.
- **The Mermaid block uses three backticks + `mermaid`**, not four. Obsidian renders it automatically when the file is opened in the vault.
- **"Walkthrough" groups lines by purpose, not by sequence.** If setup, main logic, and cleanup are each 5 lines, that's three groups — not fifteen.
- **"Concepts introduced" links to the study vault when a matching note exists.** Use Obsidian's `[[wikilink]]` syntax. If no note exists, still name the concept — the user can create the note later.

**Why the template is rigid:** consistency across sessions makes the "Code Reader" NotebookLM far more useful. If every README has the same sections in the same order, you can ask the notebook "show me all the analogies I've seen for loops" or "what concepts have I covered from my JS coursework?" and it will actually work.
