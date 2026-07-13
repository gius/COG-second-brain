---
name: task-triage
description: >
  Triage overdue and due-today tasks from the Obsidian Tasks plugin — classify each as done, superseded,
  cancelled, untracked, postponed, or needs-user with evidence from the vault, apply edits in a single
  commit, and accumulate reusable rules so the same judgment isn't asked twice. Use whenever the user
  says "triage tasks", "task review", "what's overdue", "clear my tasks", "clean up TASKS.md", or mentions
  overdue/stale tasks piling up — even when they don't explicitly name this skill.
metadata:
  roles: all
  keywords: tasks,task triage,overdue,obsidian tasks,due today,task review,task cleanup,stale tasks,TASKS.md,task hygiene
  display-name: COG Task Triage
---

# COG Task Triage Skill

## Purpose
Clear the backlog in `00-inbox/TASKS.md` without making the user answer the same judgment questions every run. Each pass classifies every overdue/due-today task with vault evidence, batches the auto-classifiable ones for one-keystroke approval, and grows a rulebook that silently handles routine cases on future runs. Review friction goes down over time; human judgment is preserved where it matters (subjective decisions, external execution).

## When to Invoke
- User says: "triage tasks", "task triage", "task review", "what's overdue", "clear my tasks", "clean up TASKS.md", "help me deal with my tasks"
- User is about to open `00-inbox/TASKS.md` and mentions wanting to clear it
- During a weekly check-in if overdue task count is climbing

