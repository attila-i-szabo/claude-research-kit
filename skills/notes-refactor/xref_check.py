#!/usr/bin/env python3
"""Check the cross-references of a project-layout notes tree.

Every ``File `X` `` or ``Files `X`–`Y` `` in Markdown and Python files below ROOT is
resolved relative to the citing file's directory; X must match exactly one ``NN-*.md``.
A trailing ``§n``, ``Table n`` or ``Fig. n``/``Figure n`` is checked against the cited file
(heading ``#… n.`` or ``#… n ``, caption ``**Table n.**``, ``**Fig. n.**``/``**Figure n.**``).

Usage:
    python3 xref_check.py ROOT                    # report failures, exit 1 if any
    python3 xref_check.py ROOT --incoming FILE... # list every citation of the given files

Limits: a reference that still resolves but points at content that was renumbered is
not detected; apply the refactor's section mapping table for that.
"""
import argparse
import glob
import os
import re
import sys

SKIP = ("/.git/", "/papers/", "/data/", "/node_modules/")
REF = re.compile(
    r"Files? ((?:`[^`]+`(?:\s*(?:,|and|–|-)\s*)?)+)"
    r"(,? ?(?:§§?[\d.]+|Table \w+|Fig\. \d+|Figure \d+))?"
)
TOKEN = re.compile(r"(\.\./)*([A-Za-z0-9_-]+/)*\d\d")


def source_files(root):
    out = []
    for ext in ("md", "py"):
        out += glob.glob(os.path.join(root, "**", f"*.{ext}"), recursive=True)
    return sorted(f for f in out if not any(s in f for s in SKIP))


def citations(path):
    """Yield (line, token, target_or_None, suffix) for every notes reference in a file."""
    text = open(path, encoding="utf-8").read()
    here = os.path.dirname(path)
    for m in REF.finditer(text):
        tokens = re.findall(r"`([^`]+)`", m.group(1))
        suffix = (m.group(2) or "").strip(", ")
        line = text.count("\n", 0, m.start()) + 1
        for i, tok in enumerate(tokens):
            if not TOKEN.fullmatch(tok):
                continue
            base, num = os.path.split(tok)
            hits = glob.glob(
                os.path.join(os.path.normpath(os.path.join(here, base)), num + "-*.md")
            )
            target = hits[0] if len(hits) == 1 else None
            yield line, tok, target, suffix if i == len(tokens) - 1 else ""


def suffix_ok(target, suffix):
    text = open(target, encoding="utf-8").read()
    if suffix.startswith("§"):
        n = suffix.lstrip("§").rstrip(".")
        return re.search(rf"^#+ {re.escape(n)}[. ]", text, re.M) is not None
    if suffix.startswith("Table"):
        return f"**{suffix}.**" in text
    if suffix.startswith("Fig"):
        n = suffix.split()[-1]
        return f"**Fig. {n}.**" in text or f"**Figure {n}.**" in text
    return True


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("root")
    ap.add_argument(
        "--incoming",
        nargs="+",
        metavar="FILE",
        help="list citations of these notes files",
    )
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    wanted = {os.path.abspath(f) for f in args.incoming or []}
    bad = 0
    for f in source_files(root):
        rel = os.path.relpath(f, root)
        for line, tok, target, suffix in citations(f):
            if wanted:
                if target and os.path.abspath(target) in wanted:
                    print(f"{rel}:{line}: {tok} {suffix}".rstrip())
                continue
            if target is None:
                print(f"{rel}:{line}: unresolved `{tok}`")
                bad += 1
            elif suffix and not suffix_ok(target, suffix):
                print(f"{rel}:{line}: `{tok}` has no {suffix}")
                bad += 1
    if not wanted:
        print(f"{bad} failure(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
