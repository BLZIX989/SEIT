# DERIVATION_ENGINE_IMPLEMENTATION_PLAN.md

Deliverable 3 of the Universal Mathematical Derivation Environment program. Ordered
strictly by dependency, per the task's own required order (§28): mathematical types →
symbolic representation → derivation traces → theorem/rule registry → execution engine
→ proof obligations → verification → falsification → invalidation → recovery →
equivalence → uniqueness → certification → physical prediction engine. Each phase
lists its deliverable, its dependency on prior phases, and how it will be verified.
No phase after Phase 1 begins until the phase before it has passing tests.

## Phase 1 — Mathematical types (`compiler/derivation/types.py`)
**Depends on:** nothing new; reads existing `compiler.core.status.Status` for reference only.
**Deliverable:** `MathType`, `EpistemicKind`, `MathObject`, `require()`, `TypeCompositionError`.
**Verification:** unit tests asserting `require()` raises for every disallowed composition
named in the spec (bare Matrix as Metric, bare Matrix as SelfAdjointOperator without a
checked `symmetric` property, etc.) and succeeds once the relevant `verified_properties`
entry is actually populated by a real check.
**Status of this phase:** implemented in this session as Slice 1 (§ below).

## Phase 2 — Symbolic representation adapter (`compiler/derivation/symbolic.py`)
**Depends on:** Phase 1.
**Deliverable:** thin wrapper functions binding `MathObject.carrier` to sympy objects
where `math_type` allows it, plus `symbolic_equal(a, b) -> bool` (wraps
`sympy.simplify(a - b) == 0`, the same pattern already used in
`finite_spectral_triple_candidate.py`, now factored into one place instead of
reimplemented per module).
**Verification:** re-run the existing symbolic checks in
`finite_spectral_triple_candidate.py::_verify_first_order_closed_form_symbolic` through
the new wrapper and confirm bit-identical results.

## Phase 3 — Derivation trace model (`compiler/derivation/derivation.py`)
**Depends on:** Phases 1–2.
**Deliverable:** `DerivationStep`, `Derivation`, `derivation_registry.json` writer
(same `dump_json`-style pattern as `compiler/protocol/registry.py`'s `ChainlinkRegistry`).
**Verification:** round-trip test — build a `Derivation` by hand, serialize, deserialize,
compare.

## Phase 4 — Theorem/rule registry (`compiler/derivation/theorems.py`)
**Depends on:** Phases 1–3.
**Deliverable:** `Theorem`, `TheoremRegistry`. Populate exactly three fully-`implemented=True`
entries for Slice 1 (`THM-SYMMETRIC-QUADRATIC-FORM-PSD`, `THM-SPECTRAL-DECOMPOSITION-
REAL-SYMMETRIC`, `THM-MATRIX-EXPONENTIAL-SEMIGROUP`), plus registered-but-unimplemented
stub entries (statement + citation only, `implemented=False`) for the remainder of the
task's §6 list (Hodge decomposition, `d²=0`, Euler–Lagrange, Noether, Levi-Civita
uniqueness, Bianchi identities, Lichnerowicz formula, heat-kernel expansion,
Seeley-DeWitt, Clifford relations) — present in the library honestly, not usable yet.
**Verification:** a test asserting every registered theorem has a non-empty `hypotheses`,
`conclusion`, and `provenance`, and that `implemented=False` entries raise
`TheoremNotImplemented` rather than executing.

## Phase 5 — Proof obligations (`compiler/derivation/obligations.py`)
**Depends on:** Phases 1–4.
**Deliverable:** `ObligationResult`, `ProofObligation`, and the obligation sets emitted
by each Slice-1 theorem (symmetry, PSD, orthonormal-eigenbasis-completeness, semigroup
identity `H(0)=I`).
**Verification:** deliberately construct a non-symmetric matrix and confirm the
symmetry obligation reports `FAILED`, not silently `NOT_TESTED` or `SATISFIED`.

## Phase 6 — Execution engine (`compiler/derivation/engine.py`)
**Depends on:** Phases 1–5.
**Deliverable:** `DerivationEngine.derive(target_id)`, wired to call into
`compiler.backends.graph_laplacian`, `compiler.backends.spectral`,
`compiler.backends.pipeline_graph_heatflow` as the `transformation` payloads for the
three Slice-1 theorems (no duplicated numerics).
**Verification:** TEST 1, TEST 2, TEST 3 (task §20) executed end to end and reaching
`DerivationStatus.CANONICAL`.

