# FC-005 Execution Report

Run with: `python3 -m pytest compiler/tests -q && python3 -m compiler.run_compiler`

This integrates the four supplied FC-005 physics derivation workbooks
into the existing Forward-MDCL compiler (`compiler/`) and executes every
admissible calculation. It does not invent a new theory, redesign the
compiler, or force a closure result — see `compiler/ir/fc005.py` for the
registration code and `fc005_result.json` for the machine-readable
result of the run this report describes.

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

**No.** No DESI catalogue (RA, DEC, z, weights) exists anywhere in the
repository, the session workspace, or any of the four supplied
workbooks — the primary workbook's own audit sheet already records
"No catalog file present in uploaded workbook," and this build
independently confirmed the absence via filesystem search. `G_DESI` is
registered `OPEN` (node `GRAPH-G-DESI`, blocked on `DESI-CATALOGUE`).
The construction code (`compiler/backends/desi_graph.py`) is
implemented and unit-tested on synthetic point clouds only.

## C. Was L_DESI successfully constructed?

**No** — blocked on B. Node `OPERATOR-L-DESI`, status `OPEN`.

## D. Did L_DESI converge toward a continuum Laplacian?

**Not applicable / not tested.** No data to test convergence against.
`CONTINUUM-LIMIT-L-DESI`, status `OPEN`.

## E. Did the spectrum converge?

**Not applicable for DESI** (blocked on B). For the **S^3 control**,
yes: the analytic spectrum is exact by construction; the heat-trace
fit converges to the exact coefficients as the fit degree increases
(degree 2 → |E_κ|~1e-3, degree 4/5 → |E_κ|~1e-8/1e-9).

## F. Were a0, a1, a2 stable?

For the **S^3 control**: yes, to the tolerances above, across all four
fit windows and a degree-2..6 sweep. For **DESI**: not computed
(blocked on B).

## G. Was κ stable?

For **S^3**: yes (κ(a1) and κ(a2) agree to ~1e-5 relative across all
four windows). For **DESI (κ_spectral)**: not computed.

## H. Did E_κ satisfy the predefined tolerance?

**Yes, for the S^3 control** (tolerance 1e-4, defined *before* running
the sweep, per spec section 17): max|E_κ| = 1.019e-05. **Not applicable
for DESI** — no E_κ_DESI was computed.

## I. Did κ_spectral agree with an independent cosmological constraint?

**Not computed.** Requires κ_spectral from real DESI data (B), which
was never constructed. `DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK`, status
`OPEN`.

## J. Which links are CLOSED?

None. Per spec section 17, `CLOSED` requires the *complete* chain
(including the DESI/cosmological links) to converge within predefined
tolerances; that chain is blocked at G_DESI. The compiler's terminal
status is `CONDITIONALLY_CLOSED` (see `compiler_test_report.md`), never
forced to `CLOSED`.

## K. Which are CONDITIONAL?

The general continuum-limit and spectral-convergence *equations*
(EQ-013, EQ-014, EQ-Δ_h-limit — bulk-imported, `PROPOSED` pending
independent execution) are registered as requiring conditions
(adequate sampling, ε→0, isolated eigenvalues) that are stated but not
empirically validated absent real data.

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

- The full DESI discrete-to-continuum chain (10 nodes, B through I),
  blocked on the missing catalogue.
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

**A real DESI (or equivalent) galaxy-level catalogue with RA, DEC, z,
and survey weights (w_FKP, w_sys).** This is the single missing
dependency blocking every downstream FC-005 link (C through J). Nothing
else in the chain is blocked for a mathematical reason — the S^3
control demonstrates the operator/spectral/heat-trace/curvature-closure
machinery itself is correct and executes cleanly; `compiler/backends/
desi_graph.py` is ready to run the identical pipeline the moment a
catalogue is supplied, with no code changes required.

## Self-audit

All 9 self-audits pass after FC-005 integration (dependency,
circularity, type, provenance, target-independence, status,
**leakage-control** [new], numerical-reproducibility,
artifact-completeness). See `self_audit_report.json` and
`compiler_test_report.md` for the full run. 83/83 pytest tests pass
(54 pre-existing + 29 new FC-005 tests).
