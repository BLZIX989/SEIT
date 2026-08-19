# Master Physics Validation Report

Per the execution override governing this run: FC-005's sparse N-scaling investigation is
**frozen, not rerun**. This report begins at Phase 6, retains Phases 11–20, and reads FC-005
as-is from `FC005_CHECKPOINT.md` / `FC005_N_SCALING_REPORT.md` throughout. **Purpose (verbatim
from instruction): "determine exactly which parts of the existing physics framework survive
independent scrutiny," not to prove a desired conclusion.**

Raw data behind this report: `MASTER_PHYSICS_VALIDATION_MATRIX.csv` (17 rows, Part VI
columns), `MASTER_PHYSICS_CLOSURE_MATRIX.csv` (28 rows, Part XIV columns),
`DEPENDENCY_CLOSURE_AUDIT.csv`/`.md` (66-node audit), `BRANCH_FC005_DEPENDENCY_SUMMARY.csv`,
`INVARIANT_AUDIT.md`, `SIGN_CONVENTION_REGISTRY.md`, `CLEAN_ROOM_REPRODUCTION_REPORT.md`.

---

## 1. Executive Status

Of the 17 branches named in scope, **executable, re-run, reproducible content exists for
four**: Spectral (heat-kernel/graph mathematics), Spectral geometry (folded into the matrix
under "Statistical"/"Quantum" cross-references), Statistical and Quantum Recovery Cores (one
executed step each, not their full stated chains), and DESI/Continuum (frozen
`FAIL/RETRIABLE`). **Seven branches — Variational, Euler-Lagrange, Symmetry, Conservation, GR,
Thermodynamic, Gauge/representation/matter, Cosmological — have no executable backend
registered anywhere in this compiler.** Three of the four "fundamental interfaces"
(Quantum↔Gravity, Matter↔Geometry, Early↔Late universe) have nothing executed behind them
either. This is the load-bearing finding of this campaign and is detailed section-by-section
below.

## 2. Canonical Equations

**Actually implemented and executed:**

- `L φ_n = λ_n φ_n` (graph-Laplacian eigenproblem, Test 1 + S³ control + DESI)
- `K(t) = Σ_n exp(-t λ_n)` (heat trace)
- `W_ij = exp(-d_ij²/(2ε²))` (kernel graph construction)
- `L̃_(N,ε) = -L_N/(C_K·N·ε^(d+2))` (continuum-limit normalization, DESI)
- `F_ij = E[(∂/∂θ_i log p)(∂/∂θ_j log p)]` (Fisher information)
- `H|n⟩ = E_n|n⟩` (used only as the substrate for the eigenvalue-uniqueness counterexample)

**Named in campaign scope but not instantiated anywhere in this compiler:** `δS=0` /
Euler-Lagrange, Noether current `J^μ`, `G_μν+Λg_μν=(8πG/c⁴)T_μν`, `∇^μG_μν=0`, `∇^μT_μν=0`,
Riemann/Ricci tensors, Clausius-Duhem inequality, entropy current `S^μ`, heat flux
`q^μ=-κ∇^μT`, `G_SM=SU(3)×SU(2)×U(1)`, Friedmann-equation evolution. See
`MASTER_PHYSICS_VALIDATION_MATRIX.csv` column `canonical_equation` for the full per-branch
listing, including exactly which equation each unexecuted branch names.

## 3. Canonical Variables

**Actually instantiated in code and given numerical values:** `N`, `ε`, `L`, `λ_n`, `φ_n`,
`W_ij`, `D` (degree matrix), `C_K`, `F` (Fisher-Rao metric), `θ=(μ,σ)`, `H`, `E_n`, DESI's
`RA, DEC, Z, WEIGHT` and derived comoving coordinates.

**Never instantiated:** `g_μν`, `T_μν`, `G_μν`, `Λ`, `R^ρ_{σμν}`, `R_μν`, `R`, `A_μ`, `F_μν`,
`S` (action), `L` (Lagrangian density, distinct from the graph Laplacian `L` above — same
symbol, different object, never confused in this codebase since the Lagrangian-density sense
of `L` has no code path at all), `e, ρ, u^α, S^μ, q^μ, κ, T` (thermodynamic).

