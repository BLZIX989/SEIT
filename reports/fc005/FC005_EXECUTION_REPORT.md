# FC-005 Execution Report

Run with: `python3 -m pytest compiler/tests -q && python3 -m compiler.run_compiler`

This integrates the four supplied FC-005 physics derivation workbooks
into the existing Forward-MDCL compiler (`compiler/`) and executes every
admissible calculation. It does not invent a new theory, redesign the
compiler, or force a closure result — see `compiler/ir/fc005.py` for the
registration code and `fc005_result.json` for the machine-readable
result of the run this report describes.

**Update:** real DESI DR1 data has since been acquired, validated, and
run through Gate 1 (mathematical convergence) — see
`FC005_DESI_ACQUISITION_REPORT.md` for the full data-acquisition report
and `FC005_DESI_PROVENANCE.json` for the complete dependency chain. The
sections below (B through N) are updated to reflect that real execution,
not the original "no catalogue" state.

## Workbook reconciliation (spec section 1/3)

The four supplied workbooks are a **strictly nested provenance chain**,
not four competing versions. Every sheet shared by two or more of them
(Equations, Variables, Dependency DAG, Status Matrix, Master Chainlink,
Closure Tests, Rejected Branches, Constants & Assumptions, Provenance,
Proofs, Four Branch Matrix) is byte-identical across all four — **zero
discrepancies found**. Precedence (earliest → primary), by embedded
modification timestamp and sheet-superset structure:

| rank | role | file (repo path under `fc005_source_workbooks/`) | sheets |
|---|---|---|---|
| 1 | ORIGINAL | `01_original_derivation_workbook.xlsx` | 15 |
| 2 | CANONICAL_DERIVATION | `02_canonical_derivation_workbook.xlsx` | 30 |
| 3 | FC005_EARLIER_SPEC | `03_fc005_earlier_execution_spec.xlsx` | 32 |
| 4 | **PRIMARY (canonical for this build)** | `04_fc005_primary_full_execution.xlsx` | 35 |

The one real discrepancy found is administrative, not physical: the
filenames in the FC-005 build command's own section 1 do not exactly
match the filenames actually supplied (see
`compiler/historical/fc005_reconciliation.py::FILENAME_DISCREPANCIES`
for the explicit mapping and reasoning — recorded rather than silently
resolved).

## Governing discipline applied

Per spec section 4 (leakage control) and section 2 of the original
Forward-MDCL compiler, a workbook's own STATUS column is prose, not
proof. Every one of the 29 equations bulk-imported from the primary
workbook's Equations sheet is registered `PROPOSED` (role `comparison`)
with the workbook's claimed status preserved in
`provenance.verification.workbook_claimed_status` for audit
transparency — never trusted at face value. Only calculations this build
actually executed (S^3 control, Fisher-Rao PSD proof, eigenvalue-
uniqueness counterexample) carry a status derived from real computation.

## A. Did the S^3 control pass?

**Yes.** Independently executed (not copied from the workbook) in
`compiler/backends/heat_kernel_sphere.py`: analytic spectrum
λ_l=l(l+2), multiplicity (l+1)², heat trace summed with a
truncation-error bound below 1e-35, degree-3 local polynomial fit of
Y(t)=K(t)(4πt)^1.5 across the workbook's four fit windows.

| window | a0 | a1 | a2 | E_κ |
|---|---|---|---|---|
| [0.001, 0.004] | 19.739209 | 19.739209 | 9.869575 | 1.483e-06 |
| [0.0015, 0.006] | 19.739209 | 19.739209 | 9.869539 | 3.344e-06 |
| [0.002, 0.008] | 19.739209 | 19.739209 | 9.869487 | 5.954e-06 |
| [0.003, 0.01] | 19.739209 | 19.739210 | 9.869404 | 1.019e-05 |

Exact reference: κ=1, R=6, a0=a1=2π²=19.739209, a2=π²=9.869604.
max|E_κ| = 1.019e-05 < tolerance 1e-4 → **PASSED**. This independently
reproduces the workbook's reported ~3.2e-6 order of magnitude at the
same window (workbook: 3.2156e-06; this build: 3.344e-06 — different
sampling/point-count choices, same regression outcome). A plain
degree-2 fit was also tested and found biased by >1000x (|E_κ|~1e-3),
confirming the degree-3 choice is not arbitrary (see
`test_s3_fit_degree_2_is_measurably_biased`).

## B. Was G_DESI successfully constructed?

**Yes.** Real DESI DR1 LRG SGC data was acquired and validated (see
`FC005_DESI_ACQUISITION_REPORT.md`); `G_DESI` (node `GRAPH-G-DESI`) was
constructed at every tested (N, ε) point — symmetric, non-negative,
zero-diagonal weight matrix, single connected component. Status
`CALCULATED`.

