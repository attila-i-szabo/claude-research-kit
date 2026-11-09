---
name: python-style
description: Python house style for research code — light style for figure and toy scripts, production style (type hints, Google docstrings, field docstrings, structured function bodies, black, 88 columns) for code used in the user's own runs, and packaging/maintainability rules for code that grows into a codebase. Use whenever writing, refactoring or reviewing Python in a project that uses this style.
---

# Python house style

There are two tiers. Light style is the default for scripts that only generate a figure or test a toy model. Production style is for code that will be **used beyond the notes**: imported into the user's training runs, or grown into a coherent codebase. Packaging and maintainability rules apply to both tiers.

Code READMEs follow skill `project-layout`. Cross-references from code to notes use the format of that skill, backticks included, e.g. ``(File `../07`, §2.2)`` in a docstring.

## Light style

- Each function has a **single-line docstring**.
- One script per figure or check, named after what it produces; it says in its module docstring which notes file it serves.
- Scripts are runnable from the root (`python code/script.py`) and write outputs to the paths given in the notes and the code README. A project's `CLAUDE.md` may name another working directory.
- A change to a script's command line, config schema or outputs updates the code README in the same pass (skill `project-layout`), with the calling sequence checked against the argument parser.

## When to use production style

- Use it when the user asks for "production style", or asks for code to be used in their own runs (e.g. a NetKet or Flax component).
- **Suggest switching** when a `code/` directory stops being a set of independent scripts: modules import each other, functions are reused across scripts, or the user asks to package, distill or refactor them into something they will import. Ask before converting existing scripts.
- When converting, change only the files that become part of the codebase. Leave the toy and figure scripts alone.

## Production style

### Naming and types

- Every function and method signature has **type hints**. Use the type aliases the libraries already define instead of new ones. With NetKet, for example, use `netket.utils.types.{Array, ArrayLike, PyTree, Optimizer}` and `netket.vqs.VariationalState`.
- **Parameters have descriptive names** (`H_coeff`, `min_advantage`, `embedding_name`), not abbreviations.
- **Local variables use the symbols of the notes**, Greek letters included (`σ_A`, `γ`, `μ`, `δ`, `φ`, `π_source`), never ASCII abbreviations like `sig`.
- **Do not introduce aliases for converted inputs.** Reassign the argument instead: `e_loc = jnp.asarray(e_loc)`, not `ℓ = jnp.asarray(e_loc)`.

### Function and method docstrings

These use Google style, readable by Sphinx Napoleon.

1. The **first line** is a one-sentence summary.
2. A **short explanatory paragraph** follows, only as long as needed. It may cite the notes (``File `../07`, §2.2``) for derivations instead of repeating them.
3. **`Args:`** lists each argument as `name: description`. The description gives the shape (e.g. `shape (n_points, n_terms)`), the dtype or allowed range where it matters, and how to initialise or obtain the value.
4. **`Returns:`** describes a single return value in prose. A **tuple** has each element listed in the same `name: description` format as `Args:`, in order.
5. When refactoring or distilling existing code, **keep this layout unchanged**. Shorten only the explanatory paragraph.

### Field docstrings of classes

Document each public field that has no `@property` with a string literal directly below its declaration. Use a telegraphic style, without semicolons. This applies to dataclass-like classes too (Flax modules, NetKet pytrees, dataclasses): do not list fields in an `Attributes:` section of the class docstring. The class docstring describes the class; each field documents itself.

- **First line, on its own:** one sentence of under 80 characters saying what the field is or does.
- **Then, optionally, after a blank line:** short lines, one statement each, and only where they help a user work with the variable. Examples are the meaning of an index, sentinel values, and the effect of tuning the field.

```python
embedding_name: str = struct.field(pytree_node=False, serialize=False)
"""Key of the MixtureEmbedding submodule to be updated in state.parameters."""
target: Array | None = struct.field(pytree_node=True, serialize=False)
"""Source indices of the last update, shape (n_points,).

target[r] == r wherever weight[r] == 0.
None before the first update."""
```