## 4. Canonical Dependency DAG

66 nodes total (58 Objects + 8 Transformations) in the live registries. Category breakdown
(from `DEPENDENCY_CLOSURE_AUDIT.csv`, node-level, corrected after a key-name bug was found and
fixed in the audit script itself — see `DEPENDENCY_CLOSURE_AUDIT.md`):

`closed_leaf`: 9 · `closed_intermediate`: 10 · `open`: 35 · `conditional`: 3 ·
`failed_retriable`: 3 · `falsified` (node-level): 0 · `proposed`: 6 · `superseded`: 0 ·
**`blocked`: 15**

Three nodes act as the DAG's "root axiom" gates, each explicitly and honestly registered as
unresolved by design (not a hidden gap): `SELECTION-SIGMA` (the full template chain's entry
point, `OPEN`), `GRAPH-G-SEED` (Test 1/2's postulated starting graph, `PROPOSED`), and
`S3-MANIFOLD` (the S³ control's postulated starting manifold, `PROPOSED`). All three are
`compiler/ir/forward_chain.py`'s own documented "directly postulated... NOT claimed to descend
from the (still-open) Selection/Vacuum chain" design — see `DEPENDENCY_CLOSURE_AUDIT.md` for
the full derivation of why this makes 15 otherwise-`VERIFIED`/`CALCULATED` nodes formally
`blocked` without being falsely closed.

## 5. Independent Derivations

Re-executed twice this campaign (`compiler.run_compiler`, independently), confirmed
bit-for-bit reproducible (excluding timestamp/commit metadata):

- 14 `CALC-T1-*` graph-topology calculations (Test 1).
- `CALC-FC005-S3-CONTROL` (S³ heat-kernel control).
- `CALC-FC005-FISHER-PSD` (Fisher-Rao PSD demonstration).
- `CALC-FC005-EIGEN-UNIQUENESS` (eigenvalue-uniqueness counterexample).

`CALC-FC005-DESI-SPARSE-N-SCALING` was **not** rerun (frozen, per the execution override) —
its `converged` field was independently re-derived this campaign from its own recorded
`eigenvector_subspace_comparison` data via the spectral-validation rule
(`FC005_CHECKPOINT.md`), a genuine independent computation on already-collected data, not a
re-execution of the underlying eigensolves.

## 6. Analytic Controls

The S³ heat-kernel control: numerical fit recovers the exact analytic `(a0,a1,a2)` to
`max|E_κ| = 1.02e-5` against a pre-registered `1e-4` tolerance, across 4 independent fit
windows and a degree-2..6 sweep (degree 2 → `|E_κ|~1e-3`; degree 4/5 → `|E_κ|~1e-8`/`1e-9`,
monotonic improvement with fit degree). This is the only genuine analytic control in this
compiler — used correctly, per instruction, as a control on the numerical method, never as
evidence that DESI "must" converge the same way.

## 7. Numerical Controls

Test 1's 14 graph topologies (path/cycle/complete/star/grid2d/erdos_renyi at multiple sizes)
serve as the numerical-method control for the graph-Laplacian/heat-trace pipeline — all
`VERIFIED`, all bit-for-bit reproducible. Within FC-005 (frozen, not rerun this campaign), the
uniform-IID synthetic control served the analogous role for the sparse N-scaling method,
confirming clean convergence through mode ~11 at N=64,000 — see `FC005_N_SCALING_REPORT.md`
section 7.

## 8. FC-005 DESI Execution

**Frozen, read as-is, not rerun.** Status confirmed via a fresh `status_matrix.json` read this
campaign (not re-derived): `CONTINUUM-LIMIT-L-DESI = FAIL`, `MATHEMATICAL-CONVERGENCE-DESI =
FAIL`, `CURVATURE-CLOSURE-DESI = OPEN`, `PHYSICAL-VALIDATION-DESI = OPEN`. Real DESI DR1 LRG
SGC data was used throughout the underlying investigation (checksum-verified, no synthetic
substitution). Gate 2 and Gate 3 were not entered — per this campaign's explicit instruction,
not attempted.

## 9. Continuum-Limit Analysis

Per the frozen sparse N-scaling investigation (`FC005_N_SCALING_REPORT.md`): modes 1–4 of the
15 retained low-lying modes show genuine joint eigenvalue+eigenvector convergence at N=64,000
(subspace cosine 0.99+); modes 5–15 show a false-positive eigenvalue-only "convergence"
(small eigenvalue change, near-orthogonal subspace, cosine 0.07–0.15) correctly rejected by
the spectral-validation rule. The corrected epsilon-scaling rate `ε_N ~ N^{-1/(d+4)}` was
verified to satisfy the required asymptotic condition `N·ε_N^{d+2} → ∞` at every tested
configuration. **The limiting operator is not automatically labeled `Δ_g`** — where
convergence is genuine (modes 1–4), no test has been performed to determine whether the limit
is `Δ_h` or a density-weighted alternative; where it is not genuine (modes 5+), no limiting
operator can be identified at all yet.

## 10. Curvature Extraction

**Not executed.** Gate 2 (`CURVATURE-CLOSURE-DESI`) was never entered, per explicit
instruction not to. `compiler/backends/desi_fc005_pipeline.py::run_curvature_closure` exists
as code but has never been invoked on real DESI data. Status: `OPEN`.

## 11. Cosmological Validation

**Not executed.** Gate 3 (`PHYSICAL-VALIDATION-DESI`) was never entered, for the same reason
(blocked on Gate 2). The only cosmology-adjacent artifact in this repository is
`FC005_cosmology.yaml` — DESI's own published fiducial parameters (H0=67.36, Ωm=0.315192,
ΩΛ=0.684808, w0=-1.0), consumed as *input* to the (unexecuted-past-Gate-1) DESI pipeline's
coordinate transform, never independently derived or validated here.

## 12. Quantum/Gravity Interface

**Nothing established.** `QUANTUM-NODE` and `GEOMETRY-NODE` are both bare `OPEN` template
placeholders. `compiler/historical/register.py` explicitly states, for the T2/NCG
spectral-triple bridge (the one candidate mechanism for this interface that was even
attempted): *"Not attempted; OPEN per spec section 5 (stop the branch, do not force
closure)."* The eigenvalue-uniqueness counterexample is a negative/guardrail result about
spectral-vs-operator identity, tangential to this interface, not a positive bridge.

