# Topic Hubs

A topic hub is one undated living page per topic: a tool category, a model family, a technique. It compiles every tool, article and research note the vault holds on that topic into one comparable view. Booklets (`05-knowledge/booklets/`) stay the per-link store; hubs are where a topic is read and decided.

File: `05-knowledge/topics/<topic-slug>.md`. Writers: `/url-dump`, `/scout` and `/auto-research` keep rows current at save time; `/knowledge-consolidation` creates hubs from clusters, splits long ones and lists them in `05-knowledge/_index.md`.

## Page shape

```markdown
---
type: "topic-hub"
title: "<Topic>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags: ["topic-hub", "<topic-tags>"]
related_projects: ["<project-slug>"]
---

# <Topic>

<Overview: what the topic is, how to choose between entries, the limits every entry shares. Link the detail notes that explain the topic itself.>

## Entries
| Entry | What it is | Licence, runtime | Status | Checked | Detail |
|---|---|---|---|---|---|

## Evidence
<Per entry without a detail note: numbers and claims, each with a verbatim quote and its source URL.>

## Where it fits
<Project or life-area tie-ins, each naming the open problem it answers.>

## Dropped
- <Entry> - <reason> (YYYY-MM-DD)

## Open contradictions
- <claim> - <new evidence> (YYYY-MM-DD)
```

- **Status:** `adopted`, `candidate` or `watching`. An entry ruled out or abandoned leaves the table for one line in `## Dropped`.
- **Checked** is the date the row was verified against its source.
- **Project candidates tables outrank hubs.** When a project truth doc tracks the topic's candidates, the hub links that table and keeps only the entries the project does not track.
- Write `## Where it fits`, `## Dropped` and `## Open contradictions` only when they have content.

## Detail notes

The hub row is the summary; a detail note holds the depth. An entry gets one when its evidence passes about 15 lines, or when a project doc links the entry directly. Otherwise its evidence stays inline under `## Evidence`.

- A detail note is a booklet entry or a research note. It carries `feeds: "[[<hub>]]"` from write time.
- Once the hub row carries the note's findings, the note also gets `consolidated_in: "[[<hub>]]"` and `consolidated_date`. `feeds` without `consolidated_in` = pending.
- A new source that contradicts a row adds one line to `## Open contradictions`; the next save or consolidation run that resolves it fixes the row and removes the line.

## Length budget

A hub over about 250 lines, or with more than 12 entries carrying inline evidence, is due for a split:

1. Move each dropped or abandoned entry to one line in `## Dropped`.
2. Move the inline evidence of the largest entries into detail notes with `feeds` and `consolidated_in`.
3. The hub keeps the overview, the table, and evidence only for entries still under the detail-note threshold.

## New hubs

A topic earns a hub when 3 or more booklet entries or research notes cover it, or when the user asks. Propose the topic name and slug to the user before creating the file; the name is theirs to set.
