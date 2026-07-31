"""Render a task-triage review page: proposals in, review.html out.

Input:  <RUN_DIR>/proposals.json - the consolidated agent classifications
        (SKILL.md §6), one record per task:

  {"file": "01-daily/checkins/wc-2026-06-20.md", "line": 232,
   "text": "Wire up Codex hybrid workflow", "due": "2026-06-27",
   "bucket": "overdue",                   # overdue|today|future|nodate
   "provenance": "user_curated",          # or "ai_generated" -> drop shape
   "proposal": "done",                    # done|superseded|cancelled|untrack|
                                          #   postpone|keep|needs-user
   "rule": "RULE-05",                     # or "agent"
   "evidence": "subscription active since 04-22",
   "target": "wc-2026-05-02",             # superseded only
   "date": "2026-07-20",                  # postpone only
   "question": "Is the Phase 1 rollout closed out?"}   # needs-user only

Output: <RUN_DIR>/review.html - self-contained, no network, dark theme.
        Radios come pre-selected with each proposal, so the user only touches
        exceptions. The page emits a decisions array that apply_edits.py eats
        as-is: {file, line, action, [date], [target]}.

The vault name (for obsidian:// deep links) is derived from the vault root,
four levels up from RUN_DIR; override with a second argument.

Usage:  python render_review.py <RUN_DIR> [vault_name]
"""
import datetime
import json
import os
import sys

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>COG Task Triage - review</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --row: #1c2129; --border: #30363d;
    --text: #c9d1d9; --dim: #8b949e; --accent: #58a6ff;
    --done: #3fb950; --postpone: #d29922; --drop: #f85149;
    --keep: #8b949e; --supersede: #a371f7; --ask: #f0883e;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 0 0 150px; background: var(--bg); color: var(--text);
    font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  header {
    position: sticky; top: 0; z-index: 10; background: var(--panel);
    border-bottom: 1px solid var(--border); padding: 12px 24px;
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  }
  h1 { font-size: 16px; margin: 0; font-weight: 600; }
  .sub { color: var(--dim); font-size: 13px; }
  .seg { display: flex; gap: 0; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
  .seg button {
    background: var(--row); color: var(--dim); border: 0; border-right: 1px solid var(--border);
    padding: 5px 11px; font-size: 12px; cursor: pointer;
  }
  .seg button:last-child { border-right: 0; }
  .seg button.on { color: var(--bg); background: var(--accent); font-weight: 600; }
  .seg-label { color: var(--dim); font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }
  .spacer { margin-left: auto; }
  main { padding: 20px 24px; max-width: 1400px; }
  section { margin-bottom: 22px; }
  .group-head {
    display: flex; align-items: baseline; gap: 10px; padding: 7px 0;
    border-bottom: 1px solid var(--border); margin-bottom: 8px;
  }
  .group-head h2 { font-size: 13.5px; margin: 0; font-weight: 600; }
  .group-head .path { color: var(--dim); font-size: 11.5px; font-family: ui-monospace, monospace; font-weight: 400; }
  .count { color: var(--dim); font-size: 12px; }
  .accept-all {
    margin-left: auto; background: none; border: 1px solid var(--border);
    color: var(--dim); border-radius: 6px; padding: 3px 9px; font-size: 11px; cursor: pointer;
  }
  .accept-all:hover { color: var(--text); border-color: var(--accent); }
  .row {
    display: grid; grid-template-columns: 34px 1fr 430px; gap: 12px;
    background: var(--row); border: 1px solid var(--border); border-left-width: 3px;
    border-radius: 8px; padding: 10px 12px; margin-bottom: 6px; align-items: start;
  }
  .row.changed { border-left-color: var(--accent); }
  .row.unresolved { border-left-color: var(--ask); }
  .idx { color: var(--dim); font-size: 12px; font-family: ui-monospace, monospace; padding-top: 3px; }
  .task { font-size: 13.5px; }
  .meta {
    color: var(--dim); font-size: 11.5px; margin-top: 3px;
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  }
  .meta a { color: var(--dim); text-decoration: none; border-bottom: 1px dotted var(--border); }
  .meta a:hover { color: var(--accent); border-bottom-color: var(--accent); }
  .obs { margin-left: 6px; text-decoration: none; font-size: 12px; opacity: .55; }
  .obs:hover { opacity: 1; }
  .overdue { color: var(--drop); }
  .evidence { color: var(--dim); font-size: 12px; margin-top: 4px; font-style: italic; }
  .question { color: var(--ask); font-size: 12.5px; margin-top: 4px; }
  .badge {
    display: inline-block; background: #21262d; border: 1px solid var(--border);
    border-radius: 4px; padding: 0 5px; font-size: 10.5px; color: var(--dim);
    font-family: ui-monospace, monospace; margin-left: 6px;
  }
  .choices { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .choices label {
    display: inline-flex; align-items: center; gap: 4px; cursor: pointer;
    border: 1px solid var(--border); border-radius: 6px; padding: 3px 8px;
    font-size: 12px; color: var(--dim); user-select: none;
  }
  .choices input { accent-color: var(--accent); margin: 0; }
  .choices label:has(input:checked) { color: var(--text); background: #21262d; }
  label.done:has(input:checked)      { border-color: var(--done); }
  label.postpone:has(input:checked)  { border-color: var(--postpone); }
  label.drop:has(input:checked)      { border-color: var(--drop); }
  label.keep:has(input:checked)      { border-color: var(--keep); }
  label.supersede:has(input:checked) { border-color: var(--supersede); }
  .extra { margin-top: 5px; display: none; }
  .extra.show { display: block; }
  .extra input {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    border-radius: 6px; padding: 3px 7px; font-size: 12px; width: 100%;
    font-family: ui-monospace, monospace;
  }
  footer {
    position: fixed; bottom: 0; left: 0; right: 0; background: var(--panel);
    border-top: 1px solid var(--border); padding: 12px 24px;
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  }
  .tally { display: flex; gap: 12px; font-size: 12.5px; flex-wrap: wrap; }
  .tally span b { font-weight: 600; }
  .actions { margin-left: auto; display: flex; gap: 8px; }
  .actions button {
    background: var(--accent); color: #0d1117; border: 0; border-radius: 6px;
    padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer;
  }
  .actions button.ghost { background: var(--row); color: var(--text); border: 1px solid var(--border); }
  .hint { color: var(--dim); font-size: 12px; width: 100%; }
  .warn { color: var(--ask); }
  .hidden { display: none !important; }
</style>
</head>
<body>
<header>
  <h1>Task triage</h1>
  <span class="sub" id="scope"></span>

  <span class="seg-label">group</span>
  <div class="seg" id="groupby">
    <button data-group="type" class="on">by type</button>
    <button data-group="due">by due date</button>
    <button data-group="folder">by folder</button>
  </div>

  <span class="seg-label spacer">show</span>
  <div class="seg" id="filters">
    <button data-filter="all" class="on">all</button>
    <button data-filter="changed">changed only</button>
    <button data-filter="unresolved">needs me</button>
  </div>
</header>

<main id="groups"></main>

<footer>
  <div class="tally" id="tally"></div>
  <div class="actions">
    <button class="ghost" id="download">Download JSON</button>
    <button id="copy">Copy decisions</button>
  </div>
  <div class="hint" id="hint">Radios are pre-set to what the agent proposed - change only what is wrong, then copy and paste back into Claude.</div>
</footer>

<script>
const PROPOSALS = __DATA__;
const VAULT = __VAULT__;
const TODAY = __TODAY__;

// Drop maps to a different edit shape depending on where the task was born
// (SKILL.md §4a): a user-curated commitment is cancelled, an AI suggestion is
// silently untracked. But rules like RULE-02/RULE-08/RULE-10 untrack regardless
// of provenance, so a drop the agent already proposed keeps the flavor the agent
// picked - re-deriving from provenance would silently overrule the rulebook.
// Provenance only decides rows the user moves into Drop themselves.
const dropAction = p => p.proposal === 'untrack' || p.proposal === 'cancelled'
  ? p.proposal
  : (p.provenance === 'ai_generated' ? 'untrack' : 'cancelled');
const CHOICES = ['done', 'postpone', 'drop', 'keep', 'supersede'];
const LABEL = { done: 'Done', postpone: 'Postpone', drop: 'Drop', keep: 'Still todo', supersede: 'Supersede' };
const labelFor = (t, c) => c === 'drop'
  ? `Drop (${dropAction(t) === 'untrack' ? 'untrack' : 'cancel'})`
  : LABEL[c];

const choiceOf = p => ({
  done: 'done', superseded: 'supersede', cancelled: 'drop', untrack: 'drop',
  postpone: 'postpone', keep: 'keep',
}[p.proposal] || '');

const state = PROPOSALS.map((p, i) => ({
  ...p, i,
  choice: choiceOf(p),
  date: p.date || nextWeek(),
  target: p.target || '',
}));

let groupBy = 'type';
let filter = 'all';

function nextWeek() {
  const d = new Date(Date.now() + 7 * 864e5);
  return d.toISOString().slice(0, 10);
}
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// Survive an accidental tab close mid-review: a long run is exactly the one
// worth resuming. Keyed by the task set, so a fresh triage run starts clean.
const KEY = 'cog-triage-' + state.map(t => t.file + t.line).join('|').length + '-' + state.length;
const save = () => localStorage.setItem(KEY, JSON.stringify(state.map(t => [t.choice, t.date, t.target])));
function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (!saved || saved.length !== state.length) return false;
    saved.forEach(([choice, date, target], i) => Object.assign(state[i], { choice, date, target }));
    return true;
  } catch { return false; }
}
function discard() { localStorage.removeItem(KEY); location.reload(); }

// ── grouping ───────────────────────────────────────────────────────────
const TYPE_ORDER = [
  ['needs-user', 'Needs your call'], ['done', 'Done'], ['superseded', 'Superseded'],
  ['cancelled', 'Drop (cancel)'], ['untrack', 'Drop (untrack)'], ['postpone', 'Postpone'],
  ['keep', 'Still todo'],
];
const DUE_ORDER = [
  ['overdue', 'Overdue'], ['today', 'Due today'], ['week', 'Due this week'],
  ['later', 'Due later'], ['nodate', 'No due date'],
];

function dueBucket(t) {
  if (!t.due) return 'nodate';
  if (t.due < TODAY) return 'overdue';
  if (t.due === TODAY) return 'today';
  const weekOut = new Date(Date.parse(TODAY) + 7 * 864e5).toISOString().slice(0, 10);
  return t.due <= weekOut ? 'week' : 'later';
}

function groups() {
  if (groupBy === 'type') {
    return TYPE_ORDER
      .map(([key, title]) => ({ key, title, rows: state.filter(t => (t.proposal || 'keep') === key) }))
      .filter(g => g.rows.length);
  }
  if (groupBy === 'due') {
    return DUE_ORDER
      .map(([key, title]) => ({ key, title, rows: state.filter(t => dueBucket(t) === key) }))
      .filter(g => g.rows.length);
  }
  // folder: one section per directory, ordered by path, indented by depth
  const byDir = new Map();
  state.forEach(t => {
    const dir = t.file.split('/').slice(0, -1).join('/') || '.';
    if (!byDir.has(dir)) byDir.set(dir, []);
    byDir.get(dir).push(t);
  });
  return [...byDir.keys()].sort().map(dir => {
    const parts = dir.split('/');
    return {
      key: dir,
      title: parts[parts.length - 1],
      path: parts.slice(0, -1).join('/'),
      depth: parts.length - 1,
      rows: byDir.get(dir).slice().sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line),
    };
  });
}

