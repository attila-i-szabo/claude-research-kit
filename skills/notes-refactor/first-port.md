# First port of a notes repository to the project-layout format

Read this together with `SKILL.md` when the notes predate the research kit: unnumbered or
freely named files, no READMEs or ones that tell a history, references like "see the MBAR
note" or "above", papers stored inside the project, failed attempts mixed into the main line.
The procedure is the same — plan mode, inventory, classification, mapping table, snapshot,
moves, checks — with the additions below. The repository-level steps (root `CLAUDE.md`, paper
library, code README, black) are in the kit README, "Porting an existing project"; do them in
the same plan.

## Inventory

- Inventory by Explore agents by default (Section 2 of `SKILL.md`): legacy notes rarely have
    headings that classify their sections reliably.
- Also list every file that is not a notes file proper: chat transcripts, scratch notes, to-do
    lists, instruction files given to earlier sessions, figures, data, PDFs.

## Plan additions

1. **Root and directories.** One `CLAUDE.md` at the project root (merge nested ones). Propose notes
    directories by topic within the nesting depth the project allows, plus the method and theory
    directories the classification suggests, plus `museum/`. Shared tools may stay in `notes/`
    itself.
2. **Numbering.** Order files within each directory so that later files build on earlier ones,
    then number `01`, `02`, ... Give every file the H1 `# LABEL — Title`.
3. **Mapping table from informal references.** Collect every free-form reference — "the MBAR
    note", "see above", "eq. (12) of the old notes", line numbers in code — and map each to
    `File \`NN\`, §x.y`. Code citations by line number become function or array names.
4. **Required sections.** Each file gets Scope, Problems that need further work, References
    (skill `research-writing`). Do not invent content to fill them: missing derivations,
    unverified claims and missing references become items under Problems.
5. **State, not history.** Remove revision narratives ("in the previous pass", "retracted",
    struck-through text) from the main line. A superseded *argument* that is still a useful
    warning goes to the museum as a standalone analysis; a superseded *mistake* is just corrected.
6. **Museum, set up now.** Create `museum/` with its README and warnings table even if it starts
    short (skill `project-layout`, "Museum"). Triage failed or abandoned approaches into it
    instead of deleting them, each with "why it fails" and "replaced by"; add main-line pointers
    and the `CLAUDE.md` line. Chat transcripts or scratch notes that are the source of a museum
    entry go beside it as unnumbered files cited from it; other such files are listed for the user
    to keep or delete, never deleted without asking.
7. **Instruction files** addressed to earlier sessions (task lists, prompts saved as Markdown) are
    not notes: list them in the plan for the user to delete or move out of `notes/`.
8. **Papers** to the shared library with symbolic links (kit README); citations become labels with
    a reference list per file.
9. **READMEs from scratch** for every notes directory and the code directory, to the structure of
    `project-layout`.

## Checks

As in `SKILL.md`, Section 8, plus: no file without H1 label, Scope, Problems and References; no
reference left in free form (grep for "see the", "above", "below", "note on", "eq."); every
directory has a README. Expect the content-loss report to be long; go through it once and list
the deliberate removals in the chat.
