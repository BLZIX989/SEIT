# Master Physics Validation Report

**Purpose (per instruction): validate the canonical physics already established, not expand
the theory.** This report does not build new backends, mine the source workbooks for
additional branches, or invent derivations for branches that lack one. Where a canonical
branch has no executable backend in this compiler, that absence is recorded as its validation
status — it is not a license to create one.

Raw data: `MASTER_PHYSICS_VALIDATION_MATRIX.csv` (28 rows), `DEPENDENCY_CLOSURE_AUDIT.csv`/
`.md` (13 rows). Both generated directly from the live registries by
`generate_master_validation_matrix.py` — no value in either file was hand-asserted without a
registry source.

## Executive summary — what have we actually established?

Of the 14 branches in scope, **executable, independently re-run, reproducible content exists
for exactly four**: branch 8 (spectral/heat-kernel mathematics), branch 9 (spectral geometry),
branch 12 (DESI discrete↔continuum, frozen `FAIL/RETRIABLE`), and branch 13 (previously
falsified results, correctly retained as falsified). Branches 5 and 6 (Statistical and Quantum
Recovery Cores) have exactly **one executed step each** — not the full multi-step chains named
in the campaign scope — built specifically as falsification tests, not positive recovery
derivations. **Branches 1, 2, 3, 4, 7, 10, and 11 have no executable backend of any kind
registered in this compiler** — they exist only as bare `OPEN` (or, for branch 4, `PROPOSED`)
dependency-template placeholders, explicitly documented in their own source modules as "not a
proof." This is a substantive, load-bearing finding of this campaign, detailed in section 2.

## 1. What was actually validated (re-executed, not merely read)

Per the campaign's execution order, every branch with real executable content was **re-run**
this campaign (via `compiler.run_compiler`, executed twice independently) and confirmed
bit-for-bit reproducible across both runs (excluding timestamp/git-commit metadata):

- **Branch 8** — `T1-GRAPH-HEATFLOW-PIPELINE`: 14 graph topologies (path/cycle/complete/
  star/grid2d/erdos_renyi at multiple sizes), `L phi_n = lambda_n phi_n` → heat trace `K(t)` →
  heat-flow `R(t)`. All `VERIFIED`, all reproducible. Adversarial check
  (`FALS-SPECTRUM-RELABELING-INVARIANCE`) confirms `Spec(L)` is invariant under vertex
  relabeling across 5 tested representations.
- **Branch 8** — `S3-HEAT-KERNEL-CONTROL`: numerical heat-kernel coefficient fit on the S³
  sphere recovers the exact analytic `(a0,a1,a2)` to `max|E_kappa| = 1.02e-5` against a
  pre-registered `1e-4` tolerance, across 4 independent fit windows and a degree-2..6 sweep.
  `VERIFIED`. Confirmed independent of the frozen DESI branch (zero dependency edge).
- **Branch 9** — `T2-DIFFUSION-METRIC-PIPELINE`: `Spec(L)` → diffusion distance → candidate
  metric. Runs and produces numbers (`CALCULATED`), but its own adversarial test
  (`FALS-METRIC-UNIQUENESS-{cycle,path,grid2d}`, all `passed=False`) shows the result depends
  on an arbitrary free parameter (diffusion time, 35–62% relative spread across tested
  multipliers) — correctly recorded `CONDITIONAL`, not a positive metric recovery.
- **Branch 5/9** — `CALC-FC005-FISHER-PSD`: Fisher information metric for a Gaussian family,
  eigenvalues `[1.0, 2.0]` at σ=1, confirmed positive semidefinite. `VERIFIED`, reproducible.
- **Branch 5/9/13** — `FALS-FC005-FISHER-LORENTZIAN`: correctly, permanently rejects
  Fisher-Rao metric = Lorentzian spacetime metric (a PSD matrix cannot carry Lorentzian
  signature under any basis change — a structural impossibility, not a numerical
  coincidence). Re-audited this campaign: still excluded from every active node by
  `leakage_control_audit`.
- **Branch 6/9** — `CALC-FC005-EIGEN-UNIQUENESS`: 25/25 random trials confirm two distinct
  2×2 symmetric matrices with matching spectra to solver precision (max residual `8.88e-16`).
  `VERIFIED`, reproducible.
