# Claude research kit

Skills, agents and hooks for writing physics literature reviews, research notes and research code with Claude Code, to the same standards in every project. This repository is the single source of truth: `install.sh` symlinks its pieces into `~/.claude/`, so an edit here takes effect in every project immediately, in new sessions.

## Contents

| Piece | Kind | Purpose |
|---|---|---|
| `skills/research-writing` | skill | Shared standards: audience, rigour, citations, references, state not history, budgets, agent hygiene, reading rules, paper library |
| `skills/research-review` | skill | Literature-review pipeline: triage → extraction → writing; evidence ledgers |
| `skills/research-notes` | skill | Notes with new results: required literature checks, derivations, notes about code and runs |
| `skills/project-layout` | skill | Project root, numbered notes files, nested notes directories, READMEs (notes and code), cross-references, splitting and merging |
| `skills/markdown-style` | skill + script | Markdown/LaTeX house style and `check_markdown.py` |
| `skills/python-style` | skill | Light and production Python style, packaging and maintainability |
| `agents/lit-searcher` | agent (Sonnet) | Literature search: shortlist for a review, or prior-work check for notes |
| `agents/paper-extractor` | agent (Sonnet) | Download 3–5 papers into the library and append targeted notes |
| `agents/code-simplifier` | agent (Sonnet) | Behaviour-preserving tidy-up and packaging of Python code |
| `hooks/post_edit.py` | hook | After each Edit/Write: markdown check on `.md`, black on `.py`, only where opted in |
| `templates/CLAUDE.md` | template | Starting point for a new project's `CLAUDE.md` |

Skills are loaded on demand: only their one-line descriptions are always in context. Agents run in their own context with their own model. The hook is the only piece that is enforced mechanically.

## Install

```
~/Science/claude-research-kit/install.sh
```

It links `~/.claude/skills/<name>` and `~/.claude/agents/<name>.md` to this repository and registers the hook in `~/.claude/settings.json` (other settings are kept). Rerunning it is harmless; run it again after adding a skill or agent.

## Using it in a project

Copy `templates/CLAUDE.md` into the project root and edit it. The essential lines say where notes and code go and name the skills the project uses. Naming them makes their use reliable (skills otherwise trigger only from their descriptions) and opts the project into the hook:

- `.md` files are checked if the nearest `CLAUDE.md` above them mentions `markdown-style`; errors are reported back to Claude;
- `.py` files are formatted with black if it mentions `python-style`.

A directory with its own `CLAUDE.md` is a project root (skill `project-layout`): Claude may work anywhere below it, never above.

## Paper library

Downloaded papers live in `~/Science/papers/` (`LABEL/LABEL.pdf`, arXiv source, `notes.md`; index `INDEX.tsv`), shared by all projects. See skill `research-writing`.

## Changing the kit

Edit the files here. Project-specific deviations belong in the project's `CLAUDE.md`, not in forked copies of a skill.
