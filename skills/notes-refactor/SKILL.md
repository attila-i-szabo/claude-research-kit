---
name: notes-refactor
description: Reorganising an existing collection of research notes — splitting, merging, moving or renumbering files, separating tangled strands (general methods, general theory, model-specific work, dead ends) into the right notes directories, creating new directories or a museum of dead ends, bringing files back within their word budget — planned in plan mode, executed with snapshot, mapping table, optional rewriter agents and mechanical checks. Use whenever the user asks to refactor, reorganise, untangle, clean up or restructure notes, or to port a notes repository to the project-layout format (then also read first-port.md in this skill's directory).
---

# Refactoring a notes collection

Notes accumulate one request at a time, so every few weeks a collection needs a global pass:
strands get tangled, files outgrow their budget, numbering and cross-references drift. This
skill makes that pass routine. It builds on skill `project-layout` (directories, labels,
cross-references, READMEs, the museum), `research-writing` (state not history, budgets, agent
hygiene) and `markdown-style`. **If the notes do not yet follow `project-layout` at all, read
`first-port.md` in this directory as well.**

Scripts in this directory (`K=~/.claude/skills/notes-refactor`; stdlib only; `--help` for details):

- `inventory.py ROOT [PATH ...]`: per file the H1, every heading with its word count, the total
    (references excluded, over-budget flag), the files it cites and how often it is cited.
- `xref_check.py ROOT [--incoming FILE ...]`: resolves every ``File `X` `` below the root, in notes
    and code, and checks the cited §, Table and Fig.; `--incoming` lists every citation of the given
    files.
- `content_loss.py SNAPSHOT NEW [FILE ...]`: paragraphs of the old notes not found in the new tree.
- `refcheck.py FILE ... [--fix --pool DIR]`: cited labels against reference lists; rebuilds lists.

## 1. Scope and autonomy

Refactors are **planned in plan mode**; the approved plan is the user check that `project-layout`
requires before weight shifts and new files. Two classes:

- **Local**: split, merge or move sections between existing files, renumber within existing
    directories, trim duplicates, move material to an existing museum. Plan the whole thing without
    asking.
- **Structural**: new directories, a new museum, moves across directories. Still plan without
    prompting: propose each new directory with a name and a one-sentence purpose. Ask
    (AskUserQuestion) only about classifications that are genuinely the user's call — a file that
    is half dead end and half reusable result, whether to keep a transcript, whether to commit
    first — with a recommended option.

**Structure given in the prompt is adopted as given** (directory names, which file goes where,
what counts as a dead end). If it conflicts with `project-layout` or with what the inventory
shows, follow it anyway and flag the conflict in the plan with the reason. Within the given frame,
fill in the rest yourself.

## 2. Inventory (plan mode)

1. Run `python3 $K/inventory.py ROOT` (and on code directories with `xref_check.py --incoming` for
    the files likely to move). This gives the section map, sizes and the citation graph without
    reading files whole.
2. Read the READMEs, then sections only where the heading does not settle the classification.
    Prefer `awk '/^## 3\./,/^## 4\./' FILE` over reading whole files.
3. **When the affected notes exceed about 20k words, delegate the reading** to at most 3 Explore
    agents, each owning a disjoint set of files. Brief: for each section return one table row —
    file, §, words, strand (Section 3), one-line content, which other sections it depends on or
    duplicates. No prose, at most about 60 rows per agent. Keep only the tables in context.

## 3. Classification

Assign every section (not every file) one strand:

| strand | goes to |
|---|---|
| model-independent method (numerics, statistics, data analysis) | a method directory, e.g. `monte-carlo/` |
| general theory of a phenomenon (universality, scaling, estimators) | a theory directory, e.g. `bkt-clock/` |
| adaptation of a general method to one model | the model's directory, citing the general file |
| result for one model | the model's directory |
| literature review | stays with its topic; generic derivations inside it may move, leaving a summary and a pointer |
| dead end (tested or worked out, fails or abandoned) | `museum/` (skill `project-layout`, "Museum") |
| duplicate | merged into the most general location; the specific file keeps a pointer plus its own numbers |

Rules that recur:

- Text that uses a model only as an example belongs to the general file, **generalised in
    notation** (e.g. $p$ instead of $6$), with the model's numbers kept as labelled examples or moved
    back to the model file.
- A file that is half dead end is split: reusable results to the main line, the rest to the museum
    with a "Why this is in the museum" lead.
- A dead end that is one paragraph inside a sound argument (e.g. "the Binder cumulant fails here")
    stays in place; it only gets a row in the museum's warnings table.
- New directories need at least two files or a clear growth path; otherwise put the file in the
    nearest existing directory.
- Aim for files of 1.5–4k words with one focus each (`research-writing` budgets).

## 4. The plan file

It must contain, concisely:

1. **Context**: what is tangled and the intended outcome.
2. **Target tree**: per new or changed file its path, H1, numbered sections with their sources
    (old file and §) and an estimated word count (all ≤ 4k).
3. **Section mapping table**: old (file, §, Table, Fig.) → new (file, §, Table, Fig.). This is the
    single artifact all cross-reference updates are derived from; it must be complete before any
    writing starts, so that files written in parallel can cite each other.
4. **Citing files outside the moved set** (from `xref_check.py --incoming`): other notes, code
    docstrings, the code README, `CLAUDE.md`.
5. **Museum entries**: per dead end, why it fails, what replaces it, where the pointer goes.
6. README changes (each changed directory, its parent, the code README) and the commit plan
    (the project's git rules decide branch and push).
7. Verification (Section 8).

## 5. Execution

1. **Clean start.** Commit or confirm the working tree as the project's rules say, so the refactor
    is one reviewable commit.
2. **Snapshot** the notes tree to the scratchpad (`cp -r notes SCRATCH/old/`). Sources are read
    from the snapshot from now on; the tree itself changes underneath.
3. **Whole-file moves with `git mv`**, so history follows. When renumbering would land on an
    existing number, move to a temporary name first. Files that are dissolved are `git rm`ed after
    their content is placed.
4. **Write the new files** (Section 6), at top level or by agents (Section 7).
5. **Apply the mapping table** to every citing file, including references that still *resolve* but
    now point at renumbered content — the checker cannot see those. Use small Python scripts with
    `assert old in text` per replacement rather than `sed` on LaTeX-laden lines.
6. **Reference lists**: `refcheck.py FILES --fix --pool SCRATCH/old` rebuilds each list from its
    citations.
7. **READMEs last**: each changed directory, then its parent, then the code README; descriptions
    must match the files as they now are (`project-layout`).
8. **Checks** (Section 8), then commit with a message listing the moves.

## 6. Writing rules for moved text

- **Move, do not rewrite.** Text stays verbatim except: cross-references, the notation
    introduction a new file needs, generalisation the target demands, and "state not history"
    fixes. Errors found on the way are corrected in place and mentioned in the chat, not in the
    notes.
- Each new file: H1 `# LABEL — Title`; **Scope** saying what the file covers and where its siblings
    are; numbered sections; **Problems that need further work**; **References**.
- Keep section numbers of moved files stable where others cite them: replace a removed section by
    a short section that summarises and points to the new location, rather than renumbering.
- Tables and figures renumber per file; every citing "Table n" goes into the mapping table.
- Open problems move to where the work lives; a general problem appears once, specific files point
    to it.
- Cross-directory ranges are written in full: Files `../a/01`–`../a/03`, never `../a/01`–`03`.
- Main-line files get a one-line pointer to the museum wherever a removed dead end would otherwise
    be tempting (e.g. "single-temperature ladders fail; evidence in File `../museum/03`, §3").

## 7. Rewriter agents

Use the `notes-rewriter` agent (Opus) when **4 or more files** are written or substantially
rewritten, or **more than about 15k words** move; below that, the top-level context is cheaper
than the briefs. Run at most 3–4 at a time. The top level keeps: the plan and mapping table, all
`git mv`, edits to files outside the agents' targets, the reference pool, READMEs, checks and the
commit. One agent per target file; two agents never write the same file.

Brief template (each brief is self-contained; the agent sees nothing else):

```
Target: notes/<dir>/NN-slug.md, H1 "# notes/<dir>/NN — <Title>".
Project root: <ROOT>. Snapshot of the old notes (read sources here): <SCRATCH>/old/notes.
Read first: ~/.claude/skills/research-writing/SKILL.md, markdown-style/SKILL.md,
  project-layout/SKILL.md (labels, cross-references, museum), notes-refactor/SKILL.md §6.
Outline (sections, sources, target words):
  Scope — new: <what to say, siblings to name>
  1. <title> — <old path> "## 3." whole; drop the last paragraph (now in <file>)
  2. <title> — <old path> "## 6." first half, generalised to p (keep p = 6 values as examples)
  ...
  Problems — <which old items>; References — rebuilt from citations.
Notation: <symbols and their definitions, consistent across the new files>.
Mapping table (excerpt: every section this file cites or is cited by): <rows>.
Do not edit any other file. Run check_markdown.py and refcheck.py on the target.
Reply (≤ 150 words): path, word count, cross-references emitted (target, §), open issues.
```

After the agents return: apply the mapping table to all other files, then run all checks; read
one or two agent-written files in full to spot drift from the brief.

## 8. Verification

- `python3 $K/xref_check.py ROOT`: 0 failures.
- `python3 $K/content_loss.py SCRATCH/old/notes notes`: every reported paragraph is a deliberate
    change (rewritten scope, generalisation, deduplication, removed stray text); report removals in
    the chat.
- `python3 $K/refcheck.py` on every changed file: nothing missing (pre-existing unused labels may be
    left, but say so).
- `check_markdown.py` on all changed `.md` (skill `markdown-style`); `inventory.py --no-sections` for
    the word budget; figure links resolve from each file's new depth; `python3 -m py_compile` on
    code whose docstrings changed.

## 9. Pitfalls

- A reference to a renumbered file or section that still resolves is silently wrong; only the
    mapping table catches it, so grep every old label (`File \`06\``, `honeycomb/06`) in notes *and*
    code.
- `git mv` onto an existing number fails or, worse, the Write of a new file clobbers a moved one;
    order the moves and use temporary names.
- Tables renumbered in one file but cited by their old number elsewhere.
- Relative figure paths change depth when a file moves into or out of a nested directory.
- Splitting a section can orphan a definition; every new file introduces its notation or cites
    where it is defined.
- Stray duplicated paragraphs show up in the content-loss report; delete them rather than carry
    them over.