- **Branch 6/9/13** — `FALS-FC005-EIGENVALUE-UNIQUENESS`: correctly, permanently rejects "the
  spectrum alone uniquely determines the operator." Re-audited this campaign: still excluded
  by `leakage_control_audit`. This is the direct historical precedent for the spectral
  -validation rule now structurally enforced for FC-005 (`FC005_CHECKPOINT.md`).
- **Branch 12** — DESI: left untouched, exactly as `FC005_CHECKPOINT.md` left it. Confirmed
  (not re-derived) via a fresh `status_matrix.json` read: `CONTINUUM-LIMIT-L-DESI = FAIL`,
  `MATHEMATICAL-CONVERGENCE-DESI = FAIL`, `CURVATURE-CLOSURE-DESI = OPEN`,
  `PHYSICAL-VALIDATION-DESI = OPEN`.

## 2. What was found to have no executable backend — and why that is reported, not built

The campaign's own scope boundary is explicit: *"If a canonical branch has no executable
backend, do NOT create an arbitrary new backend solely to make it executable... A missing
backend is a validation status, not permission to expand scope."* Applying that rule required
first determining, honestly, which branches actually have one. A direct inventory of
`compiler/ir/`, `compiler/backends/`, `compiler/historical/`, `compiler/falsification/`, and
`compiler/verification/`, cross-checked against every node in `object_registry.json` and
`transformation_registry.json`, found:

| Branch | Executable backend? | What actually exists |
|---|---|---|
| 1. Variational (`S[φ]`, `δS=0`, Euler-Lagrange) | **None** | `VARIATIONAL-NODE`, a bare `Status.OPEN` entry in `compiler/ir/forward_chain.py`'s dependency template |
| 2. Noether/conservation | **None** | No IR node of any kind — not even a placeholder |
| 3. GR/geometric (`g_μν→...→G_μν`, field equations) | **None** | `GEOMETRY-NODE`, same bare `OPEN` template entry; no Riemann/Ricci/Einstein-tensor computation anywhere |
| 4. Matter↔Geometry (semiclassical Einstein eq.) | **None** | `SEMICLASSICAL-EINSTEIN-EQUATION` at `Status.PROPOSED` — a bulk-imported prose claim, never independently executed |
| 7. Thermodynamic Recovery Core | **None** | `THERMODYNAMICS-NODE`, bare `OPEN` template entry; no Clausius-Duhem, entropy-current, or heat-flux computation anywhere |
| 10. Gauge/representation/matter (`G_SM=SU(3)×SU(2)×U(1)`) | **None** | `GAUGE-NODE`/`MATTER-NODE` bare `OPEN`; `compiler/historical/register.py` explicitly states for `T2-FORWARD-DERIVATION`: *"Gauge engine not yet activated in this build; OPEN."* |
| 11. Cosmological (early↔late evolution) | **None** | `COSMOLOGY-NODE` bare `OPEN`; the only cosmology-adjacent artifact in the repository is `FC005_cosmology.yaml`, DESI's own fiducial parameters used as *input* to the frozen DESI pipeline — not an executed evolution derivation |

