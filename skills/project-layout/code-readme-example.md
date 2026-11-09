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

---

# Second example: grouped README with a shared config schema

The example above is a flat `## Modules` README. The excerpt below is from a directory where families of analogous scripts share a method, so the shared parts are stated once per group and analogous scripts list only their differences. Sections elided here are marked "…".

# Analysis and Monte Carlo code (`code/`)

The code computes dipolar couplings on the triangular and honeycomb lattices by Ewald summation, analyses their zero-temperature physics and runs finite-temperature parallel-tempering Monte Carlo.

- **Pipeline.** `dipolar_xy.ewald` produces the triangular-lattice couplings, cached in `data/`. The analysis scripts and the Monte Carlo (MC) drivers project them onto their lattice and analyse or simulate.
- **Running.** Run every script from `code/`. Outputs go to `data/` (gitignored).
- **Package.** The shared modules form the package `dipolar_xy` (numpy, scipy and matplotlib only); `pip install -e code` makes it importable elsewhere.

## Conventions

- **Hamiltonian.** $H = \frac12 \sum_{ij} S_i \cdot J_{ij} \cdot S_j$ with a plus sign (File `../notes/02`, §1). The self-energy $J_{ii}$ is set to zero.
- …

## Parallel-tempering Monte Carlo

Classical MC with heat-bath sweeps and replica exchange along a temperature ladder.

**Round structure.** Each of the `n_rounds` recorded rounds runs `PT_per_round` rounds of replica swaps, each preceded by `sweeps_per_PT` sweeps. Only the state at the end of each round is recorded.

**Config file.** The drivers take one JSON config file (example: `honey_MC_example.json`).

- `L` (required): linear size in unit cells.
- `n_rounds` (required): number of recorded rounds.
- `sweeps_per_PT` (default 1), `PT_per_round` (default 2): the round structure above.
- `temperatures` (list) or `temperature_geom` (`{"min", "max", "steps"}`, passed to `np.geomspace`): the temperature ladder. If both are given, `temperatures` wins and a `UserWarning` is raised. The ladder is sorted ascending.
- `seed` (default: fresh entropy).

**Outputs**, under a root `data/{model}_MC_{N}..._{seed}` built from the resolved parameters:

- `{root}_resolved.json`: the config with every default filled in; passing it back reproduces the run exactly.
- `{root}_S.npy`: configurations at the end of every round, shape `(n_rounds, R, N, 2)`, memory-mapped.
- `{root}.npz`: energy, magnetization and order parameter per round and replica, the ladder and the run parameters.

### `dipolar_xy/mc.py`

MC for a generic 2D XY model with a dense coupling tensor of shape `(N, N, 2, 2)`. Used by `dipolar_xy/mc_driver.py`.

- `sweep(J, S, T, rng)` visits all sites in random order and draws each spin from its exact heat-bath distribution, for all `R` replicas at once.
- …

- **Design notes.** Because of the plus sign of $H$, a spin anti-aligns with its local field, so the von Mises location is the field angle plus π. Getting this backwards does not crash but samples the least likely states; `check_mc.py` catches it.

### `honey_MC.py`

MC of the honeycomb model in the six-site cell of `dipolar_xy.honeycomb`.

Calling sequence:

```
python honey_MC.py config.json
```

- **Config:** additionally `J1x` (default 1), the nearest-neighbour boost.
- **Outputs:** root `data/honey_MC_{6 L^2}_J1x{J1x}_T{Tmin}-{Tmax}x{R}_{seed}`. The npz also stores `J1x`.
- `order_parameter(S)` projects a configuration onto the ground-state family; it equals $e^{i\phi}$ for a perfect state at angle φ.

### `triangle_MC.py`

As `honey_MC.py`, except:

- one site per cell, so the triangular couplings are used without sublattice projection;
- no `J1x`; output root `data/triangle_MC_{L^2}_T{Tmin}-{Tmax}x{R}_{seed}`;
- `order_parameter(S)` is the complex magnetization.
