"""List the paragraphs a person changed between an agent draft and their edited version.

Usage: uv run edit_pairs.py <before.md> <after.md>

Prints one markdown block per changed region: the draft text, the edited text,
and the kind of change (rewritten / added / removed). Frontmatter and Obsidian
%% comments %% are dropped first, because they carry sources, not voice.
"""

import difflib
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
OBSIDIAN_COMMENT = re.compile(r"%%.*?%%", re.DOTALL)


def paragraphs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = FRONTMATTER.sub("", text)
    text = OBSIDIAN_COMMENT.sub("", text)
    blocks = (block.strip() for block in re.split(r"\n\s*\n", text))
    return [block for block in blocks if block]


def normalized(paragraph: str) -> str:
    """Ignore table padding and re-wrapping, which change no word."""
    unpadded = re.sub(r"[ \t]*\|[ \t]*", "|", re.sub(r"-{3,}", "---", paragraph))
    return " ".join(unpadded.split())


def word_change_ratio(before: list[str], after: list[str]) -> float:
    old, new = " ".join(before).split(), " ".join(after).split()
    return 1 - difflib.SequenceMatcher(a=old, b=new, autojunk=False).ratio()


def pair_within(old: list[str], new: list[str]):
    """Split a rewritten block into one pair per paragraph the person kept but reworded."""
    remaining = list(range(len(new)))
    for paragraph in old:
        best = max(remaining, key=lambda i: 1 - word_change_ratio([paragraph], [new[i]]), default=None)
        if best is None or word_change_ratio([paragraph], [new[best]]) > 0.6:
            yield "removed", [paragraph], []
            continue
        for skipped in [i for i in remaining if i < best]:
            yield "added", [], [new[skipped]]
            remaining.remove(skipped)
        if normalized(paragraph) != normalized(new[best]):
            yield "rewritten", [paragraph], [new[best]]
        remaining.remove(best)
    for leftover in remaining:
        yield "added", [], [new[leftover]]


def changed_regions(before: list[str], after: list[str]):
    keys_before, keys_after = [normalized(p) for p in before], [normalized(p) for p in after]
    matcher = difflib.SequenceMatcher(a=keys_before, b=keys_after, autojunk=False)
    for tag, b1, b2, a1, a2 in matcher.get_opcodes():
        if tag == "insert":
            yield "added", [], after[a1:a2]
        elif tag == "delete":
            yield "removed", before[b1:b2], []
        elif tag == "replace":
            yield from pair_within(before[b1:b2], after[a1:a2])


def merge_runs(regions):
    """Join neighbouring added or removed paragraphs, so a cut section reads as one change."""
    merged = []
    for kind, old, new in regions:
        if merged and kind != "rewritten" and merged[-1][0] == kind:
            merged[-1] = (kind, merged[-1][1] + old, merged[-1][2] + new)
        else:
            merged.append((kind, old, new))
    return merged


def render(regions) -> str:
    out = []
    for number, (kind, old, new) in enumerate(regions, start=1):
        header = f"### Pair {number} - {kind}"
        if kind == "rewritten":
            header += f", {word_change_ratio(old, new):.0%} of words changed"
        out.append(header)
        out.append("**Draft:**\n\n" + ("\n\n".join(old) or "(nothing)"))
        out.append("**Edited:**\n\n" + ("\n\n".join(new) or "(nothing)"))
    return "\n\n".join(out) if out else "No changed paragraphs."


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    before, after = (Path(arg) for arg in sys.argv[1:])
    sys.stdout.reconfigure(encoding="utf-8")
    print(render(merge_runs(changed_regions(paragraphs(before), paragraphs(after)))))


if __name__ == "__main__":
    main()
