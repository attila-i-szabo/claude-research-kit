#!/usr/bin/env python3
"""Compare the labels cited in notes files with their reference lists.

A label is ``[ABC12]`` (letters, two digits, optional suffix letter), cited alone or in a
group ``[ABC12, DE99]``. The reference list is everything after the heading
``## n. References`` (or ``## References``).

Usage:
    python3 refcheck.py FILE ...                      # report missing and unused labels
    python3 refcheck.py FILE ... --fix [--pool DIR]   # rebuild each list from its citations

With --fix, entries are taken from the file's own list, then from every reference line
of the .md files under DIR (e.g. the pre-refactor snapshot); labels found nowhere are
reported and left out.
"""
import argparse
import glob
import os
import re

LABEL = r"[A-Za-z]+[0-9]{2}[a-z]?"
ENTRY = re.compile(rf"^\[({LABEL})\] ", re.M)
HEAD = re.compile(r"^## (\d+\. )?References\s*$", re.M)


def cited(body):
    out = set()
    for grp in re.findall(r"\[([A-Za-z][A-Za-z0-9, ]*)\]", body):
        for lab in re.split(r",\s*", grp):
            if re.fullmatch(LABEL, lab):
                out.add(lab)
    return out


def entries(text):
    return {m.group(1): line for line in text.split("\n") if (m := ENTRY.match(line))}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("files", nargs="+")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--pool", help="directory whose .md reference lines may be reused")
    args = ap.parse_args()
    pool = {}
    if args.pool:
        for f in glob.glob(os.path.join(args.pool, "**", "*.md"), recursive=True):
            for k, v in entries(open(f, encoding="utf-8").read()).items():
                pool.setdefault(k, v)
    for f in args.files:
        text = open(f, encoding="utf-8").read()
        m = HEAD.search(text)
        if not m:
            print(f"{f}: no References section")
            continue
        body, reflist = text[: m.end()], text[m.end() :]
        have = entries(reflist)
        want = cited(text[: m.start()])
        missing, unused = sorted(want - set(have)), sorted(set(have) - want)
        if missing or unused:
            print(f"{f}: missing {missing}; unused {unused}")
        if args.fix and (missing or unused):
            src = {**pool, **have}
            lost = [l for l in missing if l not in src]
            if lost:
                print(f"{f}: no entry found for {lost}")
            keep = [src[l] for l in sorted(want, key=str.lower) if l in src]
            open(f, "w", encoding="utf-8").write(
                body.rstrip("\n") + "\n\n" + "\n\n".join(keep) + "\n"
            )


if __name__ == "__main__":
    main()