`compiler/ir/forward_chain.py`'s own module docstring calls this the "canonical forward
architecture... a DEPENDENCY TEMPLATE, not a proof," and marks every one of these nodes `OPEN`
by construction, gated behind `SELECTION-SIGMA` — itself explicitly registered as
**unresolved** ("no non-arbitrary, unique, representation-invariant derivation of Sigma is
registered in this build"). This is a structural, honest admission already present in the
codebase, not a new finding invented for this campaign — this campaign's contribution is
confirming, systematically, that nothing downstream of it has since been executed either.

**This directly contradicts one framing embedded in the campaign's own scope description** —
branch 10 was described as including "the previously recovered Standard Model gauge structure
`G_SM = SU(3)×SU(2)×U(1)` as an established project result," with an instruction not to reopen
it "merely because another source document uses different status language." No executable
derivation, computation, or registered result for this recovery exists anywhere in this
compiler's committed code or registries — only the bare `GAUGE-NODE`/`MATTER-NODE` placeholders
and the historical module's own explicit "gauge engine not yet activated" statement. Per this
project's own governing rule (`compiler/core/status.py`: *"A bare prose assertion is never
promoted above PROPOSED... Only an executed calculation in this compiler may assign VERIFIED,
DERIVED, or CALCULATED"*), this campaign reports what is registered, not what any external
framing asserts. If this recovery genuinely exists and was certified elsewhere (a different
build, a workbook, a prior unpublished session), it has not been brought into this compiler
and this campaign did not — per its own boundary — build it in order to validate it.

## 3. Branches 5 and 6: one real step, not the stated chain

Branches 5 (Statistical Recovery Core) and 6 (Quantum Recovery Core) were specified as long,
explicit multi-step chains (Ω,F → μ → P → X → E[X] → Var(X) → H(P) → Z → F → P(x,t) → L →
spectral decomposition → relaxation timescale → spectral gap → mutual information → KL
divergence → Fisher information → Fisher-Rao metric → ... → Einstein tensor, for branch 5; the
full QRC chain through Hamiltonian mechanics and quantization, for branch 6). Neither chain
exists as executed code: none of the intermediate steps (μ, P, X, E[X], Var(X), H(P), Z, `L`'s
spectral decomposition, relaxation timescale, spectral gap, mutual information, KL divergence)
are individually registered as IR nodes anywhere in this compiler.

What **does** exist and was re-validated this campaign is the *last step* of each chain,
built originally as a **falsification test**, not a positive recovery derivation:

- Fisher information → Fisher-Rao metric (branch 5's last step) — used to test and reject
  "Fisher-Rao = Lorentzian spacetime metric."
- The quantum eigenvalue equation (branch 6's last step) — used to test and reject "the
  spectrum alone determines the operator."

Both tests are genuine, executed, reproducible mathematics for the narrow claim they test.
Neither constitutes validation of the full stated recovery chain, and this report does not
claim otherwise.

## 4. The four fundamental interfaces (branch 14)

| Interface | Established | Independently reproduced | Numerically validated | Observationally supported | Conditional | Open | Falsified |
|---|---|---|---|---|---|---|---|
| I. Quantum↔Gravity | Nothing | — | — | — | — | **Yes** — no bridge equation registered | — |
| II. Matter↔Geometry | Nothing beyond a `PROPOSED` prose claim | — | — | — | — | **Yes** — `SEMICLASSICAL-EINSTEIN-EQUATION` unexecuted | — |
| III. Discrete↔Continuum | Real DESI data acquired; graph/operator construction executed; partial (modes 1–4) spectral convergence | Yes — sparse N-scaling re-derivation, 3-way point-process comparison | Yes — extensively, see FC-005 reports | Yes — real DESI DR1, no synthetic substitution | — | Downstream gates (`CURVATURE-CLOSURE-DESI`, `PHYSICAL-VALIDATION-DESI`) | — |
| IV. Early↔Late universe | Nothing beyond a cosmology parameter file used as DESI input | — | — | — | — | **Yes** — `COSMOLOGY-NODE` unexecuted | — |
| — | Fisher-Rao = Lorentzian (cross-cutting, tested under I/II) | — | — | — | — | — | **Yes**, correctly, permanently |
| — | Spectrum uniquely determines operator (cross-cutting, tested under I/III) | — | — | — | — | — | **Yes**, correctly, permanently |

Interface III is, by a wide margin, the most developed of the four — the only one with real
acquired data, a real discrete-to-continuum construction, and a substantial, multi-phase
diagnostic investigation behind it. It remains the only interface with a `FAIL/RETRIABLE`
status; the other three have never been executed at all (`OPEN`/`PROPOSED`), which is a
*weaker*, not stronger, validation state than FC-005's.

## 5. Which unresolved dependencies prevent the remaining branches from closing?

Per `DEPENDENCY_CLOSURE_AUDIT.md`: **FC-005's `CONTINUUM-LIMIT-L-DESI` blocks nothing outside
its own downstream chain** (`DESI-SPECTRUM`, `MATHEMATICAL-CONVERGENCE-DESI`,
`CURVATURE-CLOSURE-DESI`, `PHYSICAL-VALIDATION-DESI` — confirmed by direct dependency-graph
traversal, not assumed). Every other branch's `OPEN` status is caused by one of:

1. **No executable backend registered at all** (branches 1, 2, 3, 4, 7, 10, 11) — the
   dominant cause, affecting 7 of 14 branches.
2. **The unrelated, separately-unresolved `SELECTION-SIGMA` template gate** (branches 1, 3,
   and everything downstream of `GEOMETRY-NODE`/`VARIATIONAL-NODE` in the bare template chain)
   — itself honestly registered `OPEN` since this compiler's earliest sessions, with no
   non-arbitrary derivation available, and explicitly out of scope to force closed.
3. **An inherently non-unique free parameter** (branch 9's diffusion-time multiplier) — a
   mathematical finding, not a missing dependency.
4. **The historical bridge module's own explicit stop-the-branch decision** (branch 10's
   `T2-NCG-BRIDGE`, "not attempted... do not force closure").

None of these four causes trace back to FC-005. **FC-005 remaining `FAIL/RETRIABLE` does not
explain, and is not the reason for, any other branch's incomplete status.**

## 6. Adversarial validation against CLOSED results

No individual branch in this compiler currently holds a terminal `CLOSED` status (the
`Status` enum itself has no `CLOSED` value — only the overall *build's* terminal status can be
`CLOSED`/`PARTIALLY_CLOSED`/`CONDITIONALLY_CLOSED`/`FALSIFIED`, and the current build's
terminal status is `CONDITIONALLY_CLOSED`, confirmed unchanged by this campaign). Adversarial
validation was therefore applied to the strongest available status, `VERIFIED`, using the
adversarial/invariance tests that already exist in this build:

- `FALS-SPECTRUM-RELABELING-INVARIANCE` (branch 8/9): `Spec(L)` re-confirmed invariant under
  vertex relabeling, 5 representations, `passed=True`.
- `FALS-METRIC-UNIQUENESS-{cycle,path,grid2d}` (branch 9): re-confirmed the diffusion-metric
  candidate is *not* parameter-invariant, `passed=False` (correctly negative — this is the
  adversarial test working as intended, not a new failure).
- The S³ heat-kernel control's 4-window × degree-2..6 sweep (branch 8): re-confirmed stable
  across all tested fit configurations.
- No new adversarial tests were constructed this campaign, per the scope boundary against
  building new backends.

## 7. Final status table (summary)

| Status | Branches |
|---|---|
| `VERIFIED` | 8 (both sub-branches), 9 (relabeling invariance), 5's Fisher-PSD step, 6's eigen-uniqueness step |
| `CONDITIONAL` | 9's diffusion-metric candidate (non-unique, not a positive recovery) |
| `FALSIFIED` (retained, excluded) | 13 (both: Fisher-Rao=Lorentzian, spectrum-uniqueness) |
| `FAIL / RETRIABLE` | 12 (DESI, frozen, unchanged) |
| `PROPOSED` (prose-imported, unexecuted) | 4, 5's/6's full stated chains beyond their one executed step |
| `OPEN` (no executable backend) | 1, 2, 3, 7, 10, 11, and everything downstream of `SELECTION-SIGMA` in the template chain |
| `NOT REGISTERED` | 2 (no node exists at all) |

This is the accurate status map this campaign was asked to produce. It is not uniformly
`CLOSED`, and it was not made to be — the instruction was explicit that this is the correct,
desired outcome, not a shortfall.

## What have we actually established so far?

A rigorous, real, and reproducible spectral/heat-kernel mathematics core (branch 8): graph
Laplacians, heat traces, and an exact analytic control on S³, all independently re-verified
this campaign. A genuine, if partial and non-unique, spectral-geometry pipeline (branch 9)
that correctly refuses to claim more than its own results support. Two permanently and
correctly falsified naive identifications (branch 13), retained as guardrails. One
substantial, still-open discrete-to-continuum investigation (branch 12/interface III) with
real acquired data and genuine partial mathematical progress. Everything else in the
originally-scoped 14-branch campaign — the variational, GR, matter-geometry, thermodynamic,
gauge/Standard-Model, and cosmological branches, and three of the four "fundamental
interfaces" — has no executed content in this compiler at all.

## Which unresolved dependencies prevent the remaining branches from closing?

For 7 of 14 branches: the absence of any executable backend, not any upstream failure —
including FC-005's. For the template-chain branches specifically: the pre-existing,
separately unresolved `SELECTION-SIGMA` node. For branch 9's metric candidate: a genuine,
correctly-identified mathematical non-uniqueness, not a missing dependency. **FC-005 blocks
only its own four downstream nodes and nothing else.**

## Regeneration, tests, and audits

`compiler.run_compiler` was executed (twice, for the reproducibility check in section 1) after
this campaign's file additions; `calculation_registry.json`, `status_matrix.json`,
`falsification_registry.json`, and the provenance registries reflect the current, unchanged
state — this campaign added no new calculation, falsification, or status entries of its own
(it produced standalone validation-matrix files instead, precisely because building new IR
registrations for branches with no backend would itself be scope creep). All 95 tests and all
10 self-audits (including `leakage_control_audit` and `spectral_validation_audit`) pass — see
the commit history for this campaign for the exact run output.