## 13. Matter/Geometry Interface

**Only a bulk-imported prose claim, never executed.** `SEMICLASSICAL-EINSTEIN-EQUATION` is
registered `Status.PROPOSED` — per `compiler/core/status.py`'s own governing rule, a prose
claim is never promoted above `PROPOSED` without an executed artifact, and none has been
produced. `SEMICLASSICAL-RESIDUAL-E-SC` is `OPEN`, downstream of the unexecuted node. The
distinction between semiclassical QFT-in-curved-spacetime coupling and full quantum gravity is
preserved precisely because neither is executed here — there is nothing to conflate.

## 14. Discrete/Continuum Interface

**= FC-005.** By far the most developed of the four interfaces: real acquired data, a real
graph/operator construction fully executed, a substantial multi-phase diagnostic
investigation, and genuine (if partial) mathematical progress in the lowest spectral modes.
Remains `FAIL/RETRIABLE`, frozen. `G_DESI` is never equated with `g_μν` anywhere in this
codebase or its reports — the operator-identification question (section 9 above) is
explicitly left open rather than resolved by assumption.

## 15. Early/Late Universe Interface

**Nothing established.** `COSMOLOGY-NODE` is a bare `OPEN` template placeholder. No physical
evolution equation connecting early- and late-universe regimes (Friedmann equations, thermal
history, etc.) is registered or executed anywhere in this compiler. The existence of both a
(frozen, unexecuted-past-Gate-1) late-universe dataset (DESI) and no early-universe dataset at
all does not constitute closure of this interface, and is not treated as such.

