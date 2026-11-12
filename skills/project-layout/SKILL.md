---
name: project-layout
description: Directory management for research projects with Markdown notes and code — the project root, numbered notes files, nested notes directories, README.md files for notes and code, cross-reference format, when to split or merge files and directories, renumbering hygiene, the museum of dead ends. Use whenever creating, renaming, splitting or reorganising notes files or directories, writing a README, or citing another notes file.
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

Several files may be cited together as "Files `03`–`05`" or "Files `03` and `07`"; in another directory every end of a range carries the full path, "Files `../bar/01`–`../bar/03`". Cross-references never go above the root. They are mechanically checkable: the path plus the number must match exactly one `NN-*.md` file (`xref_check.py` of skill `notes-refactor` checks them, with the cited §, Table and Fig.).

## README.md of a notes directory

`README.md` keeps the **current state of the directory and its files.** It must only represent the current state: no history of how the content developed.

- It starts with an **overview of the topic**, explaining what the directory is for and how the files compose into the whole.
- Next, an **H2 heading for each file**, each containing:
    - heading: number (two digits) and title;
    - name of the detailed file;
    - one-sentence summary;
    - high-level table of contents, each item with a statement of progress of **at most about 50 words**;
    - any outstanding problems, **especially ones that require the user's attention** before work can proceed. Distinguish clearly between "needs a future Claude session to grind through a derivation/literature search" and "needs the user's physics judgment or a decision only they can make."
- Next an **H2 heading for each nested notes directory**, each containing:
    - heading: name of the directory;
    - one-sentence summary;
    - summary of main learning outcomes, not broken down by file, **bullet points of at most 50 words**;
    - most important outstanding problems, as above.
- Next, an **H2 heading for each code directory inside this notes directory** (its own `code/`, see above), each containing:
    - heading: name of the directory plus "(code)";
    - a list of the **most important code files**, each with the filename and a **description of at most 50 words.**
        - Ignore helper scripts and other stuff that is unlikely to be used further away from this folder.
    - Code elsewhere in the root (e.g. a project-level `code/` beside `notes/`) gets no H2 here: it is documented by its own README only.
- **At the end of each pass, check that the descriptions of every file you changed match what the file now contains. If the pass fundamentally changes the contribution of this directory, propagate it into the description of the directory in its parent, recursively if needed.**

## Detailed files: focus, splitting and merging

**Each distinct topic gets its own numbered `.md` file**, containing that topic worked out in detail.

- **Each file has one clear focus.** If a file covers several things that do not work towards the same goal, split it. If one file becomes a small subsidiary of another, merge it in.
- **Weight shifts:** you may start new files or rearrange sections only after checking the change with the user. A refactor planned in plan mode with skill `notes-refactor` counts as checked once the plan is approved.
- A file that outgrows its word budget (skill `research-writing`) is a candidate for splitting; propose the split to the user.
- **Directories.** When a notes directory accumulates several groups of files that each work towards a separate goal, propose to the user moving a group into a nested notes directory (within the allowed depth). Ask before creating a new directory when its topic overlaps strongly with an existing one; recommend adding to the existing one.
- **Renumbering and moving.** When you rearrange, renumber or move files, update every citation (grep the root for the old label and for relative paths that resolved to it) and **do not leave pointers behind** to the old location. Pointers to the museum (below) are not such leftovers: they warn against a dead end, they do not redirect to moved content.
- **Large reorganisations** (several files, new directories, separating general methods from model-specific work, first port of legacy notes): follow skill `notes-refactor`.

## Museum of dead ends

Approaches that were worked out or tested and fail, or were abandoned for a reason worth remembering, go to a notes directory `museum/` instead of being deleted or left in the main line. It is a warning collection: consult it before reviving an idea.

- **What qualifies.** A method, observable, estimator, ansatz or derivation route with evidence that it fails or is not worth pursuing here: a test, a counterexample, a cost estimate, an exact result showing it cannot work. Plain mistakes do not qualify; they are corrected in place (skill `research-writing`, "State, not history"). A museum file is a standalone analysis of why the approach fails, not a record of how the notes developed.
- **Place.** `museum/` is an ordinary notes directory (numbered files, README), a sibling of the topic directories, normally directly under the top notes directory; it counts toward the nesting depth. One museum per project unless `CLAUDE.md` says otherwise. Source material behind an entry (a chat transcript, a scratch derivation) may sit beside it as an unnumbered file cited from the entry.
- **Each file** opens its Scope with a paragraph **"Why this is in the museum"**: what was hoped, why it fails, what replaces it and where. The rest keeps the usual structure; Problems lists only what would be needed if the approach were revived.
- **README.** After the overview, a **Warnings** table with one row per dead end: dead end | why it fails | replaced by | where. It also lists short warnings that live inside main-line files (a paragraph showing that an observable fails, say), pointing to them, so the table is the complete list. Then the usual H2 per file.
- **Pointers from the main line.** Wherever a main-line file would otherwise tempt a reader into a dead end, it carries one sentence and a cross-reference to the museum entry ("single-temperature ladders fail at low $T$; File `../museum/03`, §3").
- **Discoverability.** The project's `CLAUDE.md` has one line naming `museum/` and asking to read its warnings table before proposing a method, observable or estimator. New dead ends are added (file or table row), not deleted.

