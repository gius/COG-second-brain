---
name: learn-my-voice
description: "Learn the user's personal writing rules from the edits they make to agent drafts and keep them as a reviewable list in 00-inbox/MY-VOICE.md, which the my-voice skill applies. Use when the user says 'learn from my edits', 'I fixed your draft', 'here is what I actually sent', 'add a voice rule', or 'show my voice profile', or hands back a draft they changed."
metadata:
  roles: all
  integrations: none
  keywords: learn my voice,learn from my edits,I edited your draft,what I actually sent,add a voice rule,voice profile,my writing style
  display-name: COG Learn My Voice
---

# Learn my voice

The profile `00-inbox/MY-VOICE.md` holds writing rules inferred from the user's edits to agent drafts. The `my-voice` skill applies them on top of its general rules. Rules are descriptions, not fine-tuning: the user can read, change and delete each one. Rules are grouped by context (language + audience), because the same person writes a management report and a chat reply differently.

This skill owns the profile format: `references/voice-template.md` defines it, and `my-voice` only reads sections by heading.

Method follows PRELUDE/CIPHER (Gao et al. 2024, arXiv:2404.15269): infer a preference description from each edit, store it with its context, retrieve by closest context when writing.

## Modes

| User says | Mode |
|---|---|
| "learn from my edits", "I edited X", hands back a changed draft or the version they sent | **learn** |
| "add a rule: ...", "never write X" | **add** |
| "show my voice", "what have you learned" | **show** |

## Files

| Path | Holds |
|---|---|
| `00-inbox/MY-VOICE.md` | The profile. Created from `references/voice-template.md` on the first approved rule |
| `.cog/learn-my-voice/drafts/<flat-path>` | The agent's last handed-over version of a vault file. `<flat-path>` = vault-relative path with `/` replaced by `__` |
| `.cog/learn-my-voice/pending/<YYYYMMDD-HHMM>-<slug>.before.md` + `.after.md` | Edit pairs waiting for **learn**: captured before an agent overwrote the user's edits, or pasted in chat |
| `.cog/learn-my-voice/proposals.md` | Proposed rules waiting for approval. Any session can finish the approval |
| `.cog/learn-my-voice/runs/` | Scratch for one learn run: git baselines, script output |

Everything learned about the user stays in these files. Never write rules, examples or pairs into the skill folder or any framework file: the skill ships to other people.

Snapshot capture is ambient and described in `AGENTS.md` § Voice.

## Learn

### 1. Collect pairs

Take every source that applies, in this order:

1. All pairs in `.cog/learn-my-voice/pending/`.
2. A file the user names. Baseline:
   - its snapshot in `.cog/learn-my-voice/drafts/`, if one exists and differs from the file;
   - else git: show `git log --format='%h %ad %s' --date=short -5 -- <file>` and ask which commit holds the agent's draft. Uncommitted changes against `HEAD` count only if the user confirms nobody else (no agent) edited the file since.
3. Text pasted in chat: the agent's draft and the version the user sent (email, message, comment). Save both to `pending/` first, so the pair outlives the session.

`proposals.md` exists: finish that approval (step 5) before collecting new pairs. No pairs and no proposals: say so and stop.

### 2. List changed paragraphs

With a shell: `uv run <skill-dir>/scripts/edit_pairs.py <before> <after>` per pair. Write git baselines to `.cog/learn-my-voice/runs/` first. The script drops frontmatter and `%% comments %%`, ignores table padding and re-wrapping, and prints numbered pairs: rewritten (with % of words changed), added, removed.

Without a shell: read both versions, walk paragraphs in order, list each paragraph whose words differ, plus added and removed paragraphs. Ignore whitespace and table padding.

### 3. Sort each pair

- **voice** - same facts, different words, order, length, emphasis, structure, or noise cut for the reader. Includes structural moves: a summary added on top, a section moved, a heading renamed.
- **content** - a fact corrected, added or removed; scope change; data update. Skip.
- **mixed** - extract the voice part only.
- **not the user's** - looks agent-written (a large added block with sources, a pattern the user never writes). Do not learn from it; list it in the batch under "Skipped as maybe not yours".

Unsure between voice and content: put it in the batch as a question, not as a rule.

### 4. Infer rules

Per voice change, one instruction a writer could follow without seeing the example. Name the mechanism, not a label: "Name the reader's next step at the end of each risk", not "action-oriented".

- Context = language + audience of the document (e.g. "Czech - reports for management"). Use `All writing` only when the same rule shows up in two contexts.
- Same as an existing rule: raise its `seen` count, update `last`, swap in the example if it is shorter and clearer. Keep at most two examples.
- Contradicts an existing rule: propose replacing it; show both.
- Matches a line in `## Rejected`: drop silently.

### 5. Ask for approval

One batch, numbered:

```
1. NEW  [English - reports for management] Use the word the reader uses, not the engineering term.
        `the broker port is internal` -> `access to the broker is internal`
2. +1   V-04 Name who approves, not just that approval is missing.
        `without a managed plan` -> `without a plan approved by the client`
Skipped as maybe not yours: pairs 11, 23 (added table with registry sources)
Questions: pair 31 - voice or a fact fix?
```

Write the batch to `.cog/learn-my-voice/proposals.md` with the source of each pair, then show it. User answers `all`, `1,3`, `none`, or rewords a rule. Never write unapproved rules. Proposals not approved count as declined.

### 6. Write the profile

- Create `00-inbox/MY-VOICE.md` from `references/voice-template.md` if missing.
- Approved rules go to their context section (create `## <language> - <audience>` when new), next free `V-NN` id across the file.
- Declined proposals: one line under `## Rejected`.
- Section over 20 rules: propose merging near-duplicates or dropping the lowest `seen` count, oldest `last` first. A long list gets ignored, and every rule applied everywhere turns into a tic.
- Update `updated:` in frontmatter.
- Delete `proposals.md`, processed pairs from `pending/`, and the run files from `runs/`.

### 7. Verify

Re-read `00-inbox/MY-VOICE.md`. Every approved id is present with the right count and date, no declined rule was written, `proposals.md` is gone, `pending/` holds no processed pair. Report: rules added, rules strengthened, pairs skipped. Mismatch: say so plainly.

## Add

User states a rule directly. Ask for the context only if it is not obvious. Write it with `seen 0x` and no example, then verify as in Learn step 7. User-stated rules are never merged away or dropped without asking.

## Show

Print each section's rules, one line each, highest `seen` first. No examples unless asked.

## Guardrails

- Learn only from changes the user made. Agent edits interleaved with user edits pollute the profile; when in doubt, skip the pair and say so.
- Never invent a rule from a single content fix.
- The profile is the user's file: never reword a rule they edited by hand, never re-add a deleted or rejected rule.
- Rules describe how to write, never facts about a project or customer.

## Bundled resources

- [`scripts/edit_pairs.py`](scripts/edit_pairs.py) - paragraph-level diff of a draft and its edited version, no dependencies.
- [`references/voice-template.md`](references/voice-template.md) - empty profile, copied to `00-inbox/MY-VOICE.md` on first write.