## 16. Invariant Audit

Full detail in `INVARIANT_AUDIT.md`. Summary: no dimensional, sign-convention, symmetry, or
numerical-reproduction violation was found in any branch with executable content (Spectral,
DESI's graph-construction stage, Fisher-Rao, eigenvalue-uniqueness). Conservation-law and
several limiting-case checks are `n/a` for branches with no executable backend (GR,
Thermodynamic) — recorded honestly, not fabricated. `SIGN_CONVENTION_REGISTRY.md` documents
every convention in force; no unresolved convention clash currently exists (the two historical
clashes this project actually had — `Δ_h` vs `-Δ_h`, and the `K(d²/ε)` vs `K(d²/ε²)` units
mismatch — were both found and fixed in the prior FC-005 diagnostic phase, and re-confirmed
still correctly applied this campaign).

## 17. Dependency Closure Audit

Full detail in `DEPENDENCY_CLOSURE_AUDIT.md`. Summary: `leakage_control_audit` (the
build-blocking check — no `FAIL`/`FALSIFIED` node may be a transitive ancestor of any active
node) passes with 0 issues, confirmed on every regeneration this campaign. The broader,
supplementary node-level audit built for this campaign additionally found 15 nodes formally
`blocked` by their own directly-postulated root object — a real, honestly-disclosed
methodological finding (section 4 above), not a leakage-control violation.

## 18. Clean-Room Reproduction

Full detail in `CLEAN_ROOM_REPRODUCTION_REPORT.md`. Summary: a genuine fresh clone from the
GitHub remote (commit `6818acd4`) reproduces every registry byte-for-byte except one entry
(`CALC-FC005-DESI-SPARSE-N-SCALING`), which is absent only because its source data file is a
deliberately `.gitignore`d, large, ~40-minute-compute derived artifact — correctly not
regenerated in the clean room, per this campaign's instruction not to rerun FC-005. All 95
tests and all 10 self-audits pass identically in both trees. No dependency manifest exists in
this repository (reported, not concealed) — the clean-room environment isolation is therefore
partial (same shared Python/package versions as the working tree, no separate venv), and this
limitation is stated explicitly rather than overclaimed.

## 19. Adversarial Falsification Audit

No individual node in this compiler holds a terminal `CLOSED` status — `compiler/core/
status.py`'s `Status` enum has no `CLOSED` value at all (only `TerminalStatus`, applied to the
overall *build*, has one, and the current build's terminal status is `CONDITIONALLY_CLOSED`,
confirmed unchanged by this campaign). Adversarial validation was applied instead to the
strongest available per-node status, `VERIFIED`, using the full 10-point checklist where
applicable:

| Result | Reconstructed from declared deps | Hidden assumptions searched | Dimensional | Symmetry | Conservation | Limiting cases | Numerical reproduction | Alternative representations | Known counterexamples | Clean-env reproduction | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Test 1 pipeline | Yes (self-contained) | none found | pass | pass | n/a | n/a | pass (2x + clean-room) | `FALS-SPECTRUM-RELABELING-INVARIANCE` (5 representations) | n/a | pass | **SURVIVES** |
| S³ control | Yes (self-contained) | none found | pass | pass | n/a | pass (degree sweep) | pass (2x + clean-room) | 4 independent fit windows | n/a | pass | **SURVIVES** |
| Fisher-Rao PSD | Yes (self-contained) | none found | pass | pass | n/a | n/a | pass (2x + clean-room) | symbolic derivation, not just numeric | attempted Lorentzian identification, correctly rejected | pass | **SURVIVES** |
| Eigenvalue-uniqueness counterexample | Yes (self-contained) | none found | pass | pass | n/a | n/a | pass (2x + clean-room) | 25 independent random trial instances | this IS the counterexample to a known claim | pass | **SURVIVES** |

