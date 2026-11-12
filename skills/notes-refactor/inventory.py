#!/usr/bin/env python3
"""Inventory of notes files for planning a refactor, without reading them whole.

For each Markdown file under the given paths (default: ROOT/notes): the H1, every heading
with the word count of its section, the total (reference list excluded, flagged above the
budget), the notes files it cites, and how often it is cited from notes and code.

Usage:
    python3 inventory.py ROOT [PATH ...] [--budget 4000] [--no-sections]
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xref_check import citations, source_files  # noqa: E402

REFS = re.compile(r"^## (\d+\. )?References\s*$", re.M)


def sections(text):
    """Return [(heading, words)] for every heading, words up to the next heading."""
    out, head, n = [], None, 0
    for line in text.split("\n"):
        if re.match(r"^#+ ", line):
            if head is not None:
                out.append((head, n))
            head, n = line, 0
        else:
            n += len(line.split())
    if head is not None:
        out.append((head, n))
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("root")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--budget", type=int, default=4000)
    ap.add_argument("--no-sections", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    paths = args.paths or [os.path.join(root, "notes")]
    files = []
    for p in paths:
        files += (
            [p]
            if p.endswith(".md")
            else glob.glob(os.path.join(p, "**", "*.md"), recursive=True)
        )
    files = sorted(os.path.abspath(f) for f in files if "/papers/" not in f)

    incoming = collections.Counter()
    for f in source_files(root):
        for _, _, target, _ in citations(f):
            if target and os.path.abspath(target) != f:
                incoming[os.path.abspath(target)] += 1

    for f in files:
        text = open(f, encoding="utf-8").read()
        m = REFS.search(text)
        body = text[: m.start()] if m else text
        words = len(body.split())
        flag = "  ** over budget **" if words > args.budget else ""
        rel = os.path.relpath(f, root)
        h1 = next((l for l in text.split("\n") if l.startswith("# ")), "(no H1)")
        print(f"== {rel}  {words} words, cited {incoming[f]}x{flag}\n   {h1}")
        if not args.no_sections:
            for head, n in sections(body):
                if not head.startswith("# "):
                    print(f"   {n:5d}  {head}")
        out = collections.Counter(
            os.path.relpath(t, root)
            for _, _, t, _ in citations(f)
            if t and os.path.abspath(t) != f
        )
        if out:
            print(
                "   cites: " + ", ".join(f"{k} ({v})" for k, v in sorted(out.items()))
            )


if __name__ == "__main__":
    main()