// ── render ─────────────────────────────────────────────────────────────
function obsidianHref(file) {
  return `obsidian://open?vault=${encodeURIComponent(VAULT)}&file=${encodeURIComponent(file.replace(/\.md$/, ''))}`;
}

// Supersede is not a free choice: it needs a target note that the agent found by
// grepping the vault. Hand-typing one here has no autocomplete and no existence
// check, and a typo writes a broken [[link]] into the vault. So it is offered
// only on rows where an agent proposed it - you can move off it, not invent it.
const choicesFor = t => choiceOf(t) === 'supersede'
  ? CHOICES : CHOICES.filter(c => c !== 'supersede');

function rowHtml(t) {
  const radios = choicesFor(t).map(c => `
    <label class="${c}">
      <input type="radio" name="r${t.i}" value="${c}" ${t.choice === c ? 'checked' : ''}
             onchange="setChoice(${t.i},'${c}')">${labelFor(t, c)}
    </label>`).join('');
  const overdue = t.due && t.due < TODAY;
  return `<div class="row" id="row${t.i}" data-i="${t.i}">
    <div class="idx">${t.i + 1}</div>
    <div>
      <div class="task">${esc(t.text)}</div>
      <div class="meta">${esc(t.file)}:${t.line}<a class="obs" href="${obsidianHref(t.file)}" title="Open in Obsidian">&#x2197;</a>
        ${t.due ? `<span class="${overdue ? 'overdue' : ''}"> &middot; due ${t.due}</span>` : ' &middot; no date'}
        <span class="badge">${esc(t.rule || 'agent')}</span></div>
      ${t.evidence ? `<div class="evidence">${esc(t.evidence)}</div>` : ''}
      ${t.question ? `<div class="question">? ${esc(t.question)}</div>` : ''}
    </div>
    <div>
      <div class="choices">${radios}</div>
      <div class="extra" id="extra${t.i}"></div>
    </div>
  </div>`;
}