No result was `REOPEN`ed or `FALSIFIED` by this pass. This is not because closure was
protected — every check in the list above was actually performed (not assumed) this campaign,
several for the first time (the clean-room reproduction and the corrected node-level
dependency audit both surfaced real, previously-undocumented findings — sections 4 and 18 —
demonstrating this was a genuine adversarial pass, not a rubber stamp).

## 20. Falsified Branches

Two, both node-level-`FALSIFIED`-equivalent via the separate falsification registry (see
section 4/`DEPENDENCY_CLOSURE_AUDIT.md` for why no node itself carries `Status.FALSIFIED`):

- **`FALS-FC005-FISHER-LORENTZIAN`**: Fisher-Rao metric ≠ Lorentzian spacetime metric. A PSD
  matrix cannot carry Lorentzian signature under any basis change — structurally impossible,
  not a numerical coincidence. Re-audited this campaign, confirmed still excluded from every
  active node.
- **`FALS-FC005-EIGENVALUE-UNIQUENESS`**: the spectrum alone does not uniquely determine the
  operator. Re-audited this campaign, confirmed still excluded from every active node. This is
  the direct historical precedent for FC-005's own spectral-validation rule
  (`FC005_CHECKPOINT.md`).

Neither branch was reopened or revisited for rehabilitation this campaign, per instruction.

## 21. Conditional Branches

Three nodes carry `Status.CONDITIONAL`: `METRIC-CANDIDATE` (diffusion-time-normalized
candidate metric — valid only for an arbitrarily chosen diffusion-time multiplier, shown
non-unique by `FALS-METRIC-UNIQUENESS-{cycle,path,grid2d}`), `DTC-CIRCULARITY-OBSTRUCTION`
(the corresponding circularity-obstruction finding), and the `T-DIFFUSION-TO-METRIC`
transformation itself. None claim more than their own results support.

## 22. Open Dependencies

35 `OPEN` nodes, falling into four groups: (1) the full template chain from `FOUNDATION`
through `OBSERVABLES-NODE`, blocked by `SELECTION-SIGMA`; (2) the historical T2/NCG bridge
(`T2-REPRODUCTION`, `T2-FORWARD-DERIVATION`, three `NCG-*-OBSTRUCTION` nodes), explicitly
"not attempted" by its own module; (3) FC-005's downstream gates
(`CURVATURE-CLOSURE-DESI`, `PHYSICAL-VALIDATION-DESI`, `DESI-HEAT-TRACE`,
`DESI-HEAT-COEFFICIENTS`, `KAPPA-DESI`, `E-KAPPA-DESI`, `DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK`),
blocked solely on Gate 1's `FAIL`; (4) `SEMICLASSICAL-RESIDUAL-E-SC` and `SPEC-H-UNIQUENESS`,
downstream of unexecuted/PROPOSED nodes.

## 23. Superseded Historical Results

**None — and none can exist by construction.** `compiler/core/status.py`'s `Status` enum has
no `SUPERSEDED` value (`VERIFIED, DERIVED, CALCULATED, CONDITIONAL, PROPOSED, OPEN, FAIL,
FALSIFIED` only). This campaign's instruction anticipated a `SUPERSEDED` category; this
compiler's schema does not implement one. Reported as a schema gap, not silently worked around
by inventing a new status value (which would itself be an unauthorized architecture change).

## 24. Final Closure Matrix

`MASTER_PHYSICS_CLOSURE_MATRIX.csv` (28 rows, Part XIV's column set: ID, branch, proposition,
equation, variables, dependencies, mathematical_status, symbolic_status, numerical_status,
observational_status, external_status, adversarial_status, provenance_status, final_status,
failure_mode, next_dependency) and `MASTER_PHYSICS_VALIDATION_MATRIX.csv` (17 rows, Part VI's
column set) together constitute the required final closure matrix. Neither uses a single
binary proven/not-proven field; both preserve the full distinction between `VERIFIED`,
`CALCULATED`, `CONDITIONAL`, `PROPOSED`, `OPEN`, `FAIL/RETRIABLE`, `FALSIFIED`, and
`NOT REGISTERED`.

