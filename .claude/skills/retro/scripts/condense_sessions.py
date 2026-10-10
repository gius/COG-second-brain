"""Condense Claude Code session JSONL logs into compact timelines for the retro skill.

Usage: condense_sessions.py <out_dir> <session.jsonl>...
Per session writes <id>.md: user prompts, every tool call with a short input,
tool errors, and a stats header (calls by tool, search calls before first edit).
"""
import json
import sys
from collections import Counter
from pathlib import Path

SEARCH_TOOLS = {"Grep", "Glob", "Read", "LS"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def short(value, limit=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + "..."


def tool_summary(name, inp):
    if not isinstance(inp, dict):
        return short(inp)
    for key in ("file_path", "pattern", "command", "path", "query", "url", "skill", "description", "prompt"):
        if key in inp:
            extra = f" path={inp['path']}" if key == "pattern" and "path" in inp else ""
            return f"{key}={short(inp[key])}{extra}"
    return short(inp)


def result_text(content):
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def condense(path: Path, out_dir: Path):
    lines, counts = [], Counter()
    searches_before_edit, edited = 0, False
    first_ts = last_ts = None
    for raw in path.open(encoding="utf-8"):
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        ts = rec.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        msg = rec.get("message") or {}
        content = msg.get("content")
        if rec.get("type") == "user":
            if isinstance(content, str):
                if not content.startswith("<"):
                    lines.append(f"\n[{(ts or '')[11:16]}] USER: {short(content, 600)}")
            elif isinstance(content, list):
                for c in content:
                    if c.get("type") == "tool_result" and c.get("is_error"):
                        lines.append(f"    !! ERROR: {short(result_text(c.get('content')), 240)}")
                    elif c.get("type") == "text" and not c.get("text", "").startswith("<"):
                        lines.append(f"\n[{(ts or '')[11:16]}] USER: {short(c['text'], 600)}")
        elif rec.get("type") == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_use":
                    name = c.get("name", "?")
                    counts[name] += 1
                    if name in EDIT_TOOLS:
                        edited = True
                    elif not edited and (name in SEARCH_TOOLS or name == "Bash"):
                        searches_before_edit += 1
                    lines.append(f"  - {name}: {tool_summary(name, c.get('input'))}")
                elif c.get("type") == "text" and c.get("text", "").strip():
                    lines.append(f"  > {short(c['text'], 200)}")
    header = [
        f"# Session {path.stem}",
        f"span: {first_ts} -> {last_ts}",
        f"tool calls: {sum(counts.values())} | by tool: {dict(counts.most_common())}",
        f"search/read/bash calls before first edit: {searches_before_edit}",
        "",
    ]
    (out_dir / f"{path.stem}.md").write_text("\n".join(header + lines), encoding="utf-8")
    return path.stem, sum(counts.values()), searches_before_edit


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for p in sys.argv[2:]:
        print(*condense(Path(p), out))
