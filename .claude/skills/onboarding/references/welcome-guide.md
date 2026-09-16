# Onboarding: WELCOME-TO-COG template

The guide step 8 of `SKILL.md` generates. Read this file when you reach that step.

Generate: `00-inbox/WELCOME-TO-COG.md` in the profile `language`. Per-user content only; the vault tour, the self-building files, Focus, knowledge and people are in `00-inbox/HOW-TO-USE-COG.md`, generated just before this file - link it, do not repeat it. The Focus anchor `#Focus (optional)` uses that heading as generated in `language`. Drop any section the user's answers do not support; never leave a placeholder.

```markdown
---
type: guide
created: YYYY-MM-DD
tags: [welcome, getting-started, cog]
---

# Welcome, [Name]

Your COG is set up. [[HOW-TO-USE-COG]] explains the vault: where files go, the dashboards that build themselves, the optional Focus list, and how knowledge compounds. This page holds what is yours.

## Your settings

- [[MY-PROFILE]] - name, role, projects, how you work
- [[MY-INTERESTS]] - topics and sources for your briefs
- [[MY-INTEGRATIONS]] - services COG may use
- [[03-professional/COMPETITIVE-WATCHLIST|COMPETITIVE-WATCHLIST]] - companies and people you track *(only if named)*

Edit them any time; skills read them when they run:
- daily brief reads [[MY-INTERESTS]] for topics and sources
- braindump offers the projects listed in [[MY-PROFILE]] as filing targets
- braindump and meeting notes flag anyone on the [[03-professional/COMPETITIVE-WATCHLIST|watchlist]]
- every skill checks [[MY-INTEGRATIONS]] before touching an outside service

## Skills for a [Role Display Name]

[If a role pack matched: the pack's skills in its order, one line each: **skill** - the pack's role-specific reason.]
[If none matched:]
- **daily-brief** - verified news in your interest areas, last 7 days
- **braindump** - capture a thought, classified into your domains and projects
- **url-dump** - save a link with extracted insights
- **weekly-checkin** - patterns across the week
- **knowledge-consolidation** - frameworks from scattered notes

## Your projects

[One line per project: [[04-projects/<slug>/PROJECT-OVERVIEW|Name]] - one phrase from the profile. Braindumps offer these as filing targets.]

## Integrations

[Active: list. Disabled: list. If none: "None yet; add them in [[MY-INTEGRATIONS]]."]

## First week

- Morning: "daily brief" - covers [interest areas].
- During the day: "capture this: ..." - filed into [domains].
- End of week: "reflect on my week".
- When the overdue list in [[TASKS]] grows: "triage tasks".
- If a few streams matter more than the rest: create `FOCUS.md` from the template ([[HOW-TO-USE-COG#Focus (optional)|how]]).

*Delete this page when you no longer need it; [[HOW-TO-USE-COG]] stays.*
```