Properties have a one-line docstring saying what they return.

### Structure

- Put the numerics in **pure functions** and make the heavy ones jittable, marking non-array arguments in `static_argnames`. Keep array shapes fixed under `jit`; for example, use a weight of zero instead of a variable-length selection.
- **Stateful objects are thin wrappers** around these functions and follow the conventions of the host library. For example, a NetKet object holding training state is a mutable `netket.utils.struct.Pytree`, with fields declared through `struct.field(pytree_node=..., serialize=...)` like NetKet's drivers. Do not turn it into a full driver unless asked.
- Expose diagnostics of the last call (weights, selections, losses) as fields, so the user can log them.

### Comments inside functions

A function body longer than a few lines must not be an undivided pile of instructions.

- **Split it into logical units** separated by a blank line: extracting a quantity, building shapes, drawing random numbers, folding a map into parameters, a final correction.
- **Head each unit with a one-line comment** saying what the unit computes or why, in the terms of the notes, e.g. `# slope and intercept of the map (x_min, x_max) -> (-1, 1)` or `# shift the last bias by minus the output mean over all inputs`. Lower-case, no full stop, within 88 columns.
- **Comment the non-obvious step, not the syntax.** A line whose purpose is clear from its names needs no comment; a trick (binding a Flax module to no variables, summing a kernel over the group axis for a bias) does.
- Guard clauses (argument checks that raise) form the first unit and need no comment.

### Formatting and checks

- Run **`black`** (default settings) on every `.py` file you touch in `code/`, in both tiers. In projects that opt in (their `CLAUDE.md` names `python-style`), a hook runs black after every edit of a `.py` file.
- Keep lines in production code, docstrings included, within **88 columns**. Black does not wrap docstrings or comments, so rewrap them by hand.
- **Verify each change by running it** with a test script in the scratchpad, not in `code/` unless the user asks. Where an earlier implementation exists, check the new code against it. Report what was checked.
- Mention new production modules in the relevant numbered notes file and in the code README. A change to a module's interface, a script's command line or a config schema updates the code README in the same pass (skill `project-layout`), with the calling sequence checked against the argument parser.
- Scripts take their arguments through `argparse` (so `--help` works) and keep their work in a `main()` behind `if __name__ == "__main__":`, split into functions with one job each.

## Packaging and maintainability

These apply to both tiers and are what the `code-simplifier` agent checks.

- **Preserve behaviour.** A refactor changes how the code does something, never what it does, unless the user asks. Verify by running the affected scripts or tests before and after.
- **One home for each helper.** When the same logic appears in two scripts, move it into a module both import, rather than copying it. Keep that module free of side effects on import (no plotting, no heavy work at import time).
- **Package once modules import each other.** Give `code/` (or the project's code directory) a minimal `pyproject.toml` and a package directory, installable with `pip install -e .`, instead of `sys.path` manipulation. Scripts stay outside the package and import from it.
- **No premature abstraction.** Do not add classes, configuration layers or plugin mechanisms for a single use. A plain function with explicit arguments is the default; introduce a class when there is state that must persist across calls.
- **Delete dead code**, commented-out blocks and unused arguments, rather than keeping them "just in case". The notes and version control remember old approaches.
- **Clarity over brevity.** Prefer explicit loops or named intermediate variables to nested comprehensions, chained conditional expressions or clever one-liners. Avoid nested conditional expressions entirely.
- **Flat control flow.** Use early returns and guard clauses instead of deep nesting.
- **Small functions with one job.** Split a function when its logical units (see "Comments inside functions") could be named and reused separately.
- **Consistency with the project.** Follow the existing conventions of the codebase (naming, array library, configuration style) over generic preferences.
- **Explicit dependencies.** Heavy imports (JAX, NetKet, torch) live only in the modules that need them, so lightweight analysis scripts run without them. State the dependencies in the code README.
