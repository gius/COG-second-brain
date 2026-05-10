
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
- Read `references/rules.md` — the accumulated rulebook. Every rule's hit count starts at zero for this run; it's incremented when an agent cites the rule in its classification.

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

Provenance grouping is more robust than folder grouping: adding a new vault folder type doesn't add an agent, and the taxonomy already splits cleanly by provenance (§4a).

Each agent receives:

1. Task list. Inline if ≤25 tasks (~4KB); else pass project-relative path `.cog/task-triage/runs/<YYYY-MM-DD>/cluster_<NAME>.json`.
2. Full `references/rules.md` inline. Cite rule IDs.
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
- Rule-fired counts appear at the top — retired rules that never fire should eventually be pruned from `references/rules.md`.

### 7. Await user response

Accept any of:
- `ok` / `approve all` — apply every auto-classified edit as proposed.
- `ok except N, M` (with inline reasons) — apply all except those numbered rows; the reasons feed rule generalization in step 9.
- Per-row instructions — `Q1: done`, `row 3: actually drop`, `row 12: postpone to 05-15` — the user can amend, confirm, or reclassify any row inline.
- Answers to the numbered questions — route each answered question to a classification.

Review is conversational. Don't write a staged review doc or other artifact — the user's model is: see findings, tell me what to do per row, I learn, we're done.

### 8. Apply edits (main context)

For each approved classification, edit the source file with the `Edit` tool using the original line text as the match. Exact-line matching prevents accidental edits to nearby text.

All edits land in **one git commit** per run — this is the non-negotiable revert escape hatch. Commit message format:

```
Task triage YYYY-MM-DD — N edits via M rules
```

Per `memory/feedback_git_workflow.md`, the **user** runs the git commands. Provide the commit command at the end of the run; don't run `git commit` directly.

### 9. Rule generalization

After applying edits, for each **user-corrected exception** and each **answered needs-user question**, ask the user once:

> "Generalize this into a rule? [y/n/skip]"

If yes, append a new `### RULE-NN` block to `references/rules.md` with:

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
3. **All edits land in one commit per run.** One `git revert` restores prior state.
4. **Never delete without explicit user ack.** Default is untrack/cancel.
5. **Sub-agents use specialist tier.** Not worker, not architect.
6. **Stage inputs inside project root.** Use `.cog/task-triage/runs/<date>/`. Sub-agent sandbox denies `$TEMP` / `%TEMP%` / `/tmp`; Bash-on-Windows also mistranslates them.
7. **Cap fan-out at 2 agents (one per provenance bucket).** Inline-handle clusters ≤5 tasks. Wait for user confirmation in §3 before dispatching anything in §5.

## Bundled resources

- [`references/rules.md`](references/rules.md) — The accumulated rulebook. Seeded with 12 rules from the 2026-04-24 pilot run.
- [`scripts/bucket_and_cluster.py`](scripts/bucket_and_cluster.py) — Deterministic parser + clusterer (UTF-8 safe).
- [`references/edit-shapes.md`](references/edit-shapes.md) — Before/after examples for each classification's edit shape.