function render() {
  const overdueCount = state.filter(t => dueBucket(t) === 'overdue').length;
  document.getElementById('scope').textContent = `${state.length} tasks - ${overdueCount} overdue`;
  document.getElementById('groups').innerHTML = groups().map(g => {
    const head = groupBy === 'folder'
      ? `<h2 style="padding-left:${g.depth * 14}px">${g.path ? `<span class="path">${esc(g.path)}/</span>` : ''}${esc(g.title)}</h2>`
      : `<h2>${esc(g.title)}</h2>`;
    return `<section data-group="${esc(g.key)}">
      <div class="group-head">
        ${head}<span class="count">${g.rows.length}</span>
        <button class="accept-all" onclick="resetGroup('${esc(g.key)}')">reset to proposal</button>
      </div>
      ${g.rows.map(rowHtml).join('')}
    </section>`;
  }).join('');
  state.forEach(t => syncRow(t.i));
  applyFilter();
  updateTally();
}

function setChoice(i, c) { state[i].choice = c; syncRow(i); updateTally(); }

function syncRow(i) {
  const t = state[i];
  const row = document.getElementById('row' + i);
  const extra = document.getElementById('extra' + i);
  if (!row) return;
  if (t.choice === 'postpone') {
    extra.className = 'extra show';
    extra.innerHTML = `<input type="date" value="${t.date}" onchange="state[${i}].date=this.value;updateTally()">`;
  } else if (t.choice === 'supersede') {
    extra.className = 'extra show';
    extra.innerHTML = `<input type="text" placeholder="target note (wiki-link, no brackets)" value="${esc(t.target)}"
      oninput="state[${i}].target=this.value;updateTally()">`;
  } else {
    extra.className = 'extra';
    extra.innerHTML = '';
  }
  row.classList.toggle('changed', !!t.choice && t.choice !== choiceOf(t));
  row.classList.toggle('unresolved', !t.choice);
}

