# Global Sign-Convention Registry

Part VII.2's required "global sign-convention registry," tracking every convention actually
in force across this compiler's executable backends. A module may not silently switch
convention; this document is the single reference point to check against.

## Metric signature

**Not applicable — no metric tensor `g_μν` is instantiated anywhere in this compiler.** No
signature convention (mostly-plus vs mostly-minus) has been chosen because there is nothing to
apply it to (branches "Geometry" and "GR" have no executable backend — see
`MASTER_PHYSICS_VALIDATION_MATRIX.csv`).

## Curvature convention (Riemann, Ricci)

**Not applicable — no Riemann or Ricci tensor is computed anywhere in this compiler.** The
only curvature-adjacent computations in this build are the S³ heat-kernel coefficient
extraction (`a0, a1, a2` — scalar heat-kernel coefficients, not the Riemann/Ricci tensors
themselves) and the DESI curvature-closure pipeline code (`κ`, never executed on real data
since Gate 1 has not closed).

## Graph Laplacian convention

**`L = D - W`** (`compiler/backends/{graph_laplacian,desi_graph}.py::graph_laplacian_from_weights`),
where `D = diag(row sums of W)` and `W_ij ≥ 0`. This is the standard **combinatorial /
positive-semidefinite** convention: `v^T L v = (1/2) Σ_ij W_ij (v_i - v_j)^2 ≥ 0` for all `v`,
confirmed directly (`audit_graph`'s `vTLv_min_over_200 ≥ 0` check, `compiler/backends/
desi_diagnostics.py`). Eigenvalues of `L` are therefore **non-negative** by construction, with
the constant vector spanning the (at least one-dimensional) zero eigenspace.

This is the opposite sign from the "analyst's Laplacian" `Δ_h` convention (below) — this
distinction is exactly what the FC-005 sign-convention fix (next section) had to reconcile.

## `Δ_h` vs `-Δ_h` (the FC-005 sign-convention fix)

The FC-005 workbook's own equations (DC-009/DC-010, `EQ-013`/`EQ-014`) define the normalized
continuum-limit operator as `L̃_(N,ε) → Δ_h`, the **analyst's Laplacian**, which is
**negative** semidefinite (opposite sign from the graph-Laplacian convention above — this is
the standard convention clash between "graph theory" `L` and "differential geometry" `Δ`). The
heat-trace eigenproblem actually needed for `K(t) = Σ_n exp(-t·λ_n)` to converge requires
`λ_n ≥ 0`, i.e. it is stated for `-Δ_h`, not `Δ_h`.

**Fixed convention, in force everywhere in this compiler**: every eigensolve for the
continuum-limit operator diagonalizes `-L̃`, never bare `L̃` — verified directly in
`compiler/backends/desi_fc005_pipeline.py::run_mathematical_convergence` (`_low_eigen(-L_tilde,
n_modes)`, with an explicit in-code derivation comment) and in
`compiler/backends/desi_sparse.py::sparse_low_eigen` (operates on `neg_L_tilde`, built as
`(1.0/norm_const) * L`, i.e. `Spec(-L̃) = Spec(L)/norm_const` by construction — never the
literal matrix `-L̃` built and then re-negated, avoiding a double-negation error class
entirely). Both call sites were checked directly for this registry — neither silently mixes
`L̃` and `-L̃`.

## Kernel convention (and the units bug this fixed)

**`W_ij = exp(-d_ij² / (2ε²))`**, `ε` in **length units** (`compiler/backends/
desi_graph.py::build_kernel_graph`), the standard convention in the graph-Laplacian
convergence literature (Belkin-Niyogi 2005/2008; Coifman-Lafon 2006; Hein, Audibert & von
Luxburg 2007; Singer 2006).

This is explicitly **not** the same convention as the source workbook's own kernel
`K(d²/ε)` (no factor of 2, `ε` carrying **length²** units). This exact clash —
`K(d²/ε)` vs `K(d²/ε²)` — is precisely the dimensional-normalization bug the FC-005
diagnostic investigation found and fixed (`FC005_CONTINUUM_DIAGNOSTIC_REPORT.md` section 3.2):
the normalization exponent must be `ε^(d+2)` for this code's length-unit `ε`, not the
workbook's `ε^(d/2+1)` (which is only correct for the workbook's own length²-unit `ε`). The
canonical convention was **not** changed to chase convergence — it was reconciled once, with
the derivation recorded in `compiler/backends/desi_graph.py::normalize_continuum_limit`'s
docstring, and never touched again.

**Continuum-limit normalization**: `L̃_(N,ε) = -L_N / (C_K · N · ε^(d+2))`, `C_K = (2π)^(d/2)`
(the analytic second moment of this exact kernel, cross-checked numerically in
`compiler/tests/test_fc005_desi_graph.py`). Dimensional consistency: `W_ij` is dimensionless
(the kernel argument `d²/ε²` is dimensionless by construction), so `L_N` (a sum of `W_ij`
entries) is dimensionless; `ε^(d+2)` carries units of `length^(d+2)` (`length^5` for `d=3`);
`C_K` is a dimensionless numerical constant. `L̃` therefore carries units of `1/length^(d+2)`
— consistent with the standard graph-Laplacian-to-continuum-Laplacian normalization rate
(the same rate the corrected `ε_N ~ N^{-1/(d+4)}` sparse N-scaling investigation verified
satisfies `N·ε_N^{d+2} → ∞`, `FC005_N_SCALING_REPORT.md` section 3).

## Heat-kernel / heat-trace convention

**`K(t) = Σ_n exp(-t·λ_n)`**, requiring `λ_n ≥ 0` — consistent with, and only consistent
with, the `-L̃`/`-Δ_h` sign convention above (an operator with any negative eigenvalue would
make `K(t)` diverge as `t → ∞` for that mode, which never occurs in this codebase because the
sign fix above is enforced at every call site).

## Fisher information / Fisher-Rao metric convention

**`F_ij = E[(∂/∂θ_i log p)(∂/∂θ_j log p)]`** (`compiler/verification/fisher_information.py`)
— the standard, positive-semidefinite Fisher information metric convention. No alternate
sign convention is used anywhere for this quantity in this compiler.

## Density-normalization convention (Coifman-Lafon α)

**`W'_ij = W_ij / (D_i^α · D_j^α)`** (`compiler/backends/desi_sparse.py::alpha_normalize_sparse`),
`α=0` recovers the plain (unnormalized) graph Laplacian above; `α=1` is the full
density-normalized construction. Both signs/directions tested in the sparse N-scaling
investigation used this single, consistent definition — never flipped or redefined between
calls.

## Summary — no convention clash found in force

Every module checked for this registry (`graph_laplacian.py`, `desi_graph.py`,
`desi_sparse.py`, `desi_fc005_pipeline.py`, `fisher_information.py`,
`heat_kernel_sphere.py`) uses its stated convention consistently at every call site. The one
historical convention clash this project actually had — `Δ_h` vs `-Δ_h` — was found, fixed,
and is now structurally enforced (never re-litigated per-call). The one dimensional-units clash
— `K(d²/ε)` vs `K(d²/ε²)` — was found, fixed, and documented in-code. No new clash was found
during this campaign's audit.