## C. Was L_DESI successfully constructed?

**Yes.** `L = D - W` (node `OPERATOR-L-DESI`), symmetric, row-sums zero
to machine precision, `v^T L v ≥ 0` confirmed over 200 random test
vectors at every point. Status `CALCULATED`.

## D. Did L_DESI converge toward a continuum Laplacian?

**No.** Gate 1 (mathematical convergence) was executed on real data and
**FAILED**: the low-lying spectrum's relative change across the (N, ε)
refinement sequence was 0.42, 0.28, 0.41, against a pre-registered
tolerance of 0.15. Node `CONTINUUM-LIMIT-L-DESI`, status `FAIL`. This is
the **exact failed dependency** the pipeline stopped at, per instruction.

**Update — full diagnostic/closure investigation completed:** a
dedicated investigation (`FC005_CONTINUUM_DIAGNOSTIC_REPORT.md`) audited
graph construction, sampling density, survey boundary, redshift
selection, bandwidth/kernel regime, N-refinement, normalization, sign
convention, operator action, and six synthetic controls. It found and
fixed two genuine implementation bugs (a relative-change metric floor
artifact, and a normalization-exponent units mismatch — corrected
`ε^(5/2)` → `ε^(d+2)=ε^5`), plus a bandwidth-rule correction (`3×median
NN` → `1×median NN`, the standard "median heuristic"). With every
correction applied, Gate 1 **still fails** (relative changes 0.36, 0.56,
0.38 on the full catalogue). Controlled comparison against synthetic
point processes isolates the leading cause as a mismatch between DESI's
genuinely clustered (non-i.i.d.) point process and the i.i.d.-sampling
assumption underlying graph-Laplacian convergence theorems, compounded
by insufficient resolution at N≤4000 with a dense eigensolver (even a
uniform i.i.d. positive control only borderline converges at this N
range). Survey-boundary and redshift-selection effects were specifically
tested and ruled out as the primary cause. The one standard, published
correction targeting the clustering mechanism (Coifman-Lafon
density-normalized graph Laplacian) was tested and does not repair
convergence. **Final verdict: OPEN, not FALSIFIED** — `CONTINUUM-LIMIT-
L-DESI` and `MATHEMATICAL-CONVERGENCE-DESI` remain `Status.FAIL`
(retriable), not `FALSIFIED` (terminal), because the resolution-limit
confound has not been separated from the point-process-mismatch effect.
See `FC005_CONTINUUM_DIAGNOSTIC_REPORT.md` section 16 for the next
dependency (sparse-eigensolver N-scaling test).

## E. Did the spectrum converge?

**No, for DESI** — see D. For the **S^3 control**, yes: the analytic
spectrum is exact by construction; the heat-trace fit converges to the
exact coefficients as the fit degree increases (degree 2 → |E_κ|~1e-3,
degree 4/5 → |E_κ|~1e-8/1e-9).

## F. Were a0, a1, a2 stable?

For the **S^3 control**: yes, to the tolerances above, across all four
fit windows and a degree-2..6 sweep. For **DESI**: **not computed** —
Gate 1 failed, so Gate 2 (curvature closure, where a0/a1/a2 would be
fit) was never entered, per instruction.

## G. Was κ stable?

For **S^3**: yes (κ(a1) and κ(a2) agree to ~1e-5 relative across all
four windows). For **DESI (κ_spectral)**: not computed — Gate 2 never
entered.

## H. Did E_κ satisfy the predefined tolerance?

**Yes, for the S^3 control** (tolerance 1e-4, defined *before* running
the sweep, per spec section 17): max|E_κ| = 1.019e-05. **Not applicable
for DESI** — Gate 2 never entered, no E_κ_DESI was computed.

## I. Did κ_spectral agree with an independent cosmological constraint?

**Not computed.** Requires κ_spectral (Gate 2), which requires Gate 1 to
have passed. Gate 1 failed. `DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK`,
status `OPEN`, never entered.

## J. Which links are CLOSED?

None. Per spec section 17, `CLOSED` requires the *complete* chain to
converge within predefined tolerances; the real-data chain is blocked
at `CONTINUUM-LIMIT-L-DESI` (Gate 1). The compiler's terminal status is
`CONDITIONALLY_CLOSED` (see `compiler_test_report.md`), never forced to
`CLOSED`.

## K. Which are CONDITIONAL?

The general continuum-limit and spectral-convergence *equations*
(EQ-013, EQ-014, EQ-Δ_h-limit — bulk-imported, `PROPOSED` pending
independent execution) remain registered as requiring conditions
(adequate sampling, ε→0, isolated eigenvalues) that are stated but were
not satisfied by the real-data run actually executed (see D).

