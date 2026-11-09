# Main code (`code/`)

Auxiliary scripts and checks are described in `aux/README.md`.

## Modules

### `models.py`

Dispatch on the model of a scan (`"model"` in the JSON files of `theta_scan.py`; `"ZQ14"`, `"Z3"` or `"Z3_SQRT3"`), used by the scripts that read or produce scan data. JAX is imported only by `orbital_module`, so the statistics scripts run without it.

- `orbital_module(model)` returns the module `zq14_orbitals`, `z3_orbitals` or `z3_sqrt3_orbitals` (drop-in replacements of each other); `check_model(model)` raises for an unknown model.
- `model_of(d)` returns the model of a loaded point file (its `model` key; ZQ14 if absent, as in older files). `model_of_folder(name)` returns it from a scan folder name (the suffix `_Z3` or `_Z3_SQRT3`, else ZQ14).
- `n_lattice_sites(model, L)` is the number of lattice sites ($L^2$ for ZQ14 and Z3, $3L^2$ for Z3_SQRT3), by which the densities $\chi_F$ and $d\chi_F/d\Theta$ are divided. `n_particles(model, L)` is the particle number ($L^2$ for ZQ14, $2L^2/3$ for Z3, $2L^2$ for Z3_SQRT3).

### `slater_sampler.py`

Metropolis sampler for $\vert\Phi\vert^{2K}$, where $\Phi$ is a Slater determinant given by its filled orbitals (File `../notes/05`, §2). It requires JAX, `lrux` and NetKet, and enables 64-bit precision on import. Used by `theta_scan.py`.

- The wave function is $\Phi(R) = \det_{pk} \mathrm{orbitals}[R_p, k]$, with `orbitals` an `(n_sites, N)` array whose columns are the filled orbitals.
- The acceptance uses the determinant ratio from `lrux.det_lru` (rank-1 row update), which also returns the new inverse. A step costs $O(N^2)$. The inverse and $\log\Phi$ are recomputed from scratch every `refresh_every` sweeps.
- `SlaterSampler` is a JAX pytree, as NetKet's samplers are: `orbitals`, `K` and the proposal rule's arrays are traced leaves, while shapes and loop lengths are static. The jitted methods therefore compile once and are reused for different orbitals and $K$ (`sampler.with_parameters(...)`).

Usage:

```python
sampler = SlaterSampler(orbitals, K=3, graph=graph, d_max=2, refresh_every=16384)
state = sampler.init_state(key, n_chains)
state = sampler.run(state, n_sweeps=200)
state, occupations, logdet, dlogpsi = sampler.sample(state, n_samples=1000)
state, drift = sampler.refresh(state)  # drift: largest change of log|Phi|
sampler2 = sampler.with_parameters(orbitals=new_orbitals, K=2)  # no recompilation
```

- `K`: the sampled distribution is $\vert\Phi\vert^{2K}$.
- `g` (default 0): Gutzwiller parameter; the sampled distribution is $\vert\Phi\vert^{2K} e^{-2gD}$, with $D$ the number of doubly occupied pairs (see `partner`). Positive $g$ is repulsive. A nonzero `g` needs `partner`.
- `partner` (default None): `(n_sites,)` integer array pairing the rows (an involution); it defines $D$.

### `plot_theta_scan.py`

Analysis and figure of one or several scans written by `theta_scan.py` (File `../notes/08`, File `../notes/09`). The plotted quantity is the density $\chi_F = X_F/L^2$ (File `../notes/06`, §2.4), so that its extensive part does not scale.

Calling sequence:

```
python code/plot_theta_scan.py [--partial] [scan_directory ...]
```

- `scan_directory ...`: directories with the point files of one model; default: all `code/data/theta_scan_L*_K*`. The figure is saved as `code/data/theta_scan_K{K}_summary.png`.
- `--partial`: also read the unfinished point files `.npz.partial`; a partial file is ignored if the completed `.npz` of the same point exists. Default: completed files only.
