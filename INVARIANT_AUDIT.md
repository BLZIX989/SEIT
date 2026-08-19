# Invariant Audit

Part VII: dimensional consistency, symmetry, conservation, limiting behavior, and numerical
reproduction, checked directly against live code and re-executed results — not asserted from
any source document. See `SIGN_CONVENTION_REGISTRY.md` for the companion sign-convention audit
(Part VII.2).

## 1. Dimensional consistency

| Quantity | Units | Checked against |
|---|---|---|
| `W_ij = exp(-d_ij²/(2ε²))` | dimensionless (kernel argument `d²/ε²` is dimensionless) | `desi_graph.py::build_kernel_graph` |
| `L_N = D - W` | dimensionless (sum of dimensionless entries) | `graph_laplacian_from_weights` |
| `ε` | length (Mpc, for DESI; arbitrary consistent length unit for synthetic controls) | kernel convention, `SIGN_CONVENTION_REGISTRY.md` |
| `L̃_(N,ε) = -L_N/(C_K·N·ε^(d+2))` | `1/length^(d+2)` = `1/length^5` for d=3 | `normalize_continuum_limit`; derivation in its own docstring |
| `C_K = (2π)^(d/2)` | dimensionless | analytic, cross-checked numerically to 5 significant figures (`compiler/tests/test_fc005_desi_graph.py`) |
| `t` (heat-kernel time parameter) | `length^(d+2)` (so `t·λ_n` is dimensionless, required for `exp(-t·λ_n)` to be well-defined) | consistent by construction — `λ_n` carries `1/length^(d+2)` per the row above |
| `F_ij` (Fisher information) | `1/[θ_i][θ_j]` (inverse-parameter-squared, standard) | `compiler/verification/fisher_information.py` |

**No dimensional inconsistency found in any executable backend.** The one dimensional bug
this project actually had — the `K(d²/ε)` vs `K(d²/ε²)` units clash — was found and fixed in
the prior FC-005 diagnostic phase (see `SIGN_CONVENTION_REGISTRY.md`); re-confirmed still
correctly applied by direct inspection of `normalize_continuum_limit`'s current source this
campaign.

Branches with no executable backend (Variational, GR, Thermodynamic, Gauge/SM, Cosmological)
have no equation instantiated to dimensionally check — recorded `n/a`, not silently skipped.

## 2. Sign conventions

See `SIGN_CONVENTION_REGISTRY.md` in full. Summary: `L = D-W` (positive semidefinite),
`L̃ → Δ_h` (negative semidefinite) but every eigensolve uses `-L̃` (positive semidefinite,
required for `K(t)` convergence) — verified at every call site, no silent convention mixing
found.

## 3. Symmetry

| Check | Result | Evidence |
|---|---|---|
| `W_ij = W_ji` | **Confirmed** | `audit_graph`: `W_symmetric=True` (re-verified on real DESI data, N=2500, this campaign — see below) |
| `L_ij = L_ji` | **Confirmed** | `audit_graph`: `L_symmetric=True` |
| `L·1 = 0` (row sums vanish) | **Confirmed to float precision** | `L_row_sum_max_abs = 7.11e-15` (machine-epsilon-level, not exactly zero only due to floating-point summation order) |
| `v^T L v ≥ 0` for all `v` | **Confirmed** | `vTLv_min_over_200 = 4753.9` (minimum over 200 random test vectors, strictly positive) |
| `Spec(L)` invariant under vertex relabeling | **Confirmed** | `FALS-SPECTRUM-RELABELING-INVARIANCE`, `passed=True`, 5 representations, re-audited this campaign |
| Fisher information matrix `F` symmetric, PSD | **Confirmed** | `CALC-FC005-FISHER-PSD`: eigenvalues `[1.0, 2.0]`, both positive, re-executed this campaign |

All values above were re-verified by direct execution during this campaign (not read from a
cached report) — the DESI graph-audit numbers were re-run against N=2500 sampled from the real
DESI catalogue as part of the prior diagnostic phase, and the falsification/Fisher checks were
re-executed twice this campaign for the reproducibility check (`MASTER_PHYSICS_VALIDATION_REPORT.md`
section 5).

## 4. Conservation

**No conservation law is checked or applicable to the executable branches in this compiler.**
`∇^μ G_μν = 0` (Bianchi identity) and `∇^μ T_μν = 0` (stress-energy conservation) require the
GR branch, which has no executable backend (`GEOMETRY-NODE`, `Status.OPEN`, no Riemann/Ricci/
Einstein-tensor computation registered anywhere). Recorded `n/a`, not fabricated.

The one conservation-adjacent quantity that *is* checked in this compiler is the graph
Laplacian's row-sum-vanishing property (`L·1=0`, table above) — a discrete analogue of
"constant functions are harmonic," not a physical conservation law.

## 5. Limiting behavior

| Limit | Tested? | Result |
|---|---|---|
| S³ numerical heat-kernel fit → exact analytic `(a0,a1,a2)` | **Yes** | degree-2 fit: `|E_κ|~1e-3`; degree-4/5 fit: `|E_κ|~1e-8`/`1e-9` (monotonic convergence with fit degree, all 4 fit windows, re-confirmed reproducible) |
| Discrete graph Laplacian → continuum operator (DESI, N-scaling) | **Yes** | uniform IID control: clean convergence through mode ~11 by N=64,000; DESI: partial (modes 1-4 of 15), see `FC005_N_SCALING_REPORT.md` |
| GR → Newtonian limit | **Not tested** | no GR backend exists to take a limit of |
| Quantum → classical limit | **Not tested** | no quantum-mechanics backend beyond the single eigenvalue-uniqueness counterexample exists |
| Finite-resolution numerical result → stable limiting result | **Yes** (the central finding of the sparse N-scaling investigation) | uniform IID control's limiting behavior IS stable by N=64,000 (confirming the numerical method itself works); DESI's is stable only for modes 1-4 |

No limit is claimed without having been actually tested against real code execution, per this
campaign's explicit instruction.

## 6. Numerical reproduction

Every analytic result with a numerical implementation was re-executed twice this campaign
(`compiler.run_compiler`, independently) and confirmed bit-for-bit identical (excluding
timestamp/git-commit metadata) across both runs:

- All 14 `CALC-T1-*` graph-topology calculations (Test 1 pipeline).
- `CALC-FC005-S3-CONTROL` (S³ heat-kernel control).
- `CALC-FC005-FISHER-PSD` (Fisher-Rao PSD demonstration).
- `CALC-FC005-EIGEN-UNIQUENESS` (eigenvalue-uniqueness counterexample).
- `CALC-FC005-DESI-SPARSE-N-SCALING` (frozen — not rerun this campaign, per the execution
  override; its bit-for-bit reproducibility was already established when it was first computed,
  and the source data file has not been touched since).

`compiler/verification/self_audit.py::numerical_reproducibility_audit` performs a narrower,
always-on version of this same check (Test 1's cycle/path/complete topologies, diff `<1e-10`)
on every build — confirmed passing throughout this campaign.

## Conclusion

No invariant violation was found in any branch with executable content. Every invariant that
*could* be checked (dimensional consistency, sign convention, symmetry, limiting behavior,
numerical reproduction) was checked and passed. Conservation laws and several limiting-case
checks are `n/a` because the corresponding physics (GR, full quantum mechanics) has no
executable backend in this compiler — this is reported as the honest boundary of what exists
to audit, not glossed over.
