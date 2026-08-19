# FC-005 Checkpoint — Frozen Observational State

This is the canonical, frozen checkpoint for the FC-005 DESI discrete-to-continuum bridge
investigation, following the sparse N-scaling follow-up (`FC005_N_SCALING_REPORT.md`) to the
original Gate 1 failure investigation (`FC005_CONTINUUM_DIAGNOSTIC_REPORT.md`).

**This checkpoint does not rerun or alter FC-005.** It formalizes and validates the state
already reached, adds a standing structural rule the compiler now enforces on every build,
and regenerates the derived registries through the normal compiler pathway.

## Canonical current result

| Node | Status |
|---|---|
| `CONTINUUM-LIMIT-L-DESI` | **FAIL / RETRIABLE** |
| `MATHEMATICAL-CONVERGENCE-DESI` | **FAIL / RETRIABLE** |
| `CURVATURE-CLOSURE-DESI` | **OPEN** |
| `PHYSICAL-VALIDATION-DESI` | **OPEN** |

Not `FALSIFIED`. Not `CLOSED`. Verified directly against a fresh `compiler.run_compiler` run
(see "Verification" below) — these are not asserted values, they are read back from
`status_matrix.json` after regeneration.

## Established findings

1. **Corrected epsilon scaling**: `epsilon_N ∝ N^(-1/(d+4))` for the d=3 convergence regime
   under test — the bias-variance-optimal rate, verified to satisfy the asymptotic condition
   `N·eps_N^(d+2) → ∞` at every tested configuration (the prior rate, `N^(-1/d)`, did not).
2. **Uniform IID sampling** demonstrates clean sparse spectral convergence through N=64,000 —
   modes 1 through ~11 are jointly eigenvalue- and eigenvector-stable by the final refinement
   step.
3. **DESI exhibits genuine convergence in the lowest ~4 modes** under the current
   construction (α=0, unnormalized) — joint eigenvalue+eigenvector stability confirmed for
   mode range [1,5) at N=32000→64000.
4. **Higher DESI modes (5–15) exhibit eigenvalue proximity without corresponding eigenspace
   stability** — eigenvalue relative changes as small as 0.05–0.13, paired with subspace
   principal cosines of 0.07–0.15 (near-orthogonal), a classic eigenvalue-crossing artifact.
5. **Therefore eigenvalue-only convergence is explicitly insufficient** — formalized below as
   a standing, enforced rule.
6. **The clustered synthetic control remains unresolved/failed**: zero eigenvalues were
   reliably resolved by the sparse solver at any tested N (4000–64000), under either
   normalization, within the 500-iteration budget.
7. **DESI therefore sits between the ideal IID control and the pathological clustered
   control** — not the clustered control's total breakdown, but slower to stabilize than
   uniform sampling at matched N.
8. **The finite-resolution issue has been substantially reduced but the DESI continuum
   interface is not yet closed** — N-scaling resolved the ambiguity around whether N≤4000 was
   sufficient (it was not, for any process, including the positive control), but a real,
   precisely localized residual gap remains at higher mode indices for DESI specifically.

