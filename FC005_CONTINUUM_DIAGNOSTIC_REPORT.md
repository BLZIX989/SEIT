# FC-005 Continuum-Limit Failure — Full Diagnostic / Closure Investigation

**Failed dependency:** `CONTINUUM-LIMIT-L-DESI` (Gate 1: `MATHEMATICAL-CONVERGENCE-DESI`)
**Investigation scope:** real DESI DR1 LRG SGC catalogue (v1.5, `0.4<=z<0.6`), no synthetic
substitution of DESI at any point; synthetic point sets used only as diagnostic controls.
**Final status: OPEN.** Gate 1 remains `FAIL`. Gate 2 (`CURVATURE-CLOSURE-DESI`) and Gate 3
(`PHYSICAL-VALIDATION-DESI`) were never entered. No tolerance was changed. No result was
reinterpreted as success.

---

## 1. FAILED LINK

`CONTINUUM-LIMIT-L-DESI`: the refinement sequence of `L_tilde_(N,eps)` built from the real DESI
point cloud does not show numerical evidence of convergence as `N` increases / `eps` decreases,
under any tested combination of normalization, bandwidth rule, boundary treatment, redshift
window, or density-normalization scheme. Reported originally (pre-investigation) as relative
changes 0.42 / 0.28 / 0.41 against tolerance 0.15. Those exact numbers were measured with a
metric that this investigation found and fixed to be partially unreliable (Section 3); the
corrected, honest measurement is *not smaller* — see Section 5.

## 2. CAUSE

No single-bug cause was found. Two genuine implementation-level issues were found and fixed
(Section 3); fixing them changed the numbers but did **not** produce convergence. The dominant
surviving cause, isolated by controlled comparison against synthetic point processes
(Section 8), is:

> **Category I: a mismatch between the DESI point process and the i.i.d.-sampling assumption
> required by graph-Laplacian-to-continuum-Laplacian convergence theorems, compounded by
> Category D: insufficient sampling resolution achievable with a dense `eigh` solver at the
> tested N range (800-4000).**

Categories **A** (bare implementation error), **E** (redshift/radial selection function alone),
and **F** (survey boundary alone) were each specifically tested and **ruled out** as the primary
or sole cause (Sections 6, 7, 9). Category **C** (wrong normalization exponent) was a real,
independently-justified bug and has been fixed in the canonical code (Section 3), but the fix
alone does not repair convergence. Category **G** (bandwidth/kernel regime) was swept
systematically (Section 10) and no regime was found that converges. One standard, published
correction targeting Category **I** directly — Coifman-Lafon density normalization — was tested
and does **not** repair convergence either, and destabilizes the closest synthetic analogue of
DESI's clustering (Section 8.4). No further mathematically justified, non-invented correction is
known to the investigator that has not been tested.

## 3. EVIDENCE — implementation bugs found and fixed

### 3.1 Relative-change metric floor bug (found and fixed this investigation)