function resetGroup(key) {
  const g = groups().find(x => String(x.key) === key);
  if (!g) return;
  g.rows.forEach(t => {
    t.choice = choiceOf(t);
    const el = document.querySelector(`input[name=r${t.i}][value="${t.choice}"]`);
    if (el) el.checked = true;
    else document.querySelectorAll(`input[name=r${t.i}]`).forEach(r => r.checked = false);
    syncRow(t.i);
  });
  updateTally();
}

// ── filter ─────────────────────────────────────────────────────────────
// A filter hides rows. It does NOT silently shrink the decisions payload:
// the Copy button always states exactly how many decisions it will emit, and
// warns when a filter is holding some back. Reviewing all 200 rows, then
// filtering to double-check, then copying must never drop the other 180.
// `visible` is a snapshot of what is on screen, recomputed only when the filter
// or grouping changes - never lazily at copy time. Answering a row under the
// "needs me" filter must not make that row silently drop out of the payload
// while it is still displayed. What you see is what you copy.
let visible = new Set();
const matchesFilter = t => filter === 'all'
  || (filter === 'changed' && !!t.choice && t.choice !== choiceOf(t))
  || (filter === 'unresolved' && !t.choice);
const isVisible = t => visible.has(t.i);

function applyFilter() {
  visible = new Set(state.filter(matchesFilter).map(t => t.i));
  state.forEach(t => {
    const row = document.getElementById('row' + t.i);
    if (row) row.classList.toggle('hidden', !isVisible(t));
  });
  document.querySelectorAll('section').forEach(s =>
    s.classList.toggle('hidden', !s.querySelector('.row:not(.hidden)')));
}

