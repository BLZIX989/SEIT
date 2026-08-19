# Compiler Test Report

Run with: `python3 -m pytest compiler/tests -q && python3 -m compiler.run_compiler`

## Pytest

**92 / 92 passed** (54 pre-existing unit/integration tests for IR/status,
dependency graph incl. cycle rejection, verification, falsification
protocols, target-independence firewall, and both executable-test
sweeps; 38 FC-005 tests, including 8 for the three-stage DESI execution
procedure — see `FC005_EXECUTION_REPORT.md` for the physics results
these tests check).

## Test 1 — graph → L=D-A → Spec(L) → e^{-tL} → P_ker(L)

14/14 sweep cases passed (spec section 31 requires multiple sizes and
topologies, exact arithmetic where possible, independent numerical
verification — all three are present):

| topology | n | spectral gap | passed |
|---|---|---|---|
| path | 4 | 0.5858 | yes |
| path | 10 | 0.0979 | yes |
| path | 25 | 0.0158 | yes |
| cycle | 5 | 1.382 | yes |
| cycle | 12 | 0.2679 | yes |
| cycle | 30 | 0.0437 | yes |
| complete | 5 | 5.0 | yes |
| complete | 9 | 9.0 | yes |
| star | 6 | 1.0 | yes |
| star | 15 | 1.0 | yes |
| grid2d | 3×3 | 1.0 | yes |
| grid2d | 5×5 | 0.382 | yes |
| erdos_renyi | 8 (seed 42) | 1.4384 | yes |
| erdos_renyi | 20 (seed 42) | 3.3308 | yes |

Each case checks: `L phi_n = lambda_n phi_n` residual < 1e-6;
`R(t) phi_n = e^{-t lambda_n} phi_n` residual < 1e-6; the
symmetric/positive-semidefinite hypotheses for kernel convergence are
checked programmatically (not assumed); `e^{-tL} -> P_ker(L)` residual
< 1e-6 once t is scaled to the graph's own relaxation time `1/gap`; and,
for every graph with ≤ 8 vertices, the numeric eigenvalues are
cross-checked against sympy's exact characteristic-polynomial eigenvalues.

## Test 2 — Spec(L) → diffusion distance → metric candidate

Classification (spec section 32 forbids ever inferring "exact" from
numerical resemblance — none of these are):

| topology | classification | free-parameter sensitivity (spread) |
|---|---|---|
| cycle | non_unique | 0.556 |
| path | non_unique | 0.565 |
| grid2d | non_unique | 0.620 |

On every topology tested, the limiting normalized nearest-neighbor
diffusion distance depends materially (>5% relative spread) on the
arbitrary diffusion-time parameter. No canonical time choice is derived
upstream in this build, so **no single metric candidate is selected** —
this is registered as a falsification of the uniqueness claim, not
hidden.

## Falsification records

4 registered:

- `FALS-METRIC-UNIQUENESS-{cycle,path,grid2d}` (structural elimination):
  **failed** — the diffusion-time parameter is not uniquely determined,
  so the metric-candidate construction is non-unique on every topology
  tested.
- `FALS-SPECTRUM-RELABELING-INVARIANCE` (representation invariance):
  **passed** — `Spec(L)` for a 10-cycle is confirmed invariant under 4
  random vertex relabelings, as required of a genuine structural
  invariant.

## FC-005 physics integration

The four supplied FC-005 physics derivation workbooks are reconciled and
integrated into this same MDCL — see `FC005_EXECUTION_REPORT.md` and
`FC005_DESI_ACQUISITION_REPORT.md` for the full results:

- S^3 heat-kernel control regression test: **passed**, max|E_κ|=1.019e-05.
- Real DESI DR1 LRG SGC data: **acquired, checksum-verified, and
  validated** (12/12 checks). `G_DESI`/`L_DESI` **successfully
  constructed** on real data. Gate 1 (mathematical convergence):
  **executed on real data, FAILED** (relative spectral change did not
  fall below the pre-registered tolerance across the refinement
  sequence); exact failed node `CONTINUUM-LIMIT-L-DESI`. Gates 2 and 3
  correctly never entered.
- Fisher-Rao→Lorentzian identification: **FALSIFIED**, executed via
  genuine sympy symbolic integration.
- Eigenvalue-uniqueness: **OPEN**, executed unitary-conjugation
  counterexample, 25/25 trials confirmed.

## Self-audit (spec section 36 + FC-005 build command section 4)

All 9 audits **passed** on the current build:

| audit | result |
|---|---|
| dependency_audit | pass (0 issues) |
| circularity_audit | pass — synthetic 3-cycle X→Y→Z→X correctly rejected |
| type_audit | pass (0 issues) |
| provenance_audit | pass (0 issues) |
| target_independence_audit | pass (0 issues) |
| status_audit | pass (0 issues) |
| leakage_control_audit | pass — no FALSIFIED/FAIL node is a transitive ancestor of any active (VERIFIED/DERIVED/CALCULATED) node |
| numerical_reproducibility_audit | pass — bitwise-identical repeated runs |
| artifact_completeness_audit | pass — all 12 required JSON artifacts present |

## Registry contents (this run)

58 Objects, 8 Transformations, 34 Equations, 25 Types.

Status distribution: 35 `OPEN` (includes `CURVATURE-CLOSURE-DESI` and
`PHYSICAL-VALIDATION-DESI` — never entered since Gate 1 failed — plus
everything downstream of `CONTINUUM-LIMIT-L-DESI`), 35 `PROPOSED`
(mostly the 29 bulk-imported FC-005 reference equations plus historical
claims, never trusted above PROPOSED without independent execution),
12 `VERIFIED`, 10 `CALCULATED` (includes `DESI-CATALOGUE`,
`GRAPH-G-DESI`, `OPERATOR-L-DESI` — real data, successfully executed),
3 `CONDITIONAL`, 3 `FAIL` (`CONTINUUM-LIMIT-L-DESI`, `DESI-SPECTRUM`,
`MATHEMATICAL-CONVERGENCE-DESI` — Gate 1 genuinely failed on real DESI
data; `leakage_control_audit` confirms the FAIL status correctly stops
at these nodes and never propagates into an active downstream
calculation), 1 `DERIVED`, 1 `FALSIFIED`
(`EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION`).

## Terminal status

**CONDITIONALLY_CLOSED.** Every self-audit passes and both the original
executable tests and the S^3 control regression test are fully verified,
but the build is honest that it is not `CLOSED`: `SELECTION-SIGMA` (spec
section 10) remains an unresolved compiler component, the historical
T2/NCG and FC-005 reference-equation claims remain `PROPOSED`/`OPEN` with
no supporting executable artifact located in the repository, Gate 1 of
the real-data DESI discrete-to-continuum chain genuinely failed
(`CONTINUUM-LIMIT-L-DESI`, status `FAIL` — see
`FC005_DESI_ACQUISITION_REPORT.md`), and the gauge/matter/thermodynamic/
cosmological engines have not been activated. This status is computed
from the actual audit and registry state in
`compiler/run_compiler.py::build_and_run` — it is never asserted.
