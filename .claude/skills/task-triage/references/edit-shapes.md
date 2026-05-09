# Edit Shapes — Before / After

Each classification from `SKILL.md` §4 has a specific edit shape. Use the exact patterns here when applying edits with the `Edit` tool. Match the full original line (including `- [ ]` prefix, any text, and any 📅 date) to avoid touching nearby text.

## done

Complete a task that already happened.

**Before:**
```
- [ ] Explore Codex/Gemini/Copilot hybrid dev workflow 📅 2026-04-22
```

**After** (today is 2026-04-24):
```
- [x] Explore Codex/Gemini/Copilot hybrid dev workflow 📅 2026-04-22 ✅ 2026-04-24
```

The `✅ YYYY-MM-DD` is the Obsidian Tasks plugin's completion-date marker. Always use today's date from the system clock.

## superseded

Preserve audit trail via a wiki-link. Remove the `[ ]` so the Tasks plugin no longer indexes it.

**Before:**
```
- [ ] Continue UX design work 📅 2026-04-24
```

**After:**
```
- Continue UX design work 📅 2026-04-24 → [[weekly-checkin-2026-04-22#TravelNet v2]]
```

Wiki-link precision: prefer `[[file#section]]` or `[[file#^block-id]]` when the target has a specific section. If the replacement task lives at a particular line, a plain `[[file]]` link is acceptable.

## cancelled

User committed to this task, then decided not to do it. Use the Obsidian Tasks plugin's cancelled marker `[-]`. Origin folder: `01-daily/checkins/` or `04-projects/*/PROJECT-OVERVIEW.md`.

**Before:**
```
- [ ] Finish MR automation PoCs 📅 2026-04-23
```

**After:**
```
- [-] Finish MR automation PoCs 📅 2026-04-23
```

You may optionally append a reason and a cancelled-date marker:
```
- [-] Finish MR automation PoCs 📅 2026-04-23 ❌ 2026-04-24 (handed over as part of eMan exit)
```

The `❌ YYYY-MM-DD` cancelled-date marker is supported by the Obsidian Tasks plugin and behaves analogously to `✅`.

## untrack

Idea worth keeping, task tracking not worth it. Remove the `- [ ]` prefix; the line stays as prose. Origin folder: AI-generated (`01-daily/briefs/`, `05-knowledge/booklets/`, `05-knowledge/consolidated/`, `*/braindumps/`).

**Before:**
```
- [ ] Install graphify and run on a small test project 📅 2026-04-22
```

**After** (simplest — just unmark):
```
- Install graphify and run on a small test project 📅 2026-04-22
```

**After** (more explicit about the decision):
```
- Install graphify and run on a small test project (not pursued, 2026-04-24)
```

Choose the explicit form when a reader might later wonder "did we ever do this?" — usually not needed for booklet items.

## delete

Rare. Only for genuine noise or exact duplicates. The skill must always ask for explicit user confirmation before applying. The edit removes the entire line from the file.

No before/after — the line is gone.

## postpone

Keep the task, rewrite its due date. Always include a specific new date; never relative phrasing.

**Before:**
```
- [ ] Select top 2-3 wireframe directions + nav patterns 📅 2026-04-24
```

**After:**
```
- [ ] Select top 2-3 wireframe directions + nav patterns 📅 2026-05-09
```

## needs-user

No edit. The task stays exactly as it is. The skill surfaces the question to the user in the render and waits for an answer, then applies whichever shape the answer selects.

## Applying edits with the Edit tool

Use `Edit` with `old_string` = the full original task line (as returned by the Obsidian Tasks CLI in the `text` field) and `new_string` = the transformed line.

Example call:
```
Edit(
  file_path = "D:/private/COG-second-brain/01-daily/checkins/weekly-checkin-2026-04-11.md",
  old_string = "- [ ] Explore Codex/Gemini/Copilot hybrid dev workflow 📅 2026-04-22",
  new_string = "- [x] Explore Codex/Gemini/Copilot hybrid dev workflow 📅 2026-04-22 ✅ 2026-04-24",
)
```

One Edit call per task. Do not batch edits across files — if a file has multiple classified tasks, still call Edit once per task (the CLI's file+line gives you the exact match).

Why not a bulk script: visibility. Each Edit surfaces in the transcript so the user can see the actual change. Bulk scripts hide errors.