// ── output ─────────────────────────────────────────────────────────────
function decisions(scope) {
  return state
    .filter(t => t.choice && t.choice !== 'keep' && (scope === 'all' || isVisible(t)))
    .map(t => {
      const d = { file: t.file, line: t.line };
      if (t.choice === 'done') d.action = 'done';
      else if (t.choice === 'drop') d.action = dropAction(t);
      else if (t.choice === 'postpone') { d.action = 'postpone'; d.date = t.date; }
      else if (t.choice === 'supersede') { d.action = 'superseded'; d.target = t.target; }
      return d;
    });
}

function updateTally() {
  const c = {};
  state.forEach(t => { const k = t.choice || 'unresolved'; c[k] = (c[k] || 0) + 1; });
  const order = ['done', 'supersede', 'drop', 'postpone', 'keep', 'unresolved'];
  document.getElementById('tally').innerHTML = order.filter(k => c[k]).map(k =>
    `<span style="color:var(--${k === 'unresolved' ? 'ask' : k})">
       <b>${c[k]}</b> ${k === 'unresolved' ? 'unanswered' : LABEL[k].toLowerCase()}</span>`).join('');

  const all = decisions('all').length;
  const shown = decisions('visible').length;
  const held = all - shown;
  const btn = document.getElementById('copy');
  const bad = state.some(t => t.choice === 'supersede' && !t.target.trim() && isVisible(t));

  btn.disabled = bad;
  btn.textContent = bad ? 'Supersede needs a target'
    : filter === 'all' ? `Copy ${all} decisions` : `Copy ${shown} visible decisions`;

  const hint = document.getElementById('hint');
  if (held > 0) {
    hint.className = 'hint warn';
    hint.textContent = `Filter active - ${shown} visible decisions will be copied; ${held} other resolved decisions are NOT included. Switch to "all" to copy everything.`;
  } else if (!hint.dataset.resumed) {
    hint.className = 'hint';
    hint.textContent = 'Radios are pre-set to what the agent proposed - change only what is wrong, then copy and paste back into Claude.';
  }
  save();
}

const payload = () => JSON.stringify(decisions(filter === 'all' ? 'all' : 'visible'), null, 1);

document.querySelectorAll('#groupby button').forEach(b => b.onclick = () => {
  document.querySelectorAll('#groupby button').forEach(x => x.classList.remove('on'));
  b.classList.add('on');
  groupBy = b.dataset.group;
  render();
});

document.querySelectorAll('#filters button').forEach(b => b.onclick = () => {
  document.querySelectorAll('#filters button').forEach(x => x.classList.remove('on'));
  b.classList.add('on');
  filter = b.dataset.filter;
  applyFilter();
  updateTally();
});

document.getElementById('copy').onclick = async () => {
  await navigator.clipboard.writeText(payload());
  const b = document.getElementById('copy');
  const t = b.textContent;
  b.textContent = 'Copied - paste into Claude';
  setTimeout(() => { b.textContent = t; }, 1800);
};

document.getElementById('download').onclick = () => {
  const blob = new Blob([payload()], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'decisions.json';
  a.click();
};

const resumed = restore();
render();
if (resumed) {
  const hint = document.getElementById('hint');
  hint.dataset.resumed = '1';
  hint.innerHTML = 'Resumed your unsaved choices from this browser. <a href="#" onclick="discard();return false" style="color:var(--accent)">Discard and start from the proposals</a>.';
}
</script>
</body>
</html>
"""


def main(run_dir, vault_name=None):
    with open(os.path.join(run_dir, "proposals.json"), encoding="utf-8") as fh:
        proposals = json.load(fh)

    vault_root = os.path.abspath(os.path.join(run_dir, "..", "..", "..", ".."))
    vault = vault_name or os.path.basename(vault_root)

    html = (TEMPLATE
            .replace("__DATA__", json.dumps(proposals, ensure_ascii=False))
            .replace("__VAULT__", json.dumps(vault))
            .replace("__TODAY__", json.dumps(datetime.date.today().isoformat())))

    out = os.path.join(run_dir, "review.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)

    unresolved = sum(1 for p in proposals if p.get("proposal") == "needs-user")
    print(f"{len(proposals)} tasks -> {out} ({unresolved} need a decision; vault '{vault}')")
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else None)