`run_mathematical_convergence`'s convergence metric used a **fixed absolute floor**
(`max(|prev|, 1e-12)`) in its denominator. After the normalization-exponent correction (3.2)
made the true eigenvalues fall to `O(1e-13)`-`O(1e-17)`, this fixed floor began to dominate the
comparison, producing a spurious near-zero "relative change" (`0.0004`-`0.0009`) that looked like
convergence but was actually measuring `|Δ|/1e-12`, not a real fractional comparison. This was
caught and rejected before being reported (explicit note made at the time: *"the apparent
convergence above is a measurement artifact, not a real result"*). **Fix:** the metric now
excludes the zero mode and uses a floor relative to each run's own eigenvalue scale
(`max(mean(|nonzero eigenvalues|) * 1e-6, 1e-300)`). Applied in
`compiler/backends/desi_fc005_pipeline.py::run_mathematical_convergence` and independently
duplicated in the diagnostic scripts. All reported numbers in this report use the corrected
metric.

### 3.2 Normalization exponent unit mismatch (found and fixed this investigation)

The canonical `normalize_continuum_limit` used exponent `d/2+1 = 2.5` (for `d=3`), taken directly
from the workbook's EQ-014 (`eps^(5/2)`). But the workbook's own kernel (`DC-002`) is literally
`K(d^2/eps)` — its `eps` carries **length²** units. `build_kernel_graph` in this codebase instead
implements `K(d^2/eps^2)` — a **length**-unit `eps`, the standard convention in the graph-Laplacian
convergence literature (Belkin-Niyogi 2005/2008; Coifman-Lafon 2006; Hein, Audibert & von
Luxburg 2007; Singer 2006). Translating the workbook's length²-unit exponent to this code's
length-unit `eps` gives exponent `d+2 = 5`, not `2.5`. This is a genuine units bug, not a tuning
choice — verified against the standard literature normalization for this exact kernel
convention. **Fixed** in `compiler/backends/desi_graph.py::normalize_continuum_limit` (exponent
now `d+2`), with the derivation recorded in the function's docstring. **This fix alone does not
achieve convergence** (Section 5) — it is applied because it is independently correct.

### 3.3 Bandwidth rule (found and fixed this investigation)

The prior bandwidth rule (`3 x median nearest-neighbour distance`) was audited via `audit_graph`
and found to produce a near-complete graph at typical N (34-65% edge density, hundreds to
1300+ average neighbours out of 2000-3000 nodes) — not a local graph suitable for approximating
a differential operator. **Fixed** to the standard "median heuristic" (`1 x median NN`, Gretton et
al.; widely used in spectral clustering / kernel methods), applied in both the pilot-fixture path
(`run_gate1_on_pilot_fixture`, now measured directly on the fixture rather than hardcoded) and all
diagnostic scripts. **This fix alone does not achieve convergence either** (Section 10), and in
one isolated standalone test (before the metric-floor fix was applied) appeared to make things
worse — later shown to be partly a metric artifact once 3.1 was fixed.

### 3.4 Stale test threshold (mechanical fix, not a methodology change)

`test_spectral_gap_convergence_with_more_points` used a fixed `1e-8` "nonzero" threshold tuned to
the old (`2.5`) exponent's eigenvalue scale. After the 3.2 fix the eigenvalues legitimately
shrink to `O(1e-13)`-`O(1e-14)` at the test's fixed `eps=150`, so every eigenvalue fell under the
stale floor and the test started failing with `NaN` gaps. Fixed to a floor relative to that run's
own eigenvalue scale, mirroring 3.1. All 95 tests pass with this fix.

### 3.5 Graph-construction algebraic audit — no anomaly found

Directly measured on the real DESI graph (N=2500, median-heuristic bandwidth):
`W_nonneg=True`, `W_symmetric=True`, `L_symmetric=True`, `L·1` max abs deviation `7.1e-15`
(float noise), `min(v^T L v)` over 200 random test vectors `= 4753.9` (positive, as required),
`n_connected_components=1`, `n_isolated_nodes=0`. **The graph construction itself is
mathematically sound** — this rules out a bare algebraic implementation error (Category A) as the
cause of the non-convergence.

## 4. CORRECTION APPLIED

Sections 3.2-3.4 are permanent, applied corrections to the canonical code
(`compiler/backends/desi_graph.py`, `compiler/backends/desi_fc005_pipeline.py`,
`compiler/tests/test_fc005_desi_graph.py`), independently justified regardless of the final
verdict. **None of them, individually or combined, resolves the Gate 1 failure.** Re-running the
live pilot-fixture Gate 1 with all corrections applied:

```
epsilon_rule: 1 x median NN separation (median-heuristic bandwidth), measured directly
              on the 3000-object fixture (50.112 Mpc), scaled by (3000/N)^(1/3)
N_values: [300, 600, 1000, 1500]
converged: False
relative_changes: [0.5587, 1.3502, 0.7028]
failed_dependency: CONTINUUM-LIMIT-L-DESI
```

Gate 1 fails after correction, at a magnitude no better than before. `status_matrix.json`
confirms `CONTINUUM-LIMIT-L-DESI = FAIL`, `MATHEMATICAL-CONVERGENCE-DESI = FAIL`, and every
downstream node (`DESI-HEAT-TRACE` through `PHYSICAL-VALIDATION-DESI`) remains `OPEN`. The
leakage-control audit passes: `FAIL` does not propagate as `CALCULATED`.

## 5. CONVERGENCE RESULTS (corrected metric, full downloaded catalogue, N=[800,1500,2500,4000])

| Configuration | relative_changes | converged |
|---|---|---|
| DESI, original exponent (2.5) | 0.658, 0.737, 0.606 | No |
| DESI, corrected exponent (5.0) | 0.360, 0.562, 0.377 | No |
| DESI, corrected exponent + interior-only (60th pct radial trim) | 0.272, 0.606, 0.312 | No |
| DESI, corrected exponent + alpha=1 density normalization | 0.352, 0.119, 0.271 | No |

No tested configuration of the real DESI catalogue converges under the pre-registered
tolerance (0.15) and monotonicity criterion.

## 6. SURVEY SELECTION / MASK (spec section 5)

DESI SGC footprint spans RA≈310°-360° and 0°-50° (wraps 0/360); naive RA-percentile trimming
would be spatially meaningless, so interior/boundary trimming used 3D Cartesian radial distance
from the point cloud centroid instead. Interior-only (innermost 60th percentile, 96,090 of
160,150 objects) relative_changes = **0.272, 0.606, 0.312**, essentially the same magnitude and
character as the full footprint (0.360, 0.562, 0.377). **Boundary trimming does not resolve the
failure — this is recorded as NOT a `BOUNDARY-INDUCED FAILURE`; Category F is ruled out as the
sole or primary cause.**

## 7. REDSHIFT SELECTION (spec section 6)

| Slice | N objects | number-density proxy | relative_changes |
|---|---|---|---|
| Full pilot [0.4, 0.6) | 160,150 | 2.081e-5 | 0.360, 0.562, 0.377 |
| Narrow [0.45, 0.55) | 78,287 | 2.034e-5 | 0.304, 0.475, 0.589 |
| Narrow [0.40, 0.50) | 68,679 | 2.078e-5 | 0.982, 0.605, 0.558 |

Failure persists at every tested redshift-slice width; narrowing the slice does not resolve
convergence (and the narrowest slice is worse, consistent with reduced N reducing achievable
resolution — Category D). No slice was combined with another in a way that changes physical
interpretation.

## 8. SYNTHETIC CONTROLS (diagnostic only — never evidence that DESI succeeds)

Identical pipeline (bandwidth rule, normalization, corrected metric) applied to matched N values.

| Control | Mechanism tested | relative_changes | converged |
|---|---|---|---|
| Uniform Euclidean box | i.i.d. uniform sampling (best case) | 0.155, 0.141, 0.182 | No (borderline) |
| Nonuniform clustered (12 Gaussian clumps) | strong density nonuniformity | 0.998, 0.999, 0.981 | No (flat, no improvement) |
| Masked (angular wedge removed) | hard boundary | 1.012, 0.350, 0.265 | No (improving trend) |
| DESI-like radial selection (uniform angle, real n(z) shape) | radial selection function alone | 0.246, 0.214, 0.132 | **Yes** |

**8.1 Selection function alone does not reproduce the failure** — the DESI-like radial-selection
control converges cleanly. Category E is ruled out as the primary cause.

**8.2 Boundary alone produces a large but improving-with-N residual**, unlike DESI's
non-monotonic pattern; combined with Section 6's interior-only result, boundary effects are not
the primary cause (Category F ruled out as sole cause), though they may be a contributing
component.

**8.3 Even i.i.d. uniform sampling is only borderline** (values straddling the 0.15 tolerance,
non-monotonic) at this N range — indicating N=800-4000 with a dense `eigh` solver is close to the
resolution floor for *any* point process under this exact estimator, not a DESI-specific defect.
This directly supports Category D as a compounding factor.

**8.4 Nonuniform density reproduces a failure of DESI's severity** (in fact worse) while the
uniform control does not. This isolates density nonuniformity / clustering, not the radial
selection function or the survey boundary, as the closest synthetic analogue to what happens
with real DESI data — supporting Category I: real galaxy large-scale structure is genuinely
clustered (non-Poisson), violating the i.i.d.-sampling assumption underlying the graph-Laplacian
convergence theorems being used.

**8.5 Tested correction: Coifman-Lafon alpha-normalization** (`alpha=1`, a standard published
density-normalized graph Laplacian construction — not invented for this task — proven under the
same asymptotic regime to converge to a density-independent Laplace-Beltrami operator). Applied
to DESI, uniform, and clustered controls:

| Dataset | alpha=0 (baseline) | alpha=1 (density-normalized) |
|---|---|---|
| DESI real | 0.360, 0.562, 0.377 | 0.352, 0.119, 0.271 |
| Uniform box | 0.155, 0.141, 0.182 | 0.136, 0.284, 0.075 |
| Nonuniform clustered | 0.998, 0.999, 0.981 | 0.992, **27.6**, 1.35 |

Density normalization does not repair DESI's convergence (still non-monotonic, last value above
tolerance), does not clean up the uniform control either, and **catastrophically destabilizes**
the clustered control (a 27.6 relative change at N=1500 — worse than the unnormalized case). This
standard correction is **not** a fix for this failure; no other established, non-invented
correction targeting the clustering mechanism was identified within the scope of this
investigation.

