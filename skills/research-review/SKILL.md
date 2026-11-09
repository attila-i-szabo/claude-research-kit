---
name: research-review
description: Pipeline for writing a physics literature review in Markdown — triage with the lit-searcher agent, extraction with the paper-extractor agent, writing in the main session with evidence ledgers and verdicts. Use when asked to review, survey, compare or assess the literature on a topic. Builds on research-writing.
---

# Literature reviews

Follow skill `research-writing` (standards, budgets, reading rules, paper library), skill `project-layout` (where files go, README, cross-references) and skill `markdown-style`. This skill adds the pipeline.

## Before starting

- Fix the budgets of `research-writing` (files, words per file, full reads per file) from the scope of the request, and decide the file split. If the request will not fit the budgets, propose a split to the user before searching.
- Check whether an existing notes directory of the same root already covers the topic (skill `project-layout`).

## Pipeline

1. **Triage: one `lit-searcher` agent per review** (Sonnet).
    - The brief gives the topic, the planned files with one line on the scope of each, the library path, and the path to write the shortlist to.
    - It returns a **deduplicated shortlist** with label, arXiv ID, title, a one-line summary of the abstract, the owning file, and whether the paper is *core* (needs reading beyond the abstract). **Every paper has exactly one owning file**, so agents never read the same paper twice.
    - **Flag paywalled core papers** to the user immediately.
2. **Extraction: `paper-extractor` agents** (Sonnet), **3–5 core papers per agent**, at most 3–4 agents at a time.
    - The brief gives the review directory, the question the notes serve, the library path, and for each paper its label, arXiv ID and the specific claims or numbers to look for.
    - Each agent downloads missing papers, reads only targeted parts, appends one note per paper to `LIBRARY/LABEL/notes.md` immediately after reading it, and returns only the paths.
3. **Writing: Opus, in the main session or one fresh agent per file.**
    - Work from the shortlist and the notes, never from raw TeX dumps.
    - Before stating them, **re-check the 3–5 most contested or surprising claims directly in the source**.
    - State what each paper actually shows; tag abstract-only claims as such.

## Style of a review

- **Prefer tables, evidence ledgers and short verdicts over per-paper prose.** An evidence ledger is a table with one row per result: paper label, method, system and sizes, the number or claim, and caveats.
- Where papers disagree, give each side's claim with its label, say what would decide between them, and give a verdict with its confidence (or say it is open).
- **Unify notation and terminology** across the papers covered (skill `research-writing`, "At least as clear as the source"). Say where a paper's definition differs from the one used here and how its numbers translate.
- Derivations that a reader needs in order to judge a claim are reproduced, to the standards of `research-writing`.
- The reference list stays complete: every paper on the shortlist that the text relies on is listed, core or peripheral.
