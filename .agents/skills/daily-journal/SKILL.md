---
name: daily-journal
description: "Passive work journal the agent writes for you - appends short entries after meaningful work so the record exists on days you would never sit down to write one, plus an optional guided reflection"
metadata:
  roles: all
  integrations: none
  keywords: daily journal,journal,log this,add to journal,what did I do today,reflect on today,reflect on yesterday,work log
  display-name: COG Daily Journal
---

# COG Daily Journal Skill

## Purpose
Keep an automatic, passive record of workdays without asking the user to write one. The agent is the author; the log accrues in the background as work happens.

This is not `/braindump` and not `/weekly-checkin`. Braindump captures *thinking* the user supplies. Weekly-checkin is a reflection the user drives. Here the user supplies nothing - the entries are a byproduct of work already done.

## Two modes

| Mode | Trigger | What happens |
|---|---|---|
| `log` (default) | Implicit, after meaningful work in any session | Append one entry to today's journal |
| `reflect` | `/daily-journal reflect`, "reflect on today/yesterday" | Read the day plus recent days, run a guided reflection |

## Storage
- One file per day: `01-daily/journal/YYYY-MM-DD.md`
- Get today's date from the system, never from memory or inference
- Create the file from the template on the first entry of the day
- **Append only.** Never rewrite an earlier entry. Newest goes at the bottom of `## Log`

## Mode: log

### When to log
This trigger applies in **any session**, not only when the skill is invoked by name. After finishing a meaningful unit of work, append one entry. Meaningful means it would matter to future-you, or it shows how the day was spent:

- Shipped or committed something, published a note or report, filed or moved tracker issues
- Made a decision, changed direction, or hit a notable blocker
- Produced a deliverable file (spec, plan, analysis, report)
- A substantive research or synthesis session that produced an artifact

### When not to log
- Trivial reads, one-line lookups, mid-task scratch work
- This journal's own writes
- Anything the user asked to keep out
- Work in a session the user has muted the journal for

When in doubt, one concise line beats none. Do not interrupt the flow to announce logging - append and carry on.

### Entry format
Append under `## Log`:

```markdown
### HH:MM - <short title of what got done>
- **Focus:** <the thread or project this served>
- **Did:** <1-3 concrete bullets, past tense>
- **Artifacts:** <files, PRs, links touched, or "-">
- **Signal:** <optional: decision made, blocker hit, energy if the user mentioned it - omit otherwise>
```

24-hour local time. Record what actually happened or what the user explicitly said. Never invent next steps, and never editorialise about how the work went.

### Day file template
```markdown
---
type: "journal"
domain: "personal"
date: YYYY-MM-DD
status: "open"
tags: [journal, daily]
---

# Journal - YYYY-MM-DD

## Log

## Reflection
```

## Mode: reflect

1. Read today's file plus the previous 3 journal days. If today has no entries, say so and offer to reflect on the last day that does.
2. Draft the reflection from the log itself - what the day was actually spent on, what moved, what stalled. Do not open with questions the log already answers.
3. Ask at most 3 delta questions: what the log could not see (why a direction changed, whether a blocker is still live, what tomorrow's first move is).
4. Write the result under `## Reflection` in the day file and set `status: reflected`.
5. Surface any task-shaped outcome in [Obsidian Tasks emoji format](https://publish.obsidian.md/tasks/Reference/Task+Formats/Tasks+Emoji+Format): `- [ ] Action 📅 YYYY-MM-DD`.

## Muting
If the user says to stop logging - for a session, a project, or entirely - honour it for the rest of the session and tell them how to make it permanent (remove the skill, or add the exclusion to `00-inbox/MY-PROFILE.md`). Never log a session the user asked to keep private.

## Delegation
Never. Logging is a single append and reflection is a conversation - both cost less than a sub-agent spawn.

## Relationship to other skills
- `/braindump` - user-authored thinking. The journal records work; braindump records thought.
- `/weekly-checkin` - reads journal days as evidence for the week's cross-domain scan, so the check-in starts from what happened rather than from recall.
- `/knowledge-consolidation` - journal entries are raw log, not compiled knowledge. Consolidation reads them; it does not treat them as a source of frameworks.
