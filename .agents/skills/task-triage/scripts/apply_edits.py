"""Apply task-triage classifications to vault files in place.

Reads a decisions JSON: list of {file, line, action, [date], [target]}.
Transforms the cited line per the COG task-triage edit shapes (SKILL.md §4):
  done       - [ ] X 📅 d   -> - [x] X 📅 d ✅ <today>
  cancelled  - [ ] X 📅 d   -> - [-] X 📅 d
  untrack    - [ ] X 📅 d   -> - X 📅 d            (checkbox removed, stays prose)
  superseded - [ ] X 📅 d   -> - X 📅 d → [[target]]
  postpone   - [ ] X 📅 d   -> - [ ] X 📅 <new>

Safety: verifies each line is an open task (or carries a 📅 date for postpone)
before editing; mismatches are reported and skipped, never written. Every change
is printed before/after so the run is auditable before the user commits.

Usage:  python apply_edits.py <decisions.json> [vault_root]
Vault root defaults to four levels up from the decisions file, matching the
runtime staging path .cog/task-triage/runs/<date>/decisions.json.
"""
import datetime
import io
import json
import os
import re
import sys
from collections import defaultdict

DONE_DATE = datetime.date.today().isoformat()
OPEN_TASK = re.compile(r'^(\s*)- \[ \] (.*)$')
DATE = re.compile(r'📅\s*\d{4}-\d{2}-\d{2}')


def transform(line, d):
    nl = '\n' if line.endswith('\n') else ''
    body = line.rstrip('\n')
    action = d['action']
    if action == 'postpone':
        if not DATE.search(body):
            return None, "no 📅 date to postpone"
        return DATE.sub(f"📅 {d['date']}", body, count=1) + nl, None
    m = OPEN_TASK.match(body)
    if not m:
        return None, f"not an open task: {body[:55]!r}"
    indent, rest = m.group(1), m.group(2)
    if action == 'done':
        return f"{indent}- [x] {rest} ✅ {DONE_DATE}{nl}", None
    if action == 'cancelled':
        return f"{indent}- [-] {rest}{nl}", None
    if action == 'untrack':
        return f"{indent}- {rest}{nl}", None
    if action == 'superseded':
        return f"{indent}- {rest} → [[{d['target']}]]{nl}", None
    return None, f"unknown action {action!r}"


def main(decisions_path, vault_root):
    decisions = json.load(open(decisions_path, encoding='utf-8'))
    byfile = defaultdict(list)
    for d in decisions:
        byfile[d['file']].append(d)

    applied, errors = 0, []
    for rel, ds in sorted(byfile.items()):
        path = os.path.join(vault_root, rel)
        with io.open(path, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        changed = False
        for d in ds:
            i = d['line'] - 1
            if not (0 <= i < len(lines)):
                errors.append((rel, d['line'], 'line out of range'))
                continue
            new, err = transform(lines[i], d)
            if err:
                errors.append((rel, d['line'], err))
                continue
            print(f"{rel}:{d['line']} [{d['action']}]")
            print(f"  - {lines[i].rstrip()}")
            print(f"  + {new.rstrip()}")
            lines[i] = new
            applied += 1
            changed = True
        if changed:
            with io.open(path, 'w', encoding='utf-8') as fh:
                fh.writelines(lines)

    print(f"\n=== APPLIED {applied} edits across {len(byfile)} files; {len(errors)} errors ===")
    for e in errors:
        print("ERROR", e)
    return errors


if __name__ == '__main__':
    decisions = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else os.path.abspath(
        os.path.join(os.path.dirname(decisions), '..', '..', '..', '..'))
    sys.exit(1 if main(decisions, root) else 0)