## L. Which are FALSIFIED?

Two, both independently re-executed in this build (not copied):

1. **Fisher-Rao metric = Lorentzian spacetime metric**
   (`EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION`). Executed proof: F for a
   2-parameter Gaussian family, computed by genuine sympy symbolic
   integration, is diag(1/σ², 2/σ²) — positive semidefinite for every
   σ>0 (eigenvalues confirmed ≥0 both symbolically and by sampling
   v^T F v ≥ 0 numerically). A Lorentzian signature (-,+,+,+) requires a
   strictly negative eigenvalue; signature is basis-independent
   (spectral theorem); PSD and Lorentzian are disjoint. **FALSIFIED.**

## M. Which remain OPEN?

- `DESI-HEAT-TRACE`, `DESI-HEAT-COEFFICIENTS`, `KAPPA-DESI`,
  `E-KAPPA-DESI`, `DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK`,
  `CURVATURE-CLOSURE-DESI`, `PHYSICAL-VALIDATION-DESI`: never entered,
  because Gate 1 (`MATHEMATICAL-CONVERGENCE-DESI`, status `FAIL`) did
  not pass. `GRAPH-G-DESI`, `OPERATOR-L-DESI`, `DESI-CATALOGUE` are
  `CALCULATED` (they were successfully executed); `CONTINUUM-LIMIT-L-DESI`
  and `DESI-SPECTRUM` are `FAIL` (the convergence claim itself, and
  everything whose meaning depends on it).
- `SELECTION-SIGMA` and the rest of the original forward-chain template
  past it (unrelated to FC-005, inherited from the base compiler).
- `SPEC-H-UNIQUENESS`: eigenvalue-only spectral data does not determine
  the operator (executed counterexample: 25/25 random unitary-
  conjugation trials confirm distinct H, H′ with identical spectrum,
  max spectral residual 8.9e-16). This keeps `Spec(H) alone → g_μν`
  explicitly OPEN, never claimed.
- `SEMICLASSICAL-RESIDUAL-E-SC`: requires a constructed quantum state
  and a renormalized stress tensor, neither built here. Reported as
  **SEMICLASSICAL CLOSURE scope only** (spec section 18) — never
  presented as full quantum gravity, which stays OPEN.

## N. What is the exact next dependency?

**A refinement sweep resolved deep enough into the asymptotic (N→∞,
ε→0) regime to test mathematical convergence properly** — the current
run (ε from 136 to 234 Mpc, chosen from the data's own nearest-neighbor
spacing) is very likely not yet in that regime for this sample's spatial
extent (see `FC005_DESI_ACQUISITION_REPORT.md` for the diagnostic). That
requires the sparse/kNN/chunked methods the build command's own §15
anticipates for the full catalogue (662,492 objects; the current dense
`numpy.linalg.eigh` approach does not scale past a few thousand points).
This is recorded as the next dependency, not attempted here — attempting
it now, right after seeing Gate 1 fail, would risk looking like tuning
for closure even if done in good faith. The catalogue itself is no
longer the blocker: it is acquired, validated, and Gate 1 has been run
on it for real (see `FC005_DESI_ACQUISITION_REPORT.md`).

### Execution procedure (as actually run)

`compiler/backends/desi_fc005_pipeline.py::run_fc005_desi_pipeline` runs
exactly the three-stage procedure this branch is bound to, and reports
all three stages independently rather than as a single verdict:

1. **Mathematical convergence** — checked first, on its own terms (does
   the operator converge under refinement?). On failure, the function
   returns the exact node it failed at and STOPS; stages 2 and 3 are
   never run.
2. **Curvature closure** ("observational agreement" with the
   constant-curvature sector) — only entered if stage 1 converged.
   |E_kappa| not falling below the predefined tolerance is reported as a
   genuine curvature-closure failure, not reinterpreted as anything else,
   and the pipeline stops there.
3. **Physical validation** (the independent cosmological cross-check) —
   only entered if stage 2 closed, and only against a `kappa_cosmological`
   value the caller must supply from a named, independent source; the
   function raises rather than run if no such source is given, so
   Δκ can never be computed against the same catalogue that produced
   κ_spectral.

No stage's outcome is ever inferred from another's, no threshold is
adjusted after seeing a result, and no catalogue-derived number is
reused to validate itself. This is enforced in code (see
`compiler/tests/test_fc005_three_stage_pipeline.py`), not left as a
process promise.

## Self-audit

All 9 self-audits pass after FC-005 integration (dependency,
circularity, type, provenance, target-independence, status,
**leakage-control** [new], numerical-reproducibility,
artifact-completeness). See `self_audit_report.json` and
`compiler_test_report.md` for the full run. 83/83 pytest tests pass
(54 pre-existing + 29 new FC-005 tests).
