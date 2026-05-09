# Task Triage Rules

Accumulated rules applied during `/task-triage`. Each rule has an ID, a behavioral trigger, a resulting classification, and a hit count that grows with every run.

**How these are used:** the skill loads this file at the start of each run and passes it to every classification sub-agent. Agents cite the `RULE-NN` ID when a rule fires. Main context renders the per-run hit counts in the report header.

**Rules describe behaviors, not locations.** Folder-scoping lives in one place — the provenance rule in `SKILL.md §4a` (which governs cancel-vs-untrack). Rules below reference "AI-generated" or "user-curated" when provenance matters, and defer to §4a for the folder-to-provenance mapping. This keeps the rulebook portable across vault reshuffles.

**How to tighten, retire, or add:**
- Edit a rule's text directly to narrow its trigger.
- To retire: delete the rule block (hit counts stay in past triage commits for forensics).
- New rules are appended by the skill after user sign-off on an exception or answered question (see SKILL.md §9).

**Format per rule:**
```
### RULE-NN — <short name>
- **Fires when**: <semantic condition, specific enough to avoid false positives>
- **Action**: <classification + optional note on edit specifics>
- **Added**: YYYY-MM-DD (origin)
- **Hits**: <running total across runs>
```

---

### RULE-01 — Superseded by newer document
- **Fires when**: a newer document (newer weekly-checkin, newer brief, newer research doc, newer PROJECT-OVERVIEW revision, or a memory entry) contains content that replaces the task's intent. Any of the following is sufficient:
  - Equivalent task text, possibly reworded
  - Narrative reframe — the newer doc explains *why* the task no longer applies (e.g. "throwaway test" retired because "QPCR is the proving ground now", "follow-up appt" escalated to "operation prep")
  - A broader or completed version of the task absorbs it
  - A documented strategy pivot ("Phase 10 swaps to X") makes the task target an abandoned path
- **Action**: superseded; link to the newer `file:line`. Use the section header or block anchor if the target is specific within the newer doc.
- **Added**: 2026-04-24 (consolidates pilot R01/R03/R07/R11)
- **Hits**: 13

### RULE-02 — Evergreen / maintenance items don't get due dates
- **Fires when**: task text includes explicit evergreen markers — "ongoing", "evergreen", "maintenance", "continuous", "keep doing X" — signalling a standing intention rather than a completable unit of work
- **Action**: untrack (remove `[ ]`, keep as standing note). Applies regardless of provenance.
- **Added**: 2026-04-24 (pilot R04)
- **Hits**: 1

### RULE-03 — Schedule established by ≥3 recurrences
- **Fires when**: the task is to establish/start a schedule for a recurring activity (e.g. "run this audit monthly", "do a weekly X") AND that activity has occurred ≥3 times since the task was created
- **Action**: done; the cadence is established de facto even without a formal schedule config
- **Added**: 2026-04-24 (pilot R05)
- **Hits**: 1

### RULE-04 — AI-generated action with no vault follow-up
- **Fires when**: the task is AI-generated (see SKILL.md §4a for provenance) AND no vault note references the topic within the source-type's freshness window. Freshness thresholds:

  | Source type | Window |
  |---|---|
  | Daily brief / team brief | 10 days |
  | Booklet / braindump | 14 days |
  | Consolidation / vault-health audit | 21 days |

  "References the topic" means a grep for the tool/author/action noun turns up content outside the source file itself — a braindump, a research doc, a PROJECT-OVERVIEW change, anything that shows the idea was taken up.

- **Action**: untrack. Aspirational saves and speculative brief items without follow-through rarely convert; untracking clears the surface without deleting the idea.
- **Added**: 2026-04-24 (consolidates pilot R06/R09)
- **Hits**: 6

### RULE-05 — External-execution → needs-user
- **Fires when**: the task requires action outside the vault's visibility — e.g., runtime patches on external repos, CLI installs outside `.claude/skills/`, sharing an article with a team, external service config changes
- **Action**: needs-user. The vault cannot verify external execution; route to a question with options `[done / still-todo / drop]`.
- **Added**: 2026-04-24 (pilot R08)
- **Hits**: 4

### RULE-06 — Pipeline with step 1 unstarted → postpone chain
- **Fires when**: 3+ tasks in the same file form a sequential pipeline (step 1 → step 2 → …) AND step 1's artifact doesn't exist yet
- **Action**: postpone the whole chain from step 1's evidence alone. Proposed new dates should be spaced across the pipeline (e.g. +14d, +17d, +20d…) rather than all stamped the same. Don't investigate each step individually — step 1 being blocked is sufficient signal.
- **Added**: 2026-04-24 (pilot R10)
- **Hits**: 5

### RULE-07 — "Read/study X" done when primary sources absorbed
- **Fires when**: the task is to read/study a specific work by an author (book, repo, paper) AND the author's primary sources (canonical chapters, foundational refs) are cited in a related research or design doc within 30 days
- **Action**: done; the learning intent was achieved through primary sources rather than the specific secondary work
- **Added**: 2026-04-24 (pilot R12)
- **Hits**: 2