## 25. Remaining Physics Problems

In order of tractability:

1. **DESI modes 5–15** (Continuum branch): do they eventually stabilize at larger N, or does
   the limiting behavior genuinely differ from the lowest modes? Not decided by this campaign
   (FC-005 explicitly frozen). See `FC005_N_SCALING_REPORT.md` section 16.
2. **α=1 (density-normalized) epsilon-scaling rate**: untested independently; the rate
   calibrated for α=0 does not evidently carry over.
3. **The seven backend-less branches** (Variational, Euler-Lagrange, Symmetry, Conservation,
   GR, Thermodynamic, Gauge/SM, Cosmological — eight, counting Euler-Lagrange and Variational
   separately): would each require an independently-derived, non-arbitrary starting point
   (an action functional, a metric, a gauge group, etc.) before any executable validation is
   even possible. Explicitly out of scope to construct in a validation-only campaign.
4. **`SELECTION-SIGMA`**: the single upstream gate blocking the entire template chain,
   unresolved since this compiler's earliest sessions, with — per its own registration — "no
   non-arbitrary, unique, representation-invariant derivation... registered in this build."

## 26. Reproducibility Information

See `CLEAN_ROOM_REPRODUCTION_REPORT.md` for full detail: commit `6818acd4d5f4a85252aadc22980f88594c727b36`,
Python 3.11.15, numpy 2.4.6, scipy 1.17.1, sympy 1.14.0, astropy 8.0.1, Linux 6.18.5-fc-v20
x86_64. pytest: 44s. Compiler build: <1 minute. No dependency manifest exists (reported
honestly). No raw or derived DESI datasets are committed (confirmed empty in the fresh clone).

## 27. Final Scientific Interpretation

**What survives independent scrutiny**: a rigorous, reproducible spectral/heat-kernel
mathematics core (graph Laplacians, heat traces, an exact analytic S³ control); a spectral
-geometry pipeline that correctly refuses to overclaim (explicitly non-unique metric
candidate); two permanently and correctly falsified naive identifications, retained as
guardrails; one substantial, still-open discrete-to-continuum investigation with real data and
genuine partial mathematical progress in its lowest spectral modes, now further hardened by a
structurally-enforced spectral-validation rule that caught and rejected a false-positive
convergence result during this project's own history.

**What does not survive scrutiny because it was never executed**: the variational chain, the
full GR chain (Riemann/Ricci/Einstein-tensor computation, field equations, conservation
laws), Noether's theorem, the thermodynamic recovery core, the gauge/Standard-Model recovery,
and the early/late-universe cosmological evolution chain. Three of the four "fundamental
interfaces" this project originally posed (Quantum↔Gravity, Matter↔Geometry, Early↔Late
universe) have no executed content behind them at all.

Per instruction, this report never converts: numerical agreement into theoretical identity
(the S³ control's numerical-analytic agreement is reported as exactly that, a control, never
as proof of a physical claim); representation into ontology (`G_DESI` is never equated with
`g_μν`); compiler structure into physical structure (every `OPEN`/`PROPOSED` template node is
reported as an absence of execution, never reinterpreted as a physics result); semiclassical
quantum gravity into full quantum gravity (neither is executed here, so neither is claimed);
or DESI galaxy topology into spacetime geometry without a demonstrated bridge (none has been
demonstrated — the continuum-limit analysis, section 9, explicitly declines to identify a
limiting operator where convergence has not been shown to be genuine).

**The answer to "what, exactly, have we established?"**: a real, working, independently
reproducible mathematical core for graph-Laplacian spectral theory and heat-kernel geometry,
two genuine falsifications that correctly guard against overclaiming from spectral data alone,
and a partially-successful, still-open attempt to connect real astronomical observations to
that mathematical core — nothing more, and this report does not claim otherwise. The rest of
the originally-posed physics program (from the variational principle through gauge theory to
cosmology) remains exactly where it was before this campaign: an unexecuted dependency
template, honestly labeled as such.
