---
name: project-layout
description: Directory management for research projects with Markdown notes and code — the project root, numbered notes files, nested notes directories, README.md files for notes and code, cross-reference format, when to split or merge files and directories, renumbering hygiene. Use whenever creating, renaming, splitting or reorganising notes files or directories, writing a README, or citing another notes file.
---

# Project layout

The project's `CLAUDE.md` says where notes, code and figures go, and how deeply notes directories may nest (default: 1 level, i.e. no subdirectories of numbered files inside a notes directory). Where it says nothing, use the defaults below.

## Root

- The **root** of a project is the nearest ancestor directory (of the working directory, or of the file being edited) that contains a `CLAUDE.md`. A directory with its own `CLAUDE.md` is a root even if an ancestor also has one.
- You may walk up to the root to resolve cross-references, and you may read and edit anything below the root, even when the session was started in a subdirectory. **Never go above the root.** If the session's permissions block an edit below the root, ask the user to run `/add-dir ROOT`.
- The shared paper library (skill `research-writing`) is outside every root and is the one exception.

## Notes directories

A **notes directory** holds `README.md` plus numbered files `01-short-summary.md`, `02-...md`, ... Numbering is sequential, two digits, starting fresh in every directory. A single-file topic is still `01-...md` plus `README.md`.

- If needed, a notes directory also has its own `code/` and `figures/`. Scripts in `code/` generate the figures in `figures/`.
- Notes directories may nest, up to the depth allowed by `CLAUDE.md`. Each nested notes directory is a full notes directory, with its own README and numbering. A directory used only for grouping (it has no numbered files of its own) still has a README, listing its subdirectories with one sentence each.
- When adding a file, append it with the next free number and update the directory's `README.md`.
- **Each file's H1 states its own label and a descriptive title**: `# LABEL — Title`. The label is the file's path relative to the root, with the slug and `.md` dropped, e.g. `notes/03` or `foo/bar/03`.

## Cross-references

A cross-reference is the **relative path from the citing file's directory to the cited file, ending at the file number**, in backticks, after the word "File":

- same directory: "File `03`, §2.1";
- sibling directory: "File `../bar/01`";
- further away: "File `../../foo/bar/01`";
- from `code/` (docstrings, code README) to the notes beside it: "File `../07`, §2.2".

Several files may be cited together as "Files `03`–`05`" or "Files `03` and `07`". Cross-references never go above the root. They are mechanically checkable: the path plus the number must match exactly one `NN-*.md` file.

## README.md of a notes directory

`README.md` keeps the **current state of the directory and its files.** It must only represent the current state: no history of how the content developed.

- It starts with an **overview of the topic**, explaining what the directory is for and how the files compose into the whole.
- Next, an **H2 heading for each file**, each containing:
    - number (two digits) and title;
    - name of the detailed file;
    - one-sentence summary;
    - high-level table of contents, each item with a statement of progress of **at most about 50 words**;
    - any outstanding problems, **especially ones that require the user's attention** before work can proceed. Distinguish clearly between "needs a future Claude session to grind through a derivation/literature search" and "needs the user's physics judgment or a decision only they can make."
- It lists nested notes directories and `code/` with one sentence each.
- **At the end of each pass, check that the descriptions of every file you changed match what the file now contains.**

## Detailed files: focus, splitting and merging

**Each distinct topic gets its own numbered `.md` file**, containing that topic worked out in detail.

- **Each file has one clear focus.** If a file covers several things that do not work towards the same goal, split it. If one file becomes a small subsidiary of another, merge it in.
- **Weight shifts:** you may start new files or rearrange sections only after checking the change with the user.
- A file that outgrows its word budget (skill `research-writing`) is a candidate for splitting; propose the split to the user.
- **Directories.** When a notes directory accumulates several groups of files that each work towards a separate goal, propose to the user moving a group into a nested notes directory (within the allowed depth). Ask before creating a new directory when its topic overlaps strongly with an existing one; recommend adding to the existing one.
- **Renumbering and moving.** When you rearrange, renumber or move files, update every citation (grep the root for the old label and for relative paths that resolved to it) and **do not leave pointers behind** to the old location.

## code/README.md

Every `code/` directory with more than one script has a `README.md`, updated in the same pass as any change to a module's interface or a script's command line. It describes the current behaviour only. Data-format compatibility (e.g. "ZQ14 if the key is absent, as in older files") is stated as a fact about the files, not as history. A worked example is in `code-readme-example.md` in this skill's directory; read it the first time you write a code README in a session.

- **H1** `# <Role> code (`code/`)`, followed by pointers to the READMEs of subdirectories (e.g. auxiliary scripts in `aux/README.md`).
- `## Modules`, then one `### `file.py`` section per module or script, ordered from library modules to the scripts and plotting scripts that use them.
- Each section **opens with a paragraph**:
    - purpose;
    - which notes it implements, by cross-reference (File `../09`, §2);
    - heavy dependencies and import side effects (e.g. "requires JAX, enables 64-bit precision on import"; "numpy only, so it runs without JAX");
    - which other modules use it.
- **Library modules.**
    - One bullet per public function or class: what it returns or does, key design facts (cost, jit or pytree status, drop-in replacements) and caveats.
    - Then `Usage:` and a code block of representative calls, with short trailing comments.
    - Then one bullet per constructor or configuration parameter, as `` `name` (default x): meaning ``.
- **Scripts.**
    - `Calling sequence:` and a code block (`python code/script.py [--opt] [arg ...]`).
    - Then one bullet per argument or option, with its default and effect.
    - Say where outputs are written, as paths with placeholders like `{L}`.
- **Formulas use LaTeX**, as in all other Markdown, and follow skill `markdown-style` (e.g. $\chi_F = X_F/L^2$, $\vert\Phi\vert^{2K}$). Never ASCII math like `L^2` or `|Phi|^(2K)`.