## 9. ALL PARAMETER SWEEPS

**9.1 Bandwidth multiplier sweep** (prior investigation phase): multiplier ≈1.0-2.0 gives a
connected-but-local graph regime; the old 3.0 multiplier gives a near-complete, non-local graph
(30-65% edge density). Median-heuristic (1.0) adopted (Section 3.3); alone insufficient.

**9.2 kNN graph sweep** (N=2000, k ∈ {8, 16, 32, 64, 128}, independent construction family from
the epsilon-ball kernel graph used elsewhere):

| k | connected (directed) | connected (symmetrized) | directed-vs-symmetrized max asymmetry | spectral gap |
|---|---|---|---|---|
| 8 | No (4 components) | Yes | 0.670 | 5.0e-18 |
| 16 | Yes | Yes | 0.532 | 5.9e-18 |
| 32 | Yes | Yes | 0.469 | 6.3e-18 |
| 64 | Yes | Yes | 0.434 | 6.4e-18 |
| 128 | Yes | Yes | 0.427 | 6.3e-18 |

`k=8` is too sparse (disconnected before symmetrization); `k>=16` connects. Directed/symmetrized
asymmetry falls as `k` grows (expected: more mutual-nearest-neighbour pairs at larger `k`).
Spectral gaps are ~5e-18 across the whole sweep — essentially at the double-precision noise floor
for this normalization scale, corroborating the resolution-limit finding (Category D) rather than
indicating a construction bug.

