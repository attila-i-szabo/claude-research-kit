#!/usr/bin/env python3
"""PostToolUse hook: opt-in markdown-style check and black, keyed on the nearest CLAUDE.md."""

import json
import os
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CHECKER = os.path.join(KIT, "skills", "markdown-style", "check_markdown.py")
MAX_LINES = 40


def nearest_claude_md(path):
    """Return the text of the nearest CLAUDE.md above path, or '' if there is none."""
    d = os.path.dirname(os.path.abspath(path))
    while True:
        candidate = os.path.join(d, "CLAUDE.md")
        if os.path.isfile(candidate):
            with open(candidate, encoding="utf-8", errors="replace") as f:
                return f.read()
        parent = os.path.dirname(d)
        if parent == d:
            return ""
        d = parent


def main():
    """Run the opted-in checks on the edited file; exit 2 to report errors to Claude."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not os.path.isfile(path):
        return 0
    config = nearest_claude_md(path)

    if path.endswith(".md") and "markdown-style" in config:
        result = subprocess.run(
            [sys.executable, CHECKER, path], capture_output=True, text=True
        )
        if result.returncode == 1:
            lines = result.stdout.strip().split("\n")
            more = len(lines) - MAX_LINES
            msg = "\n".join(lines[:MAX_LINES])
            if more > 0:
                msg += f"\n... and {more} more (run {CHECKER} {path})"
            print(f"markdown-style violations in {path}:\n{msg}", file=sys.stderr)
            return 2

    if path.endswith(".py") and "python-style" in config:
        black = shutil.which("black")
        if black:
            subprocess.run([black, "-q", path], capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
