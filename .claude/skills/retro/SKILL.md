---
name: retro
description: Retrospective over recent coding-agent sessions in one repo - finds where agents searched too long, repeated mistakes, wasted tool calls or lacked information, and proposes changes to the agent's environment (navigation pointers, automated checks, review rules, steering files, tooling), most severe first. Proposes only.
disable-model-invocation: true
metadata:
  roles: engineer,engineering-lead
  keywords: retro,retrospective,agent sessions,session review,navigability,why was the agent slow,improve agent environment
  display-name: COG Retro
---

# COG Retro Skill

Adapted from `retro` in [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/retro) (MIT, Copyright (c) 2026 Matt Pocock), upstream commit `a7d038f`. COG additions: multi-session input, a bundled log condenser, the opened-but-unused and dead-end questions, vault filing.

## Purpose
Change the agent's **environment**, not the code: the file an agent needed twenty calls to find, the mistake a check could have caught, the rule nobody reads. Every proposal is a pointer, a check, a standard or a tool. Nothing changes until the user picks a candidate.

## When to Invoke
- `/retro`, "retro my last sessions", "why are agents slow in this repo"
- Default cadence: every 2 weeks per active code repo; after any session that felt slow or went wrong

## Input
- **Target repo** - the user names it; default = current working directory.
- **Sessions** - default = the 10 most recent sessions in that repo with at least one tool call. "This session" = the current one.

Locate the logs for the agent runtime in use:
- **Claude Code** - JSONL files in the runtime's config dir under `projects/<repo path with every separator and colon replaced by ->/`, newest by modification time.
- **Other runtimes** - ask the user where session logs live. None kept: retro the current session only.

## Process

### 1. Condense the logs
Raw logs are megabytes of JSON. Condense first:

```bash
uv run python -I <skill dir>/scripts/condense_sessions.py .cog/retro/<repo-slug>/ <log>...
```

One timeline per session: user prompts, every tool call with a short input, tool errors, and a header with call counts and search calls before the first edit. Supports Claude Code JSONL.

**No shell (fallback):** read each log and keep only user messages, `tool_use` names with their main input, and `tool_result` entries flagged `is_error`.

### 2. Read the repo's own guardrails
Before proposing a check, read what exists: steering files (`AGENTS.md`, `CLAUDE.md`), build/lint/test scripts, CI workflows, pre-commit hooks, `.gitattributes`. An existing check that is unwired or broken is the finding, not a reinvention. A repo with no guardrail (no hook and no CI running lint/type/test) is itself a finding.

### 3. Find candidates
Read every timeline in full. Look in these categories; skip empty ones.

- **Navigation** - many calls to find a file or fact; hidden dependencies between files. Fix: a navigation pointer.
- **Automated checks** - a mistake lint, types, tests or a filesystem check could have caught.
- **Coding standards** - a mistake the reviewer missed. Mechanical violation (fixed pattern, banned API, import shape, file location) = deterministic check, never a written rule. Judgement call = a standards doc the reviewer reads.
- **Steering files** - text in `AGENTS.md`/`CLAUDE.md` (repo or global) that belongs in standards, checks, docs or skills. These files load into every session and every sub-agent; keep them to navigation pointers.
- **Tool economy** - expensive or repeated calls: whole-file dumps of huge files, guessed `sed -n` ranges, repeated loops over a CLI, outputs too large for context.
- **No-ops** - steering text that changes no behaviour.
- **Information access** - information the agent lacked: logs, device or service state, third-party docs, where a tool's source lives.

Answer two more questions:
- **Opened but never used** - files read or listed that fed no later edit or answer. Stale docs and misleading names show up here.
- **Dead ends** - for every finding, the wrong turns that justify it. Without them the retro is one more document for the next agent to wander through.

### 4. Verify
- Every finding cites session id + timestamp or the quoted tool calls.
- Every claim about the repo is checked by opening the file. Say "checked" only for what was opened.
- One session = weak signal. State how many sessions show the pattern.
- Do not fill categories to look complete.

### 5. Report
Ordered by severity: cost (calls or tokens) x frequency, or risk of wrong output first. Per finding:
- Title that says what to change
- Category
- Evidence and dead ends
- Proposed change with its target file
- Expected effect, marked as an estimate
- Owner, when the fix belongs elsewhere (a shared tool, an upstream skill)

Close with the opened-but-unused list and what could not be determined.

### 6. File it
- Target repo has a vault project (`04-projects/**/PROJECT-OVERVIEW.md` naming the repo): offer to save the report as `research/agent-retro-YYYY-MM-DD.md` there and add picked fixes to the project backlog.
- Never edit the target repo without the user picking the candidate.
- Delete `.cog/retro/<repo-slug>/` timelines after filing; they hold full prompts.

## Agent Mode
- **team:** one `worker` sub-agent reads the timelines and the repo and returns findings; brief it with steps 2-5 verbatim. The lead spot-checks the top findings in the repo before reporting.
- **solo:** do it directly.

## Implementation vs review
The implementation agent carries the most context pressure: exploration, code, debugging. The review agent gets a diff and has the least. Coding standards therefore go to review, not to implementation steering.
