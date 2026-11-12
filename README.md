# Claude research kit

Skills, agents and hooks for writing physics literature reviews, research notes and research code with Claude Code, to the same standards in every project. This repository is the single source of truth: `install.sh` symlinks its pieces into `~/.claude/`, so an edit here takes effect in every project immediately, in new sessions.

## Contents

| Piece | Kind | Purpose |
|---|---|---|
| `skills/research-writing` | skill | Shared standards: audience, rigour, citations, references, state not history, budgets, agent hygiene, reading rules, paper library |
| `skills/research-review` | skill | Literature-review pipeline: triage → extraction → writing; evidence ledgers |
| `skills/research-notes` | skill | Notes with new results: required literature checks, derivations, notes about code and runs |
| `skills/project-layout` | skill | Project root, numbered notes files, nested notes directories, READMEs (notes and code), cross-references, splitting and merging, museum of dead ends |
| `skills/notes-refactor` | skill + scripts | Plan-mode procedure for reorganising a notes collection (inventory, classification, mapping table, moves, checks); `first-port.md` for legacy notes; `inventory.py`, `xref_check.py`, `content_loss.py`, `refcheck.py` |
| `skills/markdown-style` | skill + script | Markdown/LaTeX house style and `check_markdown.py` |
| `skills/python-style` | skill | Light and production Python style, packaging and maintainability |
| `agents/lit-searcher` | agent (Sonnet) | Literature search: shortlist for a review, or prior-work check for notes |
| `agents/paper-extractor` | agent (Sonnet) | Download 3–5 papers into the library and append targeted notes |
| `agents/notes-rewriter` | agent (Opus) | Write or rewrite one notes file of a refactor from a brief (sources in a snapshot, mapping-table excerpt) |
| `agents/code-simplifier` | agent (Sonnet) | Behaviour-preserving tidy-up and packaging of Python code |
| `hooks/post_edit.py` | hook | After each Edit/Write: markdown check on `.md`, black on `.py`, only where opted in |
| `templates/CLAUDE.md` | template | Starting point for a new project's `CLAUDE.md` |
| `user/CLAUDE.md` | profile | The user's "About me" profile, linked to `~/.claude/CLAUDE.md`; skill `research-writing` takes the audience from it |

Skills are loaded on demand: only their one-line descriptions are always in context. Agents run in their own context with their own model. The hook is the only piece that is enforced mechanically.

## Install

```
~/Science/claude-research-kit/install.sh
```

It links `~/.claude/skills/<name>`, `~/.claude/agents/<name>.md` and `~/.claude/CLAUDE.md` (the profile, skipped if a regular file is already there) to this repository and registers the hook in `~/.claude/settings.json` (other settings are kept). Rerunning it is harmless; run it again after adding a skill or agent.

## Using it in a project

Copy `templates/CLAUDE.md` into the project root and edit it. The essential lines say where notes and code go and name the skills the project uses. Naming them makes their use reliable (skills otherwise trigger only from their descriptions) and opts the project into the hook:

- `.md` files are checked if the nearest `CLAUDE.md` above them mentions `markdown-style`; errors are reported back to Claude;
- `.py` files are formatted with black if it mentions `python-style`.

A directory with its own `CLAUDE.md` is a project root (skill `project-layout`): Claude may work anywhere below it, never above.

## Porting an existing project

For a project that predates the kit (for the notes themselves, follow skill `notes-refactor` with its `first-port.md`, which plans these steps together):

1. **One `CLAUDE.md` at the root.** Merge every nested `CLAUDE.md` (e.g. `notes/CLAUDE.md`) into the root one, keeping only true project overrides. A nested one makes its directory a separate root, which breaks cross-references and the hook's opt-in. Drop rules the skills already state.
2. **Rewrite the root `CLAUDE.md` from the template**: name the skills, declare the Python tier, and state any non-default working directory or figure location.
3. **Papers into the library.** Move each paper to `~/Science/papers/LABEL/LABEL.pdf`, extract any source tarballs there (extract only), append a line to `INDEX.tsv`, and replace the project copy with a symlink (`ln -s ~/Science/papers/LABEL notes/papers/LABEL`). Check for label collisions first.
4. **Labels and cross-references.** Give each notes file the H1 `# LABEL — Title` and rewrite references to other files as File `NN`, §x.y (skill `project-layout`). Replace citations of code by line number with the names of functions or arrays.
5. **Code.** Before refactoring, record the outputs of every script on small inputs; afterwards, compare them exactly. Run black once over the whole code directory, so that the hook does not reformat files piecemeal later.
6. **Code README** to the structure of `project-layout`, with calling sequences checked against the scripts.
7. **Museum.** Create `notes/museum/` for failed or abandoned approaches (skill `project-layout`) and name it in `CLAUDE.md`.
8. **Check:** run `check_markdown.py` on every Markdown file and `xref_check.py` (skill `notes-refactor`) for the cross-references.

## Paper library

Downloaded papers live in `~/Science/papers/` (`LABEL/LABEL.pdf`, arXiv source, `notes.md`; index `INDEX.tsv`), shared by all projects. See skill `research-writing`.

## Changing the kit

Edit the files here. Project-specific deviations belong in the project's `CLAUDE.md`, not in forked copies of a skill.