All previous runs remain in provenance. Nothing was deleted: the dense-`eigh` results
(`FC005_CONTINUUM_FAILURE_MATRIX.csv`, `data/desi/dr1/fc005/derived/diagnostic_full_results.json`
and siblings) and the sparse N-scaling raw results
(`data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json`) are both intact and
unmodified in content (only the `converged` field's *derivation* was corrected — see below).

## The scalar 0.127 result was NOT promoted into canonical state

The naive eigenvalue-only relative-change metric reported DESI (α=0) as `converged=True` at
N=64000 (final relative change 0.127 < 0.15 tolerance). Per instruction, this scalar result
has been explicitly excluded from the canonical state:

- `data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json` now carries three
  distinct fields per dataset: `eigenvalue_only_converged` (the original, superseded, scalar
  value — preserved for transparency, never used for status decisions),
  `joint_spectral_converged` (the corrected verdict, computed from eigenvalue **and**
  eigenvector/subspace stability), and `converged` (the canonical field, now always equal to
  `joint_spectral_converged`).
- After this correction, **every one of the six tested (process, α) configurations shows
  `converged=False`** — including uniform IID, whose highest tested mode cluster [11,15]
  also falls just short of the strict joint criterion (subspace cosine 0.76 < 0.9), correctly
  and conservatively reflecting that not even the positive control has been proven to
  converge across its *entire* retained 15-mode spectrum, only through mode ~11.
- `compiler/ir/fc005.py::register_fc005` reads this corrected `converged` field directly, so
  `calculation_registry.json`'s `CALC-FC005-DESI-SPARSE-N-SCALING` entry reflects the joint
  verdict, not the scalar one — confirmed by direct inspection after regeneration (see
  "Verification").

## Spectral-validation rule (standing, enforced)

> **Eigenvalue convergence alone is insufficient for CLOSED status whenever eigenvalue
> crossings, degeneracies, or subspace rotations are possible.** Wherever an
> eigenvector/invariant-subspace comparison is available, validate all three of: eigenvalues,
> eigenvectors, and invariant subspaces/projectors, before accepting a convergence verdict.

Implemented, not merely documented:

- `compiler/backends/desi_sparse.py::joint_spectral_convergence` — the reusable function that
  computes the authoritative joint verdict from a set of mode-cluster classifications
  (eigenvalue-only / eigenvector-only / both / neither unstable). A verdict of `True` requires
  every tested mode cluster to be classified `neither` (both eigenvalue- and
  eigenvector-stable).
- `compiler/verification/self_audit.py::spectral_validation_audit` — a new, ninth self-audit
  (wired into `run_self_audit` via an optional `calculations` parameter, called from
  `compiler/run_compiler.py`) that **fails the build** if any stored `converged` value in a
  sparse-spectral-comparison calculation disagrees with its own recorded
  `joint_spectral_converged` field. This is a structural guard against a future code path
  silently promoting a scalar eigenvalue-only result into the canonical state again.

## Verification

Executed for this checkpoint (all against the already-existing sparse investigation data —
no eigensolves were rerun):

```
python3 apply_spectral_validation_rule.py      # corrects converged fields, regenerates CSVs
python3 -m compiler.run_compiler               # regenerates calculation_registry.json,
                                                # status_matrix.json, falsification_registry.json,
                                                # provenance registries, through the normal pathway
python3 -m pytest compiler/tests -q            # full test suite
```

Results:

```
terminal status: CONDITIONALLY_CLOSED
audits passed: True
  [PASS] dependency_audit (0 issues)
  [PASS] circularity_audit (0 issues)
  [PASS] type_audit (0 issues)
  [PASS] provenance_audit (0 issues)
  [PASS] target_independence_audit (0 issues)
  [PASS] status_audit (0 issues)
  [PASS] leakage_control_audit (0 issues)
  [PASS] numerical_reproducibility_audit (0 issues)
  [PASS] artifact_completeness_audit (0 issues)
  [PASS] spectral_validation_audit (0 issues)

95 passed in 43.30s (compiler/tests)
```

`status_matrix.json` confirms `CONTINUUM-LIMIT-L-DESI = FAIL`, `MATHEMATICAL-CONVERGENCE-DESI
= FAIL`, `CURVATURE-CLOSURE-DESI = OPEN`, `PHYSICAL-VALIDATION-DESI = OPEN`.
`falsification_registry.json` is unchanged by this checkpoint (no new falsification claim was
made or should be — this checkpoint neither closes nor falsifies the branch).

`leakage_control_audit` confirms the `FAIL` status of `CONTINUUM-LIMIT-L-DESI` and
`MATHEMATICAL-CONVERGENCE-DESI` does not propagate as `CALCULATED`/`VERIFIED`/`DERIVED` into
any downstream node — `DESI-HEAT-TRACE` through `PHYSICAL-VALIDATION-DESI` remain `OPEN`,
untouched.

## Gate 2 was not entered

No curvature extraction, heat-trace fit, or `(a0, a1, a2)` computation was performed for
DESI at any point in this checkpoint. `CURVATURE-CLOSURE-DESI` and `PHYSICAL-VALIDATION-DESI`
remain `OPEN`, exactly as before this checkpoint.

---
*This checkpoint is the reference state for FC-005 while the MASTER PHYSICS VALIDATION
CAMPAIGN (validating independently reachable canonical physics branches while FC-005 remains
explicitly FAIL/RETRIABLE) proceeds separately.*