## Agent Mode Awareness
Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:
- `agent_mode: team` (default for this skill's design) — delegate classification to **specialist-tier** sub-agents, one per provenance bucket. See [step 5](#5-dispatch-classification-agents-specialist-tier).
- `agent_mode: solo` — handle classification inline in the main conversation. No delegation.

Solo mode is acceptable for small runs (<10 tasks) but loses the context-isolation benefit of sub-agents for larger runs.

## Pre-Flight Check

### 1. Obsidian CLI availability
Read `.agents/skills/obsidian/SKILL.md` §1 to classify CLI status (`ok` / `disabled` / `app-not-running` / `runtime-blocked`). This skill depends on `obsidian tasks todo format=json verbose`.

| Status | Action |
|---|---|
| `ok` | Run the command. |
| `runtime-blocked` | **Do NOT silently grep-fall-back.** Surface the diagnosis per obsidian §1 Step 4 and wait for user direction — direct fallback misses Tasks-plugin metadata and produces false-zero results. |
| `disabled` / `app-not-running` | Fall back to grep with explicit path: `rg -n -g "*.md" '- \[ \] .*📅' .`. Warn user fallback is less precise. |

### 2. Profile and rulebook
- Read `00-inbox/MY-PROFILE.md` for active projects (used to weight project-scoped tasks).
- Read `.cog/task-triage/rules.md` — **the live rulebook**. If it doesn't exist, copy the skill's bundled `references/rules.md` to that path first, then read it.
- Every rule's hit count starts at zero for this run; it's incremented when an agent cites the rule in its classification.

**The live rulebook lives at `.cog/task-triage/rules.md`, never in `references/`.** The skill directory is regenerated wholesale by `cog-sync.sh` — accumulated rules written into `references/rules.md` are silently destroyed on the next sync. `references/rules.md` is a read-only seed for fresh installs.

### 3. Scope
- Default scope: **overdue + due-today**. This matches the first two sections of `00-inbox/TASKS.md`.
- Scope overrides from the user's prompt:
  - "all open" / "everything" → include upcoming + nodate buckets too
  - "this week" → add due within +7 days
  - "overdue only" → drop due-today

## Process Flow

### 1. Pull tasks via Obsidian CLI

Stage inside the project (sub-agents can't read outside it; never use `$TEMP` / `/tmp`):

```bash
RUN_DIR=".cog/task-triage/runs/$(date +%Y-%m-%d)"
mkdir -p "$RUN_DIR"
obsidian tasks todo format=json verbose > "$RUN_DIR/cog-tasks.json"
```

Records: `{status, text, file, line}`. `text` includes `- [ ]` and any `📅 YYYY-MM-DD`.

### 2. Bucket and cluster
Run `scripts/bucket_and_cluster.py` from project root. Defaults: reads `<RUN_DIR>/cog-tasks.json`, writes `cluster_*.json` to same dir. Buckets by `overdue / today / future / nodate`, clusters by source folder.

**Preprocessing — collapse within-file duplicates.** Before handing a cluster to an agent, within each single file (most often a weekly-checkin), merge task pairs that appear in both a "Next Steps" and a "Carry Forward" section into one logical task. These are structural duplicates of the same intent — the user writes them twice because the checkin template has two sections that happen to overlap. Classify the pair as a single unit (usually both supersede to the same newer task). The agent still sees both `file:line` entries so the render can apply the same edit to each occurrence.

Cluster mapping:

| Cluster | Source folder pattern |
|---|---|
| `weekly_checkins` | `01-daily/checkins/` |
| `project_overviews` | `04-projects/*/PROJECT-OVERVIEW.md` |
| `daily_briefs` | `01-daily/briefs/` |
| `consolidations` | `05-knowledge/consolidated/` |
| `booklets` | `05-knowledge/booklets/` |
| `braindumps` | `*/braindumps/` |
| `other` | anything else — triaged inline in main context |

The script writes per-cluster JSON files to `<RUN_DIR>/cluster_<NAME>.json` and prints a summary. See [`scripts/bucket_and_cluster.py`](scripts/bucket_and_cluster.py) for the implementation.

Folder-based clustering is deliberate: a cluster gives each agent a coherent narrative (all weekly-checkins cross-reference each other; all booklets follow the same "evaluate-and-forget" pattern) which tightens the evidence trail.

### 3. Present scope to user

**Do NOT dispatch agents in this step.** Print only:

```
Triaging N tasks (X overdue, Y due today) across M clusters.
Rules loaded: 7. Will dispatch {K} agents after scope confirmation.
```

Then **wait** for user confirmation or scope adjustment before §5. (Earlier wording "Dispatching {M} agents…" caused premature double-dispatch — every cluster got classified twice.)

### 4. Classification taxonomy (shared by rules and agents)

| Class | Edit shape when applied | When to choose |
|---|---|---|
| `done` | `- [x] text 📅 date ✅ today` | Evidence that the work already happened (git log, new artifact, project state change) |
| `superseded` | `- text 📅 date → [[newer-file]]` (no `[ ]`) | Equivalent/updated task exists in a newer file; link to it |
| `cancelled` | `- [-] text 📅 date` | User committed to it, then decided against — preserves audit trail via Obsidian Tasks plugin's cancelled status |
| `untrack` | `- text 📅 date` (no `[ ]`, line stays as prose) | Idea worth keeping, task tracking not worth it — AI-generated suggestion never warranted commitment |
| `delete` | line removed entirely | Genuine noise or exact duplicate — rare; **always ask user first** |
| `postpone` | `- [ ] text 📅 <new-date>` | Still valid, original date unrealistic — agent must propose a specific new date with reasoning |
| `needs-user` | unchanged; agent frames a tight question | No vault evidence either way; requires external confirmation |

Why six "not-done" states? Because different task origins warrant different audit trails. See [`references/edit-shapes.md`](references/edit-shapes.md) for before/after examples of each edit.

### 4a. Provenance rule (cancel vs untrack)

When classifying "drop this task", the choice between `cancelled` and `untrack` is determined by **where the task was born**:

| Source folder | Provenance | Drop → |
|---|---|---|
| `01-daily/checkins/` | User-curated (weekly reflection) | **cancelled** |
| `04-projects/*/PROJECT-OVERVIEW.md` | User-curated | **cancelled** |
| `01-daily/briefs/` | AI-generated (daily-brief skill) | **untrack** |
| `05-knowledge/booklets/` | AI-generated (scout/url-dump) | **untrack** |
| `05-knowledge/consolidated/` | AI-generated (vault-health/consolidation) | **untrack** |
| `*/braindumps/` | AI-extracted from thought capture | **untrack** |
| Anywhere else | Default: untrack; ask user if unsure | — |

The split matters because user-curated tasks were deliberate commitments — marking them `[-]` cancelled records a real decision-change event. AI-generated tasks are suggestions; untracking quietly is appropriate because the commitment never really existed.

### 5. Dispatch classification agents (specialist tier)

**Model tier is non-negotiable: specialist.** Per the tier→model mapping in your project's agent guide. Not worker (cross-references multiple files exceeds single-source scope); not architect (bounded pattern-matching with evidence, not open-ended reasoning).

#### Fan-out rules (apply in order)

1. **Inline-classify if cluster_size ≤ 5.** Don't spawn an agent. Main context handles the cluster directly using the rulebook + Read/Grep on the cited files. Saves ~40K context overhead per cluster.
2. **Group by provenance, not by folder.** Merge clusters into at most **two** agent payloads:
   - **`user_curated_agent`** — `weekly_checkins` + `project_overviews` + `other` (drop → `cancelled`)
   - **`ai_generated_agent`** — `daily_briefs` + `booklets` + `consolidations` + `braindumps` (drop → `untrack`)
3. **Split a provenance bucket only if its task count > 40.** Splitting at smaller sizes wastes the agent overhead vs. just letting one agent process more tasks.

Materialize the payloads deterministically: `python scripts/split_payloads.py <RUN_DIR>`. It encodes rules 2-3 — merges `cluster_*.json` into provenance buckets, splits any bucket >40 into balanced `payload_<provenance>[_n].json` (same-file tasks kept together), and writes `payload_manifest.json`. Inline-handle (rule 1) any payload ≤5 yourself; don't spawn for it. See [`scripts/split_payloads.py`](scripts/split_payloads.py).

Provenance grouping is more robust than folder grouping: adding a new vault folder type doesn't add an agent, and the taxonomy already splits cleanly by provenance (§4a).

Each agent receives:

1. Task list = its `payload_<provenance>[_n].json` from split_payloads. Inline the JSON if ≤25 tasks (~4KB); else pass the project-relative path `.cog/task-triage/runs/<YYYY-MM-DD>/payload_<provenance>[_n].json`.
2. Full live rulebook (`.cog/task-triage/rules.md`) inline. Cite rule IDs.
3. Taxonomy (§4) + provenance rule (§4a).
4. Every non-`needs-user` classification cites file/line/commit.
5. **DO NOT EDIT** — main context applies edits.
6. Output: one YAML block per task with `classification`, `rule_id` (or `agent-classified`), `evidence`, `suggested_action`, `confidence`.
7. ≤1000 words per cluster.
8. Sandbox: Read/Grep/Glob over project root only. Don't probe `AppData\Local\Temp` or `/tmp`.

Also instruct each agent to end with a `CANDIDATE_RULES:` block listing 1-3 generalizable rules discovered during triage. These feed step 10.

### 6. Consolidate and render

Merge agent outputs in main context. Produce a **single message** in this exact shape:

```
## Triage YYYY-MM-DD — N tasks (X overdue, Y due today)

Rules fired this run:
  RULE-01 newer-doc-supersedes (13)
  RULE-03 schedule-by-recurrence (1)
  RULE-04 ai-task-no-follow-up (6)
  RULE-05 external-execution (4)
  RULE-06 pipeline-step-1-unstarted (5)
  RULE-07 primary-sources-absorbed (2)
  [no rule matched] 7 → agent-classified

### done (4)
 # | file:line                            | text                       | edit                  | evidence
 1 | 01-daily/checkins/wc-2026-04-11.md:232 | Codex hybrid workflow      | [x] ✅ (rule:RULE-05)  | subscription 04-22
 ...

### superseded (11) ...
### cancelled (0) ...
### untrack (7) ...
### postpone (9) ...

### needs-user (7)
 Q1 (01-daily/.../wc-2026-04-11.md:128) TravelNet V1 closed out? [done / open / drop]
 Q2 ...
```

Key rendering rules:
- Every row's `edit` column cites either `rule:RULE-NN` or `agent` so the user can audit what drove the classification.
- Each `needs-user` question offers 2-4 canned options so the user can answer with short codes (`Q1: done`, `Q3: drop`).
- Rule-fired counts appear at the top — retired rules that never fire should eventually be pruned from `.cog/task-triage/rules.md`.

### 6a. HTML review page (default when > 10 tasks)

Chat review works, but it degrades once the run is large: many rows, several postpone dates to pick, several `needs-user` questions to answer in one message. Above ~10 tasks, render an interactive review page instead.

Write the consolidated classifications to `<RUN_DIR>/proposals.json` — one record per task:

```json
{"file": "01-daily/checkins/wc-2026-06-20.md", "line": 232,
 "text": "Wire up Codex hybrid workflow", "due": "2026-06-27", "bucket": "overdue",
 "provenance": "user_curated",
 "proposal": "done",
 "rule": "RULE-05",
 "evidence": "subscription active since 06-22; commit 7464541",
 "target": "wc-2026-07-04",
 "date": "2026-07-27",
 "question": "Is the InTour export optimization shipped, or still open?"}
```

`provenance` is `user_curated` | `ai_generated` (§4a) — it decides whether the page's **Drop** resolves to `cancelled` or `untrack`. `proposal` is one of the §4 classes plus `keep` (leave the task open, no edit). `target` / `date` / `question` are only needed for `superseded` / `postpone` / `needs-user`.

Then:

```bash
python .agents/skills/task-triage/scripts/render_review.py "$RUN_DIR"
start "$RUN_DIR/review.html"   # Windows; `open` on macOS
```

The page groups rows by proposed classification, **pre-selects each row's radio with the agent's proposal**, and shows the rule badge + evidence that drove it. The user only touches exceptions, then clicks **Copy decisions** and pastes the JSON back into chat. Filters (`changed only` / `needs me`) let them jump straight to the rows that matter.

The page never edits the vault — it emits a decisions array in exactly the shape §8 wants. Keep the §6 text summary as well; the page is a review surface, not a replacement for telling the user what you found.

### 7. Await user response

If the review page was used, the response is a pasted decisions JSON array — write it straight to `<RUN_DIR>/decisions.json` and go to §8. Any task absent from the array was left as *still todo* (or unanswered) and gets no edit; say so in the close-out.

Otherwise accept any of:
- `ok` / `approve all` — apply every auto-classified edit as proposed.
- `ok except N, M` (with inline reasons) — apply all except those numbered rows; the reasons feed rule generalization in step 9.
- Per-row instructions — `Q1: done`, `row 3: actually drop`, `row 12: postpone to 05-15` — the user can amend, confirm, or reclassify any row inline.
- Answers to the numbered questions — route each answered question to a classification.

Review is conversational (or page-driven). Don't write a staged review doc or other artifact — the user's model is: see findings, tell me what to do per row, I learn, we're done.

### 8. Apply edits (main context)

Write the approved classifications to `<RUN_DIR>/decisions.json` — a list of `{file, line, action, [date], [target]}` using full vault-relative paths (several files share the name `PROJECT-OVERVIEW.md`). Then run `python scripts/apply_edits.py <RUN_DIR>/decisions.json`. It transforms each cited line per the §4 edit shapes, prints every before/after, and skips (never writes) any line that isn't an open task — a stale line number is reported, not mis-edited. See [`scripts/apply_edits.py`](scripts/apply_edits.py).

For a few edits the `Edit` tool with exact-line matching is fine; reach for the script once a run exceeds ~15 edits or spans many files.

All edits land in **one git commit** per run — this is the non-negotiable revert escape hatch. Commit message format:

```
Task triage YYYY-MM-DD — N edits via M rules
```

Per `memory/feedback_git_workflow.md`, the **user** runs the git commands. Provide the commit command at the end of the run; don't run `git commit` directly.

### 9. Rule generalization

After applying edits, for each **user-corrected exception** and each **answered needs-user question**, ask the user once:

When the review page was used, the exceptions are the rows whose returned action differs from the `proposal` you wrote into `proposals.json` — diff the two files to find them. Ask the user *why* for each before proposing a rule; the page captures the what, not the reasoning.

> "Generalize this into a rule? [y/n/skip]"

If yes, append a new `### RULE-NN` block to `.cog/task-triage/rules.md` (**not** `references/rules.md` — see §2) with:

```markdown
### RULE-NN — <short name>
- **Fires when**: <condition, generalized from the specific case>
- **Action**: <classification + edit shape>
- **Added**: YYYY-MM-DD (origin: run YYYY-MM-DD, exception #K / question QK)
- **Hits**: 0
```

Also review the `CANDIDATE_RULES` blocks returned by each agent — if any look generalizable and don't duplicate an existing rule, offer them to the user the same way.

**Why ask per exception rather than auto-learning**: rules have compound effects. A wrong rule becomes invisible automation that corrupts future runs. Explicit user sign-off is cheap (one keystroke) and prevents silent drift.

### 10. Close out

Emit:
1. The git commit command for the user to run.
2. A summary line: "N edits applied, M rules used (K new rules added), Q questions surfaced."
3. Any `needs-user` questions the user didn't answer yet — flag them as still-open.

## Non-negotiables

1. **Every auto-edit cites its rule or `agent`.** No silent classifications.
2. **Every rule surfaces its hit count per run.** Dead rules should be visible candidates for pruning.
2a. **Accumulated rules are written to `.cog/task-triage/rules.md` only.** Writing them into the skill's `references/` means `cog-sync.sh` deletes them on the next run.
3. **All edits land in one commit per run.** One `git revert` restores prior state.
4. **Never delete without explicit user ack.** Default is untrack/cancel.
5. **Sub-agents use specialist tier.** Not worker, not architect.
6. **Stage inputs inside project root.** Use `.cog/task-triage/runs/<date>/`. Sub-agent sandbox denies `$TEMP` / `%TEMP%` / `/tmp`; Bash-on-Windows also mistranslates them.
7. **Cap fan-out at 2 agents (one per provenance bucket).** Inline-handle clusters ≤5 tasks. Wait for user confirmation in §3 before dispatching anything in §5.

## Bundled resources

- [`references/rules.md`](references/rules.md) — **Seed** rulebook (11 rules, hit counts 0). Copied to `.cog/task-triage/rules.md` on first run; the live rulebook accumulates there and is never overwritten by sync.
- [`scripts/bucket_and_cluster.py`](scripts/bucket_and_cluster.py) — Deterministic parser + clusterer (UTF-8 safe).
- [`scripts/split_payloads.py`](scripts/split_payloads.py) — Merges clusters into provenance buckets and splits >40-task buckets into balanced agent payloads (§5).
- [`scripts/render_review.py`](scripts/render_review.py) — Renders `proposals.json` into a self-contained `review.html` with pre-selected radios; emits a `decisions.json` array (§6a).
- [`scripts/apply_edits.py`](scripts/apply_edits.py) — Applies a `decisions.json` to vault files in place with before/after output and open-task safety checks (§8).
- [`references/edit-shapes.md`](references/edit-shapes.md) — Before/after examples for each classification's edit shape.
