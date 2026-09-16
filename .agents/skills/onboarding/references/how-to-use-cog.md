# Onboarding: HOW-TO-USE-COG template

The vault tour step 8 of `SKILL.md` generates, before the welcome guide. Read this file when you reach that step.

Generate: `00-inbox/HOW-TO-USE-COG.md`, in the profile `language` (English users get it as written). Keep every section, table, callout and link; translate prose only. Frontmatter as below with today's date.

```markdown
---
type: guide
created: YYYY-MM-DD
language: <ISO 639-1 code>
tags: [cog, config, getting-started]
---

# How to use COG

> [!info] Written by onboarding from COG's template
> Say "regenerate the vault guide" after a COG update to refresh it. Your own settings live in [[MY-PROFILE]], [[MY-INTERESTS]] and [[MY-INTEGRATIONS]]; the per-user welcome is [[WELCOME-TO-COG]].

## Talking to COG

Say what you want in plain words; the assistant picks the skill. "Capture this", "what's new in my areas", "save this link", "what's overdue", "reflect on my week", "brief me on <person>". The full list with trigger phrases is in `AGENTS.md` § Available Skills. Tasks anywhere in the vault use one format: `- [ ] Do the thing 📅 YYYY-MM-DD`.

## Where things go

| Folder | Holds |
|---|---|
| `00-inbox/` | Your settings, the dashboards, this guide |
| `01-daily/` | `briefs/` morning intelligence, `checkins/` weekly reflections, `journal/` the work log the assistant writes for you |
| `02-personal/` | Personal braindumps and notes, private domain |
| `03-professional/` | Work braindumps, strategy, leadership, skills; `COMPETITIVE-WATCHLIST.md` |
| `04-projects/<project>/` | One folder per project, `PROJECT-OVERVIEW.md` at its root |
| `05-knowledge/` | What COG compiles from your notes: `_index.md` (entry point), `consolidated/` frameworks, `patterns/`, `booklets/` saved links, `people/` profiles |
| `06-templates/` | Note templates |

Inside a project folder the name decides placement, not the topic. Undated files (`PROJECT-OVERVIEW.md`, `build-plan.md`) are living documents at the root, updated in place. Dated files (`<slug>-YYYY-MM-DD.md`) are point-in-time and sit in a subfolder: `braindumps/` raw capture, `research/` findings gathered as input, `planning/` pre-build inputs, `reports/` finished output for an audience, `archive/` superseded.

## Files that build themselves

- **[[COG-DASHBOARD]]** - counts and tables of projects, open braindumps, saved links, frameworks. Dataview queries; fills as the vault grows.
- **[[TASKS]]** - every `- [ ]` from every note, grouped into Overdue, Due Today, This Week. Write tasks in the note they belong to, never here; "triage tasks" clears the overdue pile with evidence from the vault.
- **`01-daily/journal/YYYY-MM-DD.md`** - the assistant appends a short entry after real work (something shipped, decided, blocked). Say "log this" to force one, "reflect on today" for a guided review, or tell it to stop journaling.

## Focus (optional)

`TASKS.md` holds every checkbox. `00-inbox/FOCUS.md` holds only the few streams you push every day, hand-picked and hand-ordered, one link per line to where the detail lives. The file is off until you create it, from [[focus-template|the template]]. Once it exists the assistant reads it at session start: "what should I push today" answers from the linked files' open items, and naming a stream gets you the work an agent can run on it in parallel. Keep it short; when a stream is done, delete the line.

## Knowledge that compounds

Braindumps and check-ins are raw material. "Consolidate knowledge" turns recurring insights into frameworks under `05-knowledge/consolidated/` and lists them in `05-knowledge/_index.md`, which every later analysis consults first. "Vault health" runs the lightweight audit instead. When new evidence contradicts a framework, the index gets a line under Open Contradictions; consolidation resolves it.

## People

"What do I know about <name>" reads `05-knowledge/people/<firstname>-<lastname>.md`; meetings and braindumps offer to add observations, never silently. Every line carries its vault source; only what you would show the person is written.

## Your settings

Edit the three files in `00-inbox/` directly; skills read them at run time. Re-run onboarding to add projects or change your role. `language` in [[MY-PROFILE]] sets the language the assistant talks and writes in; "change my language to <language>" switches it and rewrites this page and [[WELCOME-TO-COG]]. Integrations: active ones are used, disabled ones are never mentioned, unknown ones get one question.
```