**9.3 N-refinement audit:** nested-subsample (N=800⊂1500⊂2500⊂4000, drawn as prefixes of one
random permutation) vs. independent fresh draws at each N were both tested; neither resolved
non-convergence. Subsample-measured NN distance changes with N as expected for true density
refinement (e.g. ~50 Mpc at N=3000-from-subsample vs. 8.4-8.65 Mpc true NN distance on the full
160,150-object catalogue) — subsampling is behaving correctly, not masking a bug.

## 10. OPERATOR-ACTION TEST (spec section 11)

Only the uniform-box control has an independently known flat-metric reference (`Delta f` exact
for polynomial test functions everywhere); DESI's point cloud has no independently known metric.

- **Linear test function** (`f=x`, `Delta f = 0` exactly): `||L_tilde f||` (absolute) `≈ 2.3e-7` at
  N=3000 — small, consistent with the expected near-zero action on locally affine functions. (A
  naively computed *relative* residual exploded to ~232,000 because it divides by
  `norm(reference)=0`; this is a metric-design artifact of testing against an exactly-zero
  reference, disclosed here rather than reported as a finding.)
- **Quadratic test function** (`f=|x|^2`, `Delta f = 6` exactly): relative residual `≈ 1.000`
  (whole-domain and interior-only both), meaning `L_tilde f` carries almost no overlap with the
  expected constant-6 signal at this N and normalization scale — the discrete operator is not yet
  recovering global curvature-scale signals even in the best-case uniform control. This is a
  resolution-limitation finding (Category D), consistent with 8.3 and 9.2, not evidence of an
  operator-construction bug (the near-zero response to affine functions is exactly the expected
  qualitative behavior).
