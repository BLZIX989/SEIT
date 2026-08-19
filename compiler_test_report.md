# Compiler Test Report

Run with: `python3 -m pytest compiler/tests -q && python3 -m compiler.run_compiler`

## Pytest

**54 / 54 passed** (unit tests for IR/status, dependency graph incl. cycle
rejection, verification, falsification protocols, target-independence
firewall; integration tests for both executable-test sweeps and the full
`run_compiler.build_and_run()` orchestration).

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

## Self-audit (spec section 36)

All 8 audits **passed** on the current build:

| audit | result |
|---|---|
| dependency_audit | pass (0 issues) |
| circularity_audit | pass — synthetic 3-cycle X→Y→Z→X correctly rejected |
| type_audit | pass (0 issues) |
| provenance_audit | pass (0 issues) |
| target_independence_audit | pass (0 issues) |
| status_audit | pass (0 issues) |
| numerical_reproducibility_audit | pass — bitwise-identical repeated runs |
| artifact_completeness_audit | pass — all 11 required JSON artifacts present |

## Registry contents (this run)

35 Objects, 7 Transformations, 2 Equations, 15 Types.

Status distribution: 26 `OPEN` (the untouched spec-section-6 template
past `SELECTION-SIGMA`, plus the not-yet-attempted `T2-REPRODUCTION`,
`T2-FORWARD-DERIVATION`, and the three named-but-unlocated NCG
obstruction artifacts), 6 `VERIFIED`, 4 `CALCULATED`, 3 `PROPOSED`
(historical claims), 3 `CONDITIONAL` (`DTC-CIRCULARITY-OBSTRUCTION` and
the two diffusion-metric candidate nodes).

## Terminal status

**CONDITIONALLY_CLOSED.** Every self-audit passes and both executable
tests are fully verified, but the build is honest that it is not
`CLOSED`: `SELECTION-SIGMA` (spec section 10) remains an unresolved
compiler component, the historical T2/NCG claims remain `PROPOSED`/`OPEN`
with no supporting executable artifact located in the repository, and the
gauge/matter/thermodynamic/cosmological engines have not been activated.
This status is computed from the actual audit and registry state in
`compiler/run_compiler.py::build_and_run` — it is never asserted.
