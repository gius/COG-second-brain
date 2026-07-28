#!/usr/bin/env python3
"""Fail if a skill file leaks anything that only exists on one machine or one agent tool.

Skills ship to other people and other agent runtimes. A skill that names a personal
memory file, a Claude-specific directory, or an absolute Windows path is broken for
everyone but its author.

Usage:  python scripts/check_skill_portability.py
Exit 0 = clean, 1 = violations found.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SKILL_TREES = [".agents/skills", ".claude/skills", ".gemini/skills", ".kiro/skills"]

# Runtime artifacts are staged under .cog/<skill>/ and are the one sanctioned path.
FORBIDDEN = [
    (
        "personal memory store",
        re.compile(r"\bmemory/|\bfeedback_[a-z0-9_]+\.md|\breference_[a-z0-9_]+\.md|\bMEMORY\.md"),
        "Memory is injected into context automatically and is per-user. State the rule directly, or drop it.",
    ),
    (
        "tool-specific path",
        re.compile(r"\.claude/|\.gemini/|\.kiro/"),
        "Use .cog/<skill>/... for runtime artifacts so the skill works under any agent runtime.",
    ),
    (
        "machine-specific path",
        re.compile(r"[A-Za-z]:\\{1,2}(Users|private)|/home/[a-z]+|~/\.claude"),
        "Absolute paths only exist on one machine. Use a vault-relative path.",
    ),
]


def main() -> int:
    violations = []

    for tree in SKILL_TREES:
        root = REPO / tree
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            if "/runs/" in path.as_posix():  # runtime output, not shipped source
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for label, pattern, fix in FORBIDDEN:
                    if pattern.search(line):
                        rel = path.relative_to(REPO).as_posix()
                        violations.append((rel, lineno, label, line.strip(), fix))

    if not violations:
        print("Skill portability: clean")
        return 0

    print(f"Skill portability: {len(violations)} violation(s)\n")
    for rel, lineno, label, line, fix in violations:
        snippet = line if len(line) <= 100 else line[:97] + "..."
        print(f"  {rel}:{lineno}  [{label}]")
        print(f"    {snippet}")
        print(f"    fix: {fix}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
