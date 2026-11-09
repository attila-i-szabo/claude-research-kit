#!/usr/bin/env python3
"""Check Markdown files against the markdown-style house rules (see SKILL.md)."""

import os
import re
import sys

SPACING = re.compile(r"\\(?:[,;:!]|q?quad(?![A-Za-z])|hspace|phantom)")
ROW_OPTION = re.compile(r"\\\\\s*\[[^\]]*\]")
LIST_ITEM = re.compile(r"^( *)(?:[-*+]|\d+[.)])\s")
FENCE = re.compile(r"^\s*(```|~~~)")
DIFF_BEFORE = re.compile(
    r"(?<![A-Za-z\\])[dD](?:\s*\\[A-Za-z]+|\s*[A-Za-z0-9]|\s*[\^_]\{[^{}]*\}"
    r"|\s*[\^_]\S)+\s*$|\\mathrm\{d\}\s*\\?[A-Za-z]+\s*$"
)
DIFF_AFTER = re.compile(r"^\s*(?:[dD](?:\\?[A-Za-z]|\s*\\[A-Za-z])|\\mathrm\{d\})")


def fenced_lines(lines):
    """Return the set of 1-based line numbers inside fenced code blocks."""
    inside, out = False, set()
    for k, line in enumerate(lines, 1):
        if FENCE.match(line):
            out.add(k)
            inside = not inside
        elif inside:
            out.add(k)
    return out


def scan_math(text, fenced):
    """Return (start_line, content, is_display) for each math segment outside code."""
    segments = []
    line_starts = [0] + [m.end() for m in re.finditer("\n", text)]
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif line in fenced:
            # jump to the newline ending this line, which advances the counter
            i = line_starts[line] - 1 if line < len(line_starts) else n
        elif c == "\\" and i + 1 < n and text[i + 1] in "$`\\":
            i += 2
        elif c == "`":
            ticks = re.match(r"`+", text[i:]).group(0)
            end = text.find(ticks, i + len(ticks))
            if end != -1 and "\n\n" not in text[i:end]:
                line += text.count("\n", i, end)
                i = end + len(ticks)
            else:
                i += len(ticks)
        elif c == "$":
            delim = "$$" if text.startswith("$$", i) else "$"
            j = i + len(delim)
            while j < n and not text.startswith(delim, j):
                if text[j] == "\\":
                    j += 1
                elif delim == "$" and text.startswith("\n\n", j):
                    j = n
                j += 1
            if j >= n:
                i += len(delim)
                continue
            content = text[i + len(delim) : j]
            segments.append((line, content, delim == "$$"))
            line += content.count("\n")
            i = j + len(delim)
        else:
            i += 1
    return segments


def boxed_contents(content):
    """Yield the brace-matched argument of every \\boxed in content."""
    for m in re.finditer(r"\\boxed\s*\{", content):
        depth, j = 1, m.end()
        while j < len(content) and depth:
            depth += {"{": 1, "}": -1}.get(content[j], 0)
            j += 1
        yield content[m.end() : j - 1]


def check_math(segment, report, table_lines):
    """Apply rules 1, 3, 4, 5, 6 and 7 to one math segment."""
    start, content, display = segment

    def at(offset):
        return start + content.count("\n", 0, offset)

    for m in SPACING.finditer(content):
        cmd = m.group(0)
        if cmd == r"\," and (
            DIFF_BEFORE.search(content[: m.start()])
            or DIFF_AFTER.match(content[m.end() :])
        ):
            continue
        if "quad" in cmd:
            report(at(m.start()), "R1?", f"{cmd}: only between short equations")
        else:
            report(at(m.start()), "R1", f"spacing command {cmd}")
    for m in ROW_OPTION.finditer(content):
        report(at(m.start()), "R1", f"row option {m.group(0)}")
    if display:
        if re.search(r"\n[ \t]*\n", content):
            report(start, "R3", "blank line inside $$ block")
        stripped = content.strip()
        if stripped.startswith("\\\\") or stripped.endswith("\\\\"):
            report(start, "R3", "$$ block starts or ends with \\\\")
    for box in boxed_contents(content):
        if "\\\\" in box:
            report(start, "R4", "\\\\ inside \\boxed{}")
    for m in re.finditer(r"[<>]", content):
        k = m.start()
        before = content[k - 1] if k > 0 else " "
        after = content[k + 1] if k + 1 < len(content) else " "
        if not (before.isspace() and after.isspace()):
            snippet = content[max(0, k - 6) : k + 7].replace("\n", " ")
            report(at(k), "R5", f"'{m.group(0)}' needs spaces: ...{snippet}...")
    if "`" in content:
        report(start, "R7", "backtick inside math")
    if "|" in content and "\n" not in content and start in table_lines:
        report(start, "R6", "| inside math in a table row (use \\vert or \\mid)")


def check_tables(lines, fenced, report):
    """Check rule 6 column counts and return the set of table-row line numbers."""
    table_lines, header = set(), None
    for k, line in enumerate(lines, 1):
        if k not in fenced and line.lstrip().startswith("|"):
            table_lines.add(k)
            count = line.count("|") - line.count("\\|")
            if header is None:
                header = count
            elif count != header:
                report(k, "R6", f"row has {count} '|' but header has {header}")
        else:
            header = None
    return table_lines


def check_lists(lines, skip, report):
    """Check rule 8: indentation in multiples of 4, blank line before a list."""
    for k, line in enumerate(lines, 1):
        m = LIST_ITEM.match(line)
        if k in skip or not m:
            continue
        indent = len(m.group(1))
        if indent % 4:
            report(k, "R8", f"list item indented by {indent} spaces")
        if indent == 0 and k > 1 and lines[k - 2].strip():
            # walk back over the paragraph; fine if it is already part of a list
            j = k - 1
            while j >= 1 and lines[j - 1].strip():
                if j not in skip and LIST_ITEM.match(lines[j - 1]):
                    break
                j -= 1
            if j < 1 or not lines[j - 1].strip():
                report(k, "R8", "no blank line before list")


def check_file(path):
    """Return the sorted list of (line, code, message) violations of one file."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    found = []

    def report(line, code, msg):
        found.append((line, code, msg))

    fenced = fenced_lines(lines)
    table_lines = check_tables(lines, fenced, report)
    display_lines = set()
    for segment in scan_math(text, fenced):
        start, content, display = segment
        if display:
            display_lines.update(range(start, start + content.count("\n") + 1))
        check_math(segment, report, table_lines)
    check_lists(lines, fenced | display_lines, report)
    return sorted(found)


def markdown_files(paths):
    """Expand directories (without following symlinks) into their .md files."""
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                for f in sorted(files):
                    if f.endswith(".md"):
                        yield os.path.join(root, f)
        else:
            yield p


def main(argv):
    """Check files and directories; return 1 if any error (not warning) is found."""
    if not argv:
        print("usage: check_markdown.py FILE_OR_DIR ...", file=sys.stderr)
        return 2
    errors = 0
    for path in markdown_files(argv):
        for line, code, msg in check_file(path):
            print(f"{path}:{line}: [{code}] {msg}")
            errors += not code.endswith("?")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
