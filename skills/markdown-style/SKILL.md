---
name: markdown-style
description: House style for Markdown with LaTeX math, tuned to the user's Markdown editor/renderer — spacing commands, display blocks, \boxed, < and > spacing, | in tables, backticks in math, list indentation — plus a checker script. Use whenever creating or editing a .md file that contains math, tables or lists in a project that uses this style.
---

# Markdown and LaTeX house style

**These rules are checked on every pass. Before finishing, run the checker on every file you created or edited and fix all violations.**

```
python3 ~/.claude/skills/markdown-style/check_markdown.py FILE_OR_DIR ...
```

It prints `FILE:LINE: [Rn] message` for each violation and exits 1 if there are errors. Cases that need judgement are printed as warnings (`[R1?]`). In projects that opt in (their `CLAUDE.md` names `markdown-style`), a hook runs the checker after every edit of a `.md` file and reports errors back.

## Rules

1. **Keep LaTeX simple.** **Never** use the spacing commands `\,` `\;` `\:` `\!` `\quad` `\qquad` `\hspace`, row options like `\\[2pt]`, or `\phantom`: not around equals signs, operators or relations, not to separate a formula from a side condition, not to pad the inside of `\boxed{...}`. Write `E = svk`, never `E \;=\; s\,v\,k`. LaTeX's own spacing is correct.
    - **Exception 1:** `\,` between the differentials and the integrand of an integral, adjacent to a `d`- or `D`-differential: $\int dx\,dy\,f(x,y)$, $\int D\bar\psi\,D\psi\,e^{-S}$. Covers only `\,` and only in that position.
    - **Exception 2:** `\quad` separating several **short** equations on the same line, or a short condition like `(n \in \mathbb{Z})` from the equation it refers to. If the equations are long, put them on separate lines with `\\`.
2. **Long formulas go on separate lines**, not inline.
3. **One long formula per line.** Never put two long formulas on a line separated by `\qquad`. Split them with `\\` inside one `$$` block:
    ```
    $$
    \tau_{\rm m} = \frac{d+iv\beta}{L},
    \\
    q = e^{2\pi i\tau_{\rm m}},
    \\
    |q| = e^{-2\pi v\beta/L} < 1.
    $$
    ```
    Put `\\` on a line of its own. Never leave a blank line inside a `$$` block (it breaks the block). Never start or end a block with `\\`.
4. **`\boxed{...}` stays on one line.** A top-level `\\` inside `\boxed{}` does not render. Box only the result and put definitions or side conditions on their own `\\` lines outside the box.
5. **`<` and `>` as relations need a space on both sides:** `$k > 0$`, `$0 < x < L$`, `$\sum_{i < j}$`, never `$0<x<L$`. (The user's renderer mis-parses them when flush against a neighbour.) Use `\langle`, `\rangle` for expectation values and `\leq`, `\geq`, `\ll`, `\gg` for the other relations, so bare `<`/`>` only appear as strict inequalities.
6. **No bare `|` in a Markdown table row, including inside `$...$`.** The renderer treats it as a cell separator. Use `\vert` for absolute values and norms (`$\vert t\vert$`) and `\mid` for "such that". A `|` in math outside tables is fine.
7. **No backticks inside math mode** (not even inside `\text`).
8. **Nested Markdown lists are indented by 4 spaces per level**, and a blank line precedes every top-level list (otherwise the renderer may not recognise the list).
9. **List items that contain empty line(s)** (e.g. to separate a sublist from the bulk text) **must be delimited by a newline** on either side.

These rules apply to every Markdown file of an opted-in project, code READMEs included.

## Math in code READMEs

Formulas in code READMEs are LaTeX too, never ASCII math like `L^2`, `sqrt(3)` or `|Phi|^(2K)`. Two exceptions keep the source readable where math is sparse:

- **Single Greek letters** may be plain Unicode: Γ for the centre of the Brillouin zone, φ for an angle, χ for a susceptibility.
- **Formulas that read unambiguously without rendering** may be plain text: function notation such as V(k) or D(k), path labels such as Γ-K-M-Γ, a product or ratio of two symbols. Anything with exponents, subscripts, fractions, roots, sums or vectors is LaTeX: $L^2$, $\sqrt3 \times \sqrt3$, $1/r^3$, $e^{i\phi}$, $H = \frac12 \sum_{ij} S_i \cdot J_{ij} \cdot S_j$.

**Code identifiers are always in backticks, never in math** (rule 7). Whether a symbol is a code name or a quantity decides its markup: "`L` must be divisible by 6", but "an $L \times L$ torus". Where a symbol is both, give the code name once together with its mathematical meaning.

## What the checker covers

- **Rule 1.** It flags spacing commands, `\\[..]` row options and `\phantom`.
    - It accepts `\,` next to a differential.
    - `\quad` and `\qquad` are reported as warnings, to judge against Exception 2.
- **Rule 3.** It flags blank lines in `$$` blocks and blocks that start or end with `\\`.
- **Rules 4, 5, 7 and 8.** It checks each of them fully.
- **Rule 6.** It also flags a row whose count of `|` differs from the header's.
- **Not checked.** Rules 2 and 9, and long formulas set side by side (rule 3), need your own judgement.

Text inside code spans and fenced code blocks is ignored.