## README.md of a code directory

Every `code/` directory with more than one script has a `README.md`. A worked example is in `code-readme-example.md` in this skill's directory; read it the first time you write a code README in a session.

### Division of labour with the notes

- The **notes** say *what* is computed and *why*: the physics, the formulas, the derivations.
- The **README** says *how* the code computes it: data layout, index orderings and sign conventions the code relies on, array shapes, file formats, numerical and performance design, pitfalls.
- A formula appears in the README only to fix a convention the code depends on (e.g. the sign of the Hamiltonian). Anything that needs a derivation goes into the notes and is cited by cross-reference (File `../notes/04`, §3).
- Do not describe the code in a separate notes directory: numbered notes files carry literature checks, references and open problems that do not fit a code description, and a description away from the code drifts.

### Structure

1. **H1** `# <Role> code (`code/`)`, then an **overview** of at most about 200 words:
    - what the directory computes, and the pipeline (which modules feed which);
    - **how to run the scripts**, said once: working directory and where outputs go (e.g. "run from `code/`; outputs go to `data/`, which is gitignored");
    - the dependencies and the installable package, if any;
    - pointers to the READMEs of subdirectories (e.g. `aux/README.md`).
2. Optional `## Conventions`, only for conventions shared by two or more files: lattice embeddings and geometry, index orderings, units, sign conventions, file formats.
3. **One H2 per group of files that share a method** (e.g. "Luttinger-Tisza and order by disorder", "Parallel-tempering Monte Carlo"), ordered from library modules to the scripts that use them. If the files have no natural grouping, use a single `## Modules`. A group opens with an **approach** paragraph or a short numbered pipeline, at most about 300 words, citing the notes for derivations. It also holds what the members share: a common calling-sequence block, a config schema, an output-naming rule.
4. **One H3 per file**, its heading the filename in backticks, ordered within the group from library modules to scripts.

**Say everything once, at the highest level it applies to.** A file section contains only what is specific to that file. For a script analogous to another, say so explicitly and list only the differences: "As `honey_MC.py`, except: …". Each file section is at most about 250 words, code blocks excluded; longer explanations are derivations and belong in the notes.

### Content of a file section

- It **opens with a paragraph**:
    - purpose;
    - which notes it implements, by cross-reference (File `../notes/09`, §2);
    - heavy dependencies and import side effects (e.g. "requires JAX, enables 64-bit precision on import"; "numpy only, so it runs without JAX");
    - which other modules use it.
- **Library modules.**
    - One bullet per public function or class: what it returns or does, key design facts (cost, jit or pytree status, drop-in replacements) and caveats.
    - Then `Usage:` and a code block of representative calls, with short trailing comments.
    - Then one bullet per constructor or configuration parameter, as `` `name` (default x): meaning ``.
- **Scripts.**
    - `Calling sequence:` and a code block (`python script.py [--opt] [arg ...]`, from the working directory given in the overview).
    - Then one bullet per argument or option, with its default and effect.
    - **Config file** (for scripts that take a JSON, YAML or TOML file as an argument):
        - a pointer to the checked-in example config;
        - one bullet per field, as `` `name` (required) `` or `` `name` (default x) ``, then its meaning, units and allowed values;
        - alternative or conflicting fields and which one wins, with any warning raised;
        - fields only some scripts accept ("`honey_MC.py` only");
        - any resolved config the script writes back, and how output names are derived.

        When several scripts share a schema, it is given once in the group section, and each file section lists only its deviations.
    - **Outputs:** files written, as paths with placeholders like `{L}`, then the printed diagnostics, one bullet each.
- Optional **Design notes:** invariants and pitfalls that someone editing the file must know (e.g. "a spin anti-aligns with its local field, so the von Mises location is the field angle plus π; getting this backwards does not crash but samples the wrong states").

### Maintenance

- Update the README **in the same pass** as any change to a module's interface or a script's command line or config schema.
- **Check every calling sequence against the script's argument handling** (run `--help`, or read the argument parser) whenever you touch the script or its section.
- Describe the current behaviour only. Data-format compatibility (e.g. "ZQ14 if the key is absent, as in older files") is stated as a fact about the files, not as history; phrases like "as before" or "verified during development" are history.
- **Formulas use LaTeX**, following skill `markdown-style`, including its exceptions for code READMEs (plain Unicode for single Greek letters, plain text for formulas such as V(k) that read unambiguously without rendering). Code identifiers are in backticks, never in math.