## Phase 7 — Verification integration
**Depends on:** Phase 6.
**Deliverable:** cross-check every symbolic result against its numeric counterpart
(task §12's example: symbolic `L=Lᵀ` vs. numeric `‖L−Lᵀ‖<ε`), recorded as two distinct
`ProofObligation`s per claim, never conflated into one.
**Verification:** a test asserting both obligation records exist and are independently
inspectable.

## Phase 8 — Falsification integration (no new code; wiring only)
**Depends on:** Phase 6.
**Deliverable:** `DerivationEngine` calls the EXISTING
`compiler.falsification.protocols` functions (`representation_invariance_test`,
`mathematical_invariance_test`, `structural_elimination_protocol`) as additional
`verification_tests` on applicable theorems, rather than reimplementing them.
**Verification:** re-run of the existing falsification test suite, unchanged pass rate.

## Phase 9 — Invalidation (`compiler/derivation/invalidation.py`)
**Depends on:** Phase 3. Reuses `compiler.dependencies.graph.DependencyGraph`'s
existing `.descendants()` (confirmed present, alongside `.ancestors()`, during Phase-1
implementation — no change needed there) and `compiler.verification.self_audit`'s
existing `build_dependency_graph`.
**Deliverable:** `InvalidationEngine.on_falsified`.
**Verification:** TEST 8 (task §20): inject a deliberately false theorem result three
levels deep in a small synthetic dependency chain, confirm exactly the correct
descendants flip to `BLOCKED` and no others.

## Phase 10 — Recovery (`compiler/derivation/recovery.py`)
**Depends on:** Phase 9.
**Deliverable:** `RecoveryEngine.recover`.
**Verification:** continuing TEST 8 — confirm a recovery search runs against the
remaining theorem registry, and confirm it correctly reports `DERIVATION_FAILED` when
(as in the deliberately-broken synthetic case) no honest alternative exists, rather than
forcing a result.

## Phase 11 — Equivalence engine (`compiler/derivation/equivalence.py`)
**Depends on:** Phase 1, 4.
**Deliverable:** `EquivalenceEngine.classify`, with exactly one real registered check to
start (matrix similarity via an explicit, verified change-of-basis) and `"unknown"` as
the default for everything else.
**Verification:** confirm two numerically-different matrices related by a verified
similarity transform classify as `basis_transformation`, and confirm two matrices with
no registered check classify as `unknown`, never a false `distinct_candidate`.

## Phase 12 — Uniqueness engine (`compiler/derivation/uniqueness.py`)
**Depends on:** Phase 4, 11.
**Deliverable:** `UniquenessEngine.admissible_set`.
**Verification:** re-run against the already-known GEO-001 diffusion-metric case and
confirm it reports `"unknown"` or `"continuous"` (never `"singleton"`) given the
existing eigenvalue-uniqueness counterexample and free-time-parameter finding —
i.e. confirm the engine does not accidentally certify what this project's own prior
audit already falsified.

## Phase 13 — Certification mapping (no new engine; a pure function)
**Depends on:** Phases 1–12.
**Deliverable:** `compiler/derivation/certification.py::to_canonical_status`, implementing
the `DerivationStatus → Status` table in `DERIVATION_ENGINE_SPEC.md` §6, and the actual
registration call into `registries.objects.add_object` / `make_provenance` (existing
functions, called, not reimplemented) when a Derivation reaches `CANONICAL`.
**Verification:** run a Slice-1 derivation through to registration and confirm the
resulting `status_matrix.json` entry has the mapped `Status`, with a
`derivation_id` cross-reference in its provenance.

## Phase 14 — Physical prediction engine
**Depends on:** all of the above, plus whichever DER-canon branches (thermodynamic,
variational, geometric) are implemented per the Documentation Conformance Audit's own
Priority 1–2 recommendations.
**Deliverable:** `derive(target=flagship_prediction)` attempting `m_{aP}`, `f_GW`, `R_c`.
**Not started in this pass** — explicitly deferred until Phases 1–13 are real and its
own upstream dependency chain (§ the Documentation Conformance Audit's DER-SC/DER-TRC/
DER-GEO recommendations) exists to derive from. Attempting it earlier would mean
inventing the missing upstream mathematics ad hoc, which is exactly what this whole
program exists to prevent.

## What this session implements now

Phases 1–6 and a minimal Phase 9/10 (invalidation + recovery search over a small
synthetic three-node chain, since no real canonical node has been falsified this
session) — i.e. TEST 1, TEST 2, TEST 3, and TEST 8 from the task's §20 benchmark list,
executed for real, with passing tests, committed as an additive `compiler/derivation/`
package. Phases 7, 8, 11, 12, 13, 14 are specified above but not implemented in this
pass; they are the explicit next-session backlog, in the stated order.
