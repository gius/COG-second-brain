---
name: people
description: "Evidence-based profiles of the people you work with - append observations from meetings, notes and messages, and read back what is known before a conversation"
metadata:
  roles: all
  integrations: none
  keywords: people,person,profile,who is,what do I know about,team member,colleague,crm,brief me on
  display-name: COG People
---

# COG People Skill

## Purpose
Keep a profile per person built only from evidence already in the vault. Answers "what do I know about X before I talk to them" without re-reading every meeting note.

Never a substitute for talking to people. The profile records observed working patterns, not conclusions about character.

## Storage
- One file per person: `05-knowledge/people/<firstname>-<lastname>.md`, lowercase, hyphenated
- Create from `06-templates/people-profile-template.md` on first write
- Two layers: **Compiled Truth** (current, rewritable) and **Timeline** (append-only, newest last)
- Conventions and design principles: `05-knowledge/people/README.md`

## Modes

| Mode | Trigger | What happens |
|---|---|---|
| `update` | "note that X …", or invoked by another skill after a meeting | Append observations, escalate the tier if warranted |
| `show` | "what do I know about X", "brief me on X" | Read the profile, report Compiled Truth plus anything unresolved |
| `list` | "who am I tracking" | List profiles with tier and last-updated date |

## Mode: update

1. Resolve the name to a file. On a near-match (`jan-novak` vs `jan-novack`), ask before creating a second file.
2. For each observation, capture the **source note it came from**. An observation with no vault source is not written - ask the user to braindump it first, or record it as their statement with the conversation as the source.
3. Append to `## Timeline` under a `### YYYY-MM-DD` heading. Never rewrite an existing entry.
4. Update **Compiled Truth** only where the new evidence changes the current picture. Contradiction with an existing line moves that line to `### Open Threads`, it does not silently overwrite it.
5. Report which profiles changed and how many observations landed.

### Citation format
Every line in both layers carries:

```
[Source: [[path/to/source-note]] | YYYY-MM-DD | confidence: high|medium|low]
```

`high` = directly stated in a source note. `medium` = consistent pattern across 2+ sources. `low` = single weak signal, keep it in Open Threads.

### Tiers
Profiles grow with evidence. Do not fill sections that the evidence cannot support.

| Tier | Threshold | Sections filled |
|---|---|---|
| 3 - stub | 1 mention | Name, role, one-line context |
| 2 - moderate | 3+ mentions | + Executive Snapshot, Working Style, Strengths |
| 1 - full | 8+ mentions, or a direct meeting | All sections including Collaboration Notes |

## What never goes in
- Personal or private life details, health, family, anything the person did not share in a work context
- Negative judgment, gossip, speculation about motive
- Performance verdicts, or anything you would not show the person themselves
- Compensation, hiring or exit discussions

The test is literal: if showing the profile to its subject would be awkward, the line is wrong. Rewrite it as the observation it came from, or drop it.

## Mode: show
Read the profile and report Compiled Truth first, then Open Threads. Name the sources. Say plainly when a section is empty rather than inferring one - "no working-style evidence yet" is the correct answer at Tier 3.

## Delegation
Never. Every mode is a small number of file reads and one append.

## Relationship to other skills
- `/meeting-transcript` - the main feeder. After writing a meeting note, it offers to append the people observations it found.
- `/braindump` - a braindump that discusses a colleague is a valid source; the braindump file is the citation.
- `/knowledge-consolidation` - reads profiles as evidence, never rewrites them.
