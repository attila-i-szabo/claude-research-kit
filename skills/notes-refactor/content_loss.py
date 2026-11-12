#!/usr/bin/env python3
"""Find paragraphs of the old notes that are missing from the refactored tree.

Each paragraph of the snapshot files (reference lists excluded) is cut into overlapping
6-word shingles after stripping cross-references (File `X`, §n, Table n, Section n) and
normalising whitespace; a paragraph is reported when the fraction of its shingles found
anywhere in the new tree is below the threshold. Every reported paragraph must be a
deliberate change (rewritten scope, generalised notation, deduplication, removal).

Usage:
    python3 content_loss.py SNAPSHOT_DIR NEW_DIR [FILE ...] [--threshold 0.4]

FILE paths are relative to SNAPSHOT_DIR (default: every .md in it).
"""
import argparse
import glob
import os
import re

STRIP = re.compile(
    r"Files? `[^`]*`|`\.\./[^`]*`|§§?[\d.]+|Table \d\w?|Fig(ure|\.) \d+|Section \d+"
)


def norm(s):
    return re.sub(r"\s+", " ", STRIP.sub("", s)).strip()


def body(text):
    m = re.search(r"^## (\d+\. )?References\s*$", text, re.M)
    return text[: m.start()] if m else text


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("snapshot")
    ap.add_argument("new")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--threshold", type=float, default=0.4)
    ap.add_argument("--min-words", type=int, default=12)
    args = ap.parse_args()
    new = norm(
        " ".join(
            open(f, encoding="utf-8").read()
            for f in glob.glob(os.path.join(args.new, "**", "*.md"), recursive=True)
        )
    )
    files = args.files or [
        os.path.relpath(f, args.snapshot)
        for f in glob.glob(os.path.join(args.snapshot, "**", "*.md"), recursive=True)
    ]
    n_bad = 0
    for rel in sorted(files):
        text = body(open(os.path.join(args.snapshot, rel), encoding="utf-8").read())
        for para in text.split("\n\n"):
            words = norm(para).split(" ")
            if len(words) < args.min_words:
                continue
            shingles = [" ".join(words[i : i + 6]) for i in range(0, len(words) - 5, 3)]
            frac = sum(s in new for s in shingles) / len(shingles)
            if frac < args.threshold:
                n_bad += 1
                print(f"{rel}: {frac:.2f}: {' '.join(words)[:160]}")
    print(f"{n_bad} paragraph(s) below {args.threshold}")


if __name__ == "__main__":
    main()
