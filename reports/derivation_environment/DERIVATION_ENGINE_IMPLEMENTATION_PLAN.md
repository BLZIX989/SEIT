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
**Status: minimal slice implemented (follow-up session).** `m_aP` only, via
`compiler/backends/qcd_axion_mass.py` (the standard QCD axion mass relation, an
established formula, not invented here) and `compiler/derivation/
flagship_theorems.py::THM_QCD_AXION_MASS`. The arithmetic independently reproduces
`reports/master_toe/MASTER_TOE_PREDICTIONS.md`'s own hand-checked value
(6.885×10⁻¹³ eV) to 0.1%, but N_sub is bound as an explicit, unresolved
`EpistemicKind.ASSUMPTION` — that report's own audit found the N_sub ← CMB spectral
index (n_s) connecting formula was never located in the source corpus — so the
resulting Derivation is honestly `CONDITIONAL`, and `register_canonical_derivation`
correctly refuses to register it as `CANONICAL`. This is the intended outcome, not an
unfinished feature: the engine must not let a correct downstream arithmetic check
promote a claim whose upstream link is still open. `f_GW` (166.48 Hz) and `R_c`
(120–150 pc) remain **not attempted**: unlike N_sub, their upstream chains have not
been audited anywhere in this repository the way N_sub's was, and wiring them now
would mean inventing missing mathematics ad hoc rather than reproducing an
already-checked chain — the exact thing this program exists to prevent.

## What this session implements now

Phases 1–6 and a minimal Phase 9/10 (invalidation + recovery search over a small
synthetic three-node chain, since no real canonical node has been falsified this
session) — i.e. TEST 1, TEST 2, TEST 3, and TEST 8 from the task's §20 benchmark list,
executed for real, with passing tests, committed as an additive `compiler/derivation/`
package.

## Follow-up session: Phases 7, 8, 9-completion, 11, 12, 13, and a Phase 14 slice

- **Phase 7** (verification integration): the three Slice-1 theorems now each carry an
  independent symbolic obligation alongside their numeric one (exact sympy
  characteristic-polynomial cross-check for the spectrum; sympy's own matrix
  exponential, a different implementation path than scipy's `expm`, for the heat
  kernel) — never conflated into a single obligation.
- **Phase 8** (falsification integration): `compiler.falsification.protocols.
  representation_invariance_test` and `.mathematical_invariance_test` (existing,
  unmodified) now run as additional obligations on the Laplacian-PSD and
  spectral-decomposition theorems. The pre-existing falsification test suite's pass
  rate (21 tests) is unchanged.
- **Phase 9 completion**: `DerivationEngine.derive` now actually enforces
  `InadmissiblePremise` (previously declared but never raised) — a bound premise
  produced by a FALSIFIED/BLOCKED/otherwise-uncertified Derivation is refused, recorded
  as an honest `DERIVATION_FAILED` record, never silently used. Definitions and
  assumptions (the premises themselves, not claims about them) are always admissible.
- **Phase 11** (`compiler/derivation/equivalence.py`): `EquivalenceEngine.classify`
  with exactly the one registered check the spec calls for (verified change-of-basis);
  defaults to `"unknown"` otherwise, including when two candidates share an identical
  spectrum but no witness was supplied.
- **Phase 12** (`compiler/derivation/uniqueness.py`): `UniquenessEngine.admissible_set`,
  re-run directly against this project's own GEO-001 finding
  (`compiler/falsification/eigen_uniqueness.py`'s executed counterexample) and
  confirmed to report `"unknown"`, never `"singleton"`, for two operators sharing a
  spectrum. `"singleton"` is reachable only via an explicit `Theorem.proves_uniqueness`
  flag — never from an unexhausted search stopping after one success.
- **Phase 13** (`compiler/derivation/certification.py`): `to_canonical_status` (the
  `DerivationStatus → Status` table) and `register_canonical_derivation`, the one
  integration point that promotes a `VERIFIED` Derivation to `CANONICAL` and registers
  it into the existing `compiler.ir.registry.MDCLRegistries` — idempotent, and a
  refusal (not a crash) for anything not `VERIFIED`/`CANONICAL`.
- **Phase 14 slice**: as described above.

20 new tests added this follow-up session (29 total across all `compiler/derivation`
test files, all passing), full pre-existing suite re-run with 0 regressions after each
phase.