- **DESI (no independent reference available):** reported as required — `||L_tilde f|| = 1.36e-10`
  for `f=x` (self-consistency only, no anomaly, but explicitly **not** a convergence proof, since
  no independent `Delta_h` exists for this point set's unknown metric).

## 11. EIGENVECTOR / SUBSPACE TEST (spec section 12)

Not completed to full invariant-subspace/projector comparison within this investigation's scope.
The leading nonzero eigenvalues at every tested N are non-degenerate to solver precision (no
near-clusters requiring subspace comparison were observed in the low-lying spectrum reported in
`diagnostic_full_results.json`), so naive eigenvalue-based relative-change comparison (Sections
5-9) is not confounded by eigenvector sign/ordering ambiguity for this data; a full
projector-based test was not additionally run. **This is recorded as an incomplete sub-diagnostic,
not a decided one** — see Section 15, Next Dependency.

## 12. SIGN CONVENTION RE-AUDIT (spec section 10)

Re-confirmed from the prior session's fix: the workbook's `L_tilde -> Delta_h` (negative
semidefinite), but the heat-trace eigenproblem needs `Spec(-Delta_h)` (`lambda_n >= 0`). Every
diagnostic script in this investigation diagonalizes `-L_tilde`, matching
`run_mathematical_convergence`'s convention exactly (`_low_eigen(-L_tilde, n_modes)`), never mixed
with bare `L_tilde` at any stage. No change was made to the canonical physical convention; this
section only re-verifies consistency.

## 13. NORMALIZATION / C_K AUDIT (spec section 9)

`C_K = (2*pi)^(d/2)` is the analytic second moment of the isotropic Gaussian kernel `K(u)=exp(-u/2)`
used by `build_kernel_graph` (`K(d^2/eps^2)`), verified against direct numerical integration in
`compiler/tests/test_fc005_desi_graph.py` (pre-existing test, unaffected by this investigation).
The exponent bug (Section 3.2) was a units mismatch between the workbook's kernel convention and
this code's kernel convention, not an error in `C_K` itself.

## 14. DESI RESULTS SUMMARY

Real DESI DR1 LRG SGC v1.5 catalogue, `0.4<=z<0.6`, does not show numerical evidence of
`L_tilde_(N,eps)` convergence to a continuum operator under:
- both the original and corrected normalization exponent,
- both the original and corrected (median-heuristic) bandwidth,
- an independent kNN graph-construction family,
- full-footprint and interior-only (boundary-trimmed) subsamples,
- three redshift-slice widths,
- nested and independent N-refinement,
- the standard density-normalized (alpha=1) graph Laplacian correction.

All raw run data are recorded in `FC005_CONTINUUM_FAILURE_MATRIX.csv` (76 rows) and
`data/desi/dr1/fc005/derived/{diagnostic_full_results.json, alpha_normalization_results.json,
operator_and_knn_results.json, redshift_slice_results.json}`. No failed run was removed from
provenance.

## 15. FINAL STATUS

**OPEN — not CLOSED, not FALSIFIED.**

This is not outcome D (closure): no configuration tested achieves stable convergence.

This is not a clean outcome A (implementation failure): two real, independently-justified bugs
were found and fixed (Sections 3.1-3.4), and the graph construction itself is algebraically sound
(Section 3.5), but fixing every identified bug does not produce convergence — there is no further
specific defect identified to fix.

This is not outcome B (method failure with a repair): the one standard, published, non-invented
correction that directly targets the isolated mechanism (density nonuniformity /
non-i.i.d. clustering, Coifman-Lafon alpha-normalization) was tested and does not repair
convergence — it destabilizes the closest synthetic analogue of DESI's clustering instead. No
other established, mathematically justified (i.e. not invented for this task) correction for
correlated/clustered point processes was identified within scope.

This is not outcome C (falsification): a full `FALSIFIED: CONTINUUM-LIMIT-L-DESI` verdict would
assert the physical continuum limit does not exist for this data under these assumptions. That
claim is not supportable with confidence, because the **uniform i.i.d. positive control itself
only borderline converges** at the same N range (Section 8.3) and the discrete operator does not
yet recover curvature-scale signals even in that best-case control (Section 10). The evidence is
consistent with "N=800-4000 with a dense eigensolver is an insufficient resolution regime to
decide the asymptotic claim at all, for any point process" compounded by "DESI's real clustering
makes this worse, because correlated samples carry less effective information per point than
i.i.d. samples." Both components (D and I) are evidenced; neither alone, nor together, has been
shown sufficient to prove non-existence of the limit.

`CONTINUUM-LIMIT-L-DESI` and `MATHEMATICAL-CONVERGENCE-DESI` are recorded as `Status.FAIL`
(retriable, per `ALLOWED_TRANSITIONS`), not `Status.FALSIFIED` (terminal) — this distinction is
deliberate and matches the evidence above. Gate 2 and Gate 3 remain `OPEN` and were never entered.

## 15a. FOLLOW-UP: SPARSE N-SCALING INVESTIGATION (POST-PUBLICATION UPDATE)

A dedicated follow-up (`FC005_N_SCALING_REPORT.md`) extended this investigation with a
sparse eigensolver up to N=64000 (vs. this report's dense-`eigh` ceiling of N≤4000) and a
corrected epsilon-scaling rate (`eps_N ~ N^(-1/(d+4))`, replacing a rate shown there to
violate the standard asymptotic convergence condition `N·eps_N^(d+2) → ∞`). Key findings:
the uniform IID positive control, only borderline convergent here (section 8.3), is
confirmed to converge cleanly (joint eigenvalue+eigenvector stability through mode ~11) once
N is scaled properly — confirming Category D (finite resolution) was the dominant limiting
factor at this report's N range. Real DESI data shows genuine partial convergence (modes 1–4
of 15, joint eigenvalue+eigenvector stable) at N=64000, closely paralleling but trailing the
uniform control's own outward stabilization. A naive eigenvalue-only reading of the same
data gives a **false positive** ("converged", driven by an eigenvalue-crossing artifact in
the higher modes whose invariant subspaces remain unstable — cosine 0.07–0.15, nearly
orthogonal), caught and rejected by the eigenvector/subspace test spec section 12 required.
The clustered non-i.i.d. synthetic control shows a qualitatively more severe failure (total,
persistent ARPACK non-convergence at every N tested) than DESI exhibits. See
`FC005_N_SCALING_REPORT.md` for full detail. **Status unchanged: FAIL / RETRIABLE, not
FALSIFIED, not CLOSED.**

## 16. NEXT DEPENDENCY

To move this from OPEN toward a decided CLOSURE or FALSIFIED verdict, in order of expected
diagnostic value:

1. **Scale N well beyond 4000** using a sparse iterative eigensolver (e.g. Lanczos / ARPACK via
   `scipy.sparse.linalg.eigsh` on the sparse kernel graph) rather than dense `eigh`, to test
   whether the uniform-box positive control (Section 8.3) cleanly converges at N=10,000-50,000+ —
   this would directly determine whether Category D (resolution) is the dominant limiting factor,
   independent of DESI.
2. **If the uniform control converges cleanly at larger N but DESI still does not**, that would
   be much stronger evidence toward a genuine Category I effect (or toward outcome C), since the
   resolution confound would be removed.
3. **Complete the eigenvector/invariant-subspace projector test** (Section 11) at the larger N
   from (1), to rule out spectral-instability artifacts distinct from operator non-convergence.
4. Do not re-attempt tolerance changes, cherry-picked parameter points, or synthetic substitution
   for DESI at any point in this continuation — the same prohibitions in force during this
   investigation remain in force.

---
*Generated as part of the FC-005 CONTINUUM-LIMIT-L-DESI diagnostic investigation. All numbers in
this report were produced by executing real code against real DESI DR1 data (or, where explicitly
labeled "synthetic", diagnostic-only controls never substituted for DESI) — none were asserted
from prose.*
