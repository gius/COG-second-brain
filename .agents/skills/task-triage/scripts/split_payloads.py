"""Merge per-cluster task JSON into provenance buckets, then split any bucket
over the size cap into balanced agent payloads, keeping same-file tasks together.

Input:  cluster_<NAME>.json files produced by bucket_and_cluster.py (in RUN_DIR).
Output: payload_<provenance>[_<n>].json + payload_manifest.json in the same dir.

Used by task-triage SKILL.md §5 to bound each classification agent's payload so
evidence stays accurate. Run from the run dir, or pass it as the first argument.
"""
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict

# Cluster -> provenance (mirrors SKILL.md §4a). 'other' defaults to user_curated
# because it is dominated by hand-authored project docs; the classifying agent
# still applies per-file provenance when choosing cancel vs untrack.
PROVENANCE = {
    "weekly_checkins": "user_curated",
    "project_overviews": "user_curated",
    "other": "user_curated",
    "daily_briefs": "ai_generated",
    "booklets": "ai_generated",
    "consolidations": "ai_generated",
    "braindumps": "ai_generated",
}

SPLIT_THRESHOLD = 40  # split a provenance bucket only if it exceeds this


def load_clusters(run_dir):
    buckets = defaultdict(list)
    for cluster, prov in PROVENANCE.items():
        path = os.path.join(run_dir, f"cluster_{cluster}.json")
        if not os.path.exists(path):
            continue
        for t in json.load(open(path, encoding="utf-8")):
            t["_cluster"] = cluster
            buckets[prov].append(t)
    return buckets


def split_balanced(tasks, parts):
    """Split into `parts` near-equal groups, never splitting a single file across groups."""
    by_file = OrderedDict()
    for t in tasks:
        by_file.setdefault(t["file"], []).append(t)
    groups = [[] for _ in range(parts)]
    for file_group in sorted(by_file.values(), key=len, reverse=True):
        target = min(range(parts), key=lambda i: len(groups[i]))
        groups[target].extend(file_group)
    return groups


def main(run_dir):
    buckets = load_clusters(run_dir)
    manifest = {}
    for prov, tasks in buckets.items():
        n = len(tasks)
        parts = max(1, -(-n // SPLIT_THRESHOLD)) if n > SPLIT_THRESHOLD else 1
        groups = split_balanced(tasks, parts) if parts > 1 else [tasks]
        for i, g in enumerate(groups, 1):
            name = f"{prov}_{i}" if parts > 1 else prov
            out = os.path.join(run_dir, f"payload_{name}.json")
            json.dump(g, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            files = Counter(t["file"].replace("\\", "/").split("/")[-1] for t in g)
            manifest[name] = {"count": len(g), "file": out, "top_files": files.most_common(6)}
    for name, m in manifest.items():
        print(f"{name:18} {m['count']:3} -> {m['file']}")
        for fn, c in m["top_files"]:
            print(f"    {c:3}  {fn}")
    json.dump(manifest, open(os.path.join(run_dir, "payload_manifest.json"), "w"), indent=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
