#!/usr/bin/env python3
"""Parse Obsidian Tasks CLI output, bucket by due date, cluster by source folder.

Usage:
    obsidian tasks todo format=json verbose > $TEMP/cog-tasks.json
    python scripts/bucket_and_cluster.py [--scope overdue|today|week|all] [--today YYYY-MM-DD]

Writes per-cluster JSON files to $TEMP/cluster_<NAME>.json and prints a summary.
Cluster names match those expected by SKILL.md §2 and §5.

UTF-8 safe on Windows consoles (forces stdout reconfigure). The 📅 date marker
is parsed from task text; today's date comes from --today or the system clock.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

DATE_RE = re.compile(r"\U0001f4c5\s*(\d{4}-\d{2}-\d{2})")  # 📅 YYYY-MM-DD

CLUSTER_RULES = [
    ("weekly_checkins", lambda p: p.startswith("01-daily/checkins/")),
    ("project_overviews", lambda p: p.startswith("04-projects/") and p.endswith("PROJECT-OVERVIEW.md")),
    ("daily_briefs", lambda p: p.startswith("01-daily/briefs/")),
    ("consolidations", lambda p: p.startswith("05-knowledge/consolidated/")),
    ("booklets", lambda p: p.startswith("05-knowledge/booklets/")),
    ("braindumps", lambda p: "/braindumps/" in p or p.startswith("braindumps/")),
]


def cluster_for(file_path: str) -> str:
    for name, match in CLUSTER_RULES:
        if match(file_path):
            return name
    return "other"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default=None,
                    help="Path to cog-tasks.json (default: $TEMP/cog-tasks.json)")
    ap.add_argument("--outdir", default=None,
                    help="Directory for cluster_*.json (default: $TEMP)")
    ap.add_argument("--scope", default="default",
                    choices=["default", "overdue", "today", "week", "all"],
                    help="default = overdue + today (matches TASKS.md view)")
    ap.add_argument("--today", default=None,
                    help="Override today's date (YYYY-MM-DD) — for testing")
    return ap.parse_args()


def main() -> int:
    # UTF-8 safe stdout on Windows cp1252 consoles
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    temp = os.environ.get("TEMP") or "/tmp"
    input_path = args.input or os.path.join(temp, "cog-tasks.json")
    outdir = args.outdir or temp

    if not Path(input_path).exists():
        print(f"ERROR: {input_path} not found. Run:", file=sys.stderr)
        print("  obsidian tasks todo format=json verbose > \"$TEMP/cog-tasks.json\"", file=sys.stderr)
        return 1

    today = date.fromisoformat(args.today) if args.today else date.today()
    week_ahead = today + timedelta(days=7)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    buckets = {"overdue": [], "today": [], "future": [], "nodate": []}
    for t in data:
        m = DATE_RE.search(t["text"])
        if not m:
            buckets["nodate"].append(t)
            continue
        due = date.fromisoformat(m.group(1))
        t["due"] = m.group(1)
        if due < today:
            buckets["overdue"].append(t)
        elif due == today:
            buckets["today"].append(t)
        else:
            buckets["future"].append(t)

    scope = args.scope
    if scope == "default":
        in_scope = buckets["overdue"] + buckets["today"]
    elif scope == "overdue":
        in_scope = buckets["overdue"]
    elif scope == "today":
        in_scope = buckets["today"]
    elif scope == "week":
        in_scope = buckets["overdue"] + buckets["today"] + [
            t for t in buckets["future"]
            if date.fromisoformat(t["due"]) <= week_ahead
        ]
    else:  # all
        in_scope = buckets["overdue"] + buckets["today"] + buckets["future"] + buckets["nodate"]

    # Stable sort: by due date (nodate last), then by file, then by line
    in_scope.sort(key=lambda t: (t.get("due") or "9999-12-31", t["file"], int(t["line"])))

    clusters: dict[str, list] = collections.defaultdict(list)
    for t in in_scope:
        clusters[cluster_for(t["file"])].append(t)

    # Write cluster files
    for name, items in clusters.items():
        path = Path(outdir) / f"cluster_{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"Today: {today.isoformat()}    Scope: {scope}")
    print(f"Buckets:  overdue={len(buckets['overdue'])}  today={len(buckets['today'])}  "
          f"future={len(buckets['future'])}  nodate={len(buckets['nodate'])}")
    print(f"In-scope total: {len(in_scope)}\n")
    print("Clusters (written to {0}):".format(outdir))
    for name, items in sorted(clusters.items(), key=lambda x: -len(x[1])):
        print(f"  {len(items):3d}  {name}")

    # Machine-readable summary for the skill to parse
    summary = {
        "today": today.isoformat(),
        "scope": scope,
        "bucket_counts": {k: len(v) for k, v in buckets.items()},
        "in_scope_total": len(in_scope),
        "clusters": {name: len(items) for name, items in clusters.items()},
        "cluster_files": {name: str(Path(outdir) / f"cluster_{name}.json")
                          for name in clusters},
    }
    with open(Path(outdir) / "triage_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSummary: {Path(outdir) / 'triage_summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
