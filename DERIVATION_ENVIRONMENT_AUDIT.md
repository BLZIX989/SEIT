# DERIVATION_ENVIRONMENT_AUDIT.md

Deliverable 1 of the Universal Mathematical Derivation Environment program. Every
line below reflects direct inspection of the actual code in this repository at
commit `c499166` (branch `claude/forward-mdcl-compiler-build-ng4k2k`) — file paths,
function names, and behavior are cited, not inferred from filenames, docstrings, or
prior reports. Where a capability is real but narrower than its name suggests, that
narrowness is stated explicitly. This document does not modify, promote, or demote
any existing status; it only reports what already exists.

Rating scale used throughout, per the task's own instruction:

- **PRESENT AND EXECUTABLE** — real code, runs today, does what the capability name says.
- **PARTIAL** — real code exists and executes, but covers a narrower case than the
  capability name implies, or implements the detection half of a capability without
  the action half.
- **STUB** — a function/class/field exists with the right name and signature but
  performs no real work (e.g. always returns a constant, or is unused dead code).
- **DOCUMENTATION ONLY** — described in a docstring, spec section, or report, with
  no corresponding executable code.
- **ABSENT** — nothing found, in code or documentation.

---

## 1. Capability-by-capability findings

### 1. Symbolic mathematics
**PRESENT AND EXECUTABLE.** `sympy` is a real, exercised dependency (`compiler/requirements.txt: sympy>=1.13`,
installed version 1.14.0 confirmed this session). Used in: `compiler/backends/finite_spectral_triple_candidate.py`
(`_verify_first_order_closed_form_symbolic`, small-n symbolic confirmation of a commutator identity),
`compiler/backends/finite_spectral_triple_recovery.py` and `..._recovery_coupled.py` (same pattern),
`compiler/backends/graph_laplacian.py`, `compiler/backends/lichnerowicz_seeley_dewitt.py`,
`compiler/backends/pipeline_graph_heatflow.py`, `compiler/verification/fisher_information.py`,
`compiler/verification/verify.py`, `compiler/ir/executable_tests.py`.

### 2. Symbolic equation manipulation
**PARTIAL.** Every sympy use found is `sp.simplify`, `sp.zeros`/`sp.Matrix` construction, and direct symbolic
equality comparison (`residual == sp.zeros(...)`) — confirming a closed-form identity holds exactly for small,
fixed-size symbolic examples. There is no general-purpose `solve`, `factor`, `expand`, symbolic differentiation,
or symbolic integration anywhere in `compiler/`. The manipulation vocabulary is: build a symbolic matrix,
multiply, simplify, compare to a hand-derived closed form.

### 3. Numerical linear algebra
**PRESENT AND EXECUTABLE.** `numpy`/`scipy` throughout (`np.linalg.eigh`, `eigvalsh`, `matrix_power`,
`scipy.linalg.expm`-equivalent constructions via eigendecomposition, `scipy.sparse.linalg.eigsh` in
`compiler/backends/desi_sparse.py`). This is the single most mature capability in the repository.

### 4. Arbitrary precision arithmetic
**ABSENT.** No `mpmath`, no `decimal.Decimal`/`getcontext`, no sympy `Rational`/arbitrary-precision `evalf`
call found anywhere in `compiler/`. All numerical work is standard IEEE double precision.

### 5. Graph construction
**PRESENT AND EXECUTABLE.** `compiler/backends/graph_laplacian.py` (`build_graph`), `desi_graph.py`
(`build_kernel_graph`), `desi_sparse.py`, and the H2/H2B ring-graph constructions in
`finite_spectral_triple_candidate.py`/`_tft002b.py`.

### 6. Spectral decomposition
**PRESENT AND EXECUTABLE.** `compiler/backends/spectral.py`; real eigendecomposition, cross-checked exactly
for n≤8 per `compiler/protocol/derivation_chainlinks.py`'s own reproducibility classification.

### 7. Differential operators
**PARTIAL.** Discrete exterior-calculus operators exist and are real: incidence matrices `d1`/`d2`
(`dirac_candidates.py`, `finite_spectral_triple_tft002b.py`) implementing the discrete boundary/coboundary
maps, and the discrete Hodge-Dirac construction `D=d+d†` (TFT-002B, `D3²=diag(L0,L1,L2)`, exactly verified).
There is no continuum differential-operator layer (no `∂_μ`, `∇`, or PDE-operator representation) anywhere.

### 8. Tensor algebra
**PARTIAL.** Real tensor/matrix objects exist for specific, small, hand-built cases (the flat-2D and round-S²/S³
control manifolds in `lichnerowicz_seeley_dewitt.py`, where curvature `R`, field strength `F_12`, and the
Seeley-DeWitt coefficient contractions are evaluated numerically). There is no general index-notation tensor
type, no automatic index contraction, no covariance/rank checking.

### 9. Differential geometry
**PARTIAL.** Genuine, executed differential geometry exists, but only on **externally specified control
manifolds** (flat ℝ², round S², round S³), never on a metric the compiler itself derived from its own graph/
spectral primitives: `CL-CONTROL-TO-LICHNEROWICZ-GAUGE` and `..._GRAVITY` (VERIFIED), computing
`D_A²=-(∇²+E)` with `E=iF_12γ¹γ²` and `E=cR` (`c=-1/4` solved, not assumed). Metric, connection, and
Riemann/Ricci/Einstein-tensor recovery from the compiler's own graph/spectral chain is OPEN/NO_CORRESPONDING_ARTIFACT
(`protocol_matrix.json`: MR-011 CONDITIONAL, MR-012..016 OPEN or absent).

### 10. Variational calculus
**ABSENT.** `VARIATIONAL-NODE` (`compiler/ir/forward_chain.py`) is a registered dependency-template
placeholder Object with status OPEN; no code computes, varies, or extremizes any functional anywhere in
`compiler/`.

### 11. Euler–Lagrange derivation
**ABSENT.** No occurrence of an actual Euler–Lagrange computation (symbolic or numeric) in `compiler/`.

### 12. Constraint solving
**PARTIAL.** Specific, hand-coded admissibility checks exist (e.g. `finite_spectral_triple_tft002b.py`'s
promotion criterion: self-adjointness ∧ grading² ∧ anticommutation ∧ exact-square, evaluated as a boolean
conjunction) — this is constraint *checking*, not constraint *solving*. No general constraint-satisfaction
solver (SAT/SMT/algebraic-constraint solver) exists.

### 13. Dimensional analysis
**ABSENT.** The one grep hit for "dimension" in `compiler/backends/toe_closure_hypotheses.py`
(`CALC-H4-G2-SPIN8-GAUGE-CLOSURE`, `kind: "lie_group_rank_dimension_check"`) is a Lie-group **rank/dimension**
count (an integer comparison for the G2/Spin(8) gauge-group construction), not a physical-units dimensional
consistency system. No units/dimension type (mass, length, time, action, energy) exists anywhere.

### 14. Theorem/proof representation
**PARTIAL.** `compiler/protocol/schema.py`'s `Protocol` dataclass has `proof_obligations: list[str]`,
`invariants: list[str]`, `falsification_criteria: list[str]`, `admissibility_conditions: list[str]` — all
**free-text string lists**, populated by hand at registration time. There is no structured theorem object with
machine-checkable hypotheses/conclusion/applicability conditions.

### 15. Proof obligations
**PARTIAL.** Same as above — the field exists and is populated (e.g. `CL-CONTROL-TO-FINITE-SPECTRAL-TRIPLE-AXIOMS`'s
`failure_conditions`), but obligations are discharged by the surrounding Python code's own `np.allclose`/`==`
checks, not by a generic obligation-discharge engine that reports SATISFIED/FAILED/PARTIAL/NOT_TESTED per
obligation. The status of the whole chainlink is the only externally visible signal; individual obligations
within it are not independently tracked as pass/fail records.

### 16. Numerical verification
**PRESENT AND EXECUTABLE.** The strongest capability alongside numerical linear algebra: `np.allclose`,
exact block-matching, and residual-norm checks are used pervasively and are the actual basis for every
VERIFIED/CALCULATED status in the registries.

### 17. Falsification protocols
**PRESENT AND EXECUTABLE.** `compiler/falsification/protocols.py`: `structural_elimination_protocol`,
`representation_invariance_test`, `mathematical_invariance_test`, `observer_independent_structural_reduction`
— all four are real, executed, registered functions (not merely named), and their pass/fail results feed the
`falsification_status` field on chainlinks. `compiler/falsification/eigen_uniqueness.py` and the Fisher-Rao
rejection (`EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION`) are real, executed counterexample constructions.

### 18. Alternative-hypothesis generation
**ABSENT as an automated capability.** Every "alternative construction" in this repository to date (the
Hilbert-doubling recovery, TFT-002B, the nontrivially-coupled recovery, the KO-sign-convention scan) was
manually authored, one Python module at a time, by a human/session directing specific new code. No code
searches a space of candidate constructions and proposes new ones; `AXIOM-CHECK-FIRST-ORDER-CONDITION`'s
own registry entry states this explicitly ("a genuinely different (A_F,J_F,γ_F)... has not been found or
attempted anywhere in this corpus" prior to the manually-authored recovery).

### 19. Dependency invalidation
**PARTIAL — this is the single most important nuance in this audit.** `compiler/verification/self_audit.py`'s
`leakage_control_audit` is a real, executed **detector**: it computes, for every active (VERIFIED/DERIVED/
CALCULATED) node, whether any transitive ancestor is FALSIFIED or FAIL, and fails the whole self-audit if so.
This is genuine dependency-invalidation *checking*. So is `compiler/dependencies/graph.py::ExecutionGuard.check`,
which actively refuses (raises `DependencyError`) to let a transformation execute at all if any of its declared
upstream dependencies has a status outside `EXECUTABLE_UPSTREAM_STATUSES` (`{VERIFIED, DERIVED, CALCULATED,
CONDITIONAL}`) — this is real, enforced, pre-execution invalidation-awareness, not merely a post-hoc audit.
`DependencyGraph` (same module) already implements **both** `.ancestors()` and `.descendants()` — the traversal
infrastructure a propagation engine would need already exists and did not need to be added.
What is still genuinely absent: nothing *actively walks forward* from a node that has just transitioned to
FALSIFIED/FAIL and flips its already-registered descendants' status in response — `ExecutionGuard` stops a
*new* execution from building on a bad dependency, but does not retroactively react to an *existing* downstream
result when its upstream is falsified after the fact. Today that reaction is still a manual source-correction +
full re-run, exactly as this project's own established discipline already requires.

### 20. Downstream re-derivation
**ABSENT.** No code re-executes or re-derives a downstream object automatically in response to an upstream
change. Every re-derivation performed in this repository's history (e.g. the ε^(5/2)→ε^5 continuum-exponent
correction) was a manual source-code edit followed by a full manual `compiler.run_compiler` re-run, not an
automated cascade.

### 21. Registry promotion/demotion
**PRESENT AND EXECUTABLE, for single-node transitions.** `compiler/core/status.py::can_transition` and
`ALLOWED_TRANSITIONS` define a real, enforced transition table (e.g. `VERIFIED→{FALSIFIED}` only; `FALSIFIED`
is terminal, `set()`). It is genuinely called from `compiler/core/ir.py` (`IRNode`'s status setter checks
`can_transition` before allowing a change, with an explicit `force` override). This governs one node's own
status change; it is not a graph-wide propagation mechanism (see item 19/20).

### 22. Provenance tracking
**PRESENT AND EXECUTABLE.** `compiler/provenance/provenance.py::make_provenance`, attached to essentially
every Object/Transformation/Equation; dumped to `provenance_registry.json` every run, containing source module,
calculation_id, status, and verification payload.

### 23. Derivation trace storage
**PARTIAL.** `calculation_registry.json` stores, per calculation: `id`, `kind`, `inputs`, `results`,
`verification`, `status` — a real, structured input/output/verification record. It is **not** a step-by-step
transformation trace (it does not record "start from L=D-A, apply xᵀ(·)x, apply the graph-weight identity,
conclude ≥0" as a sequence of individual steps) — it records the calculation's inputs and final numeric/boolean
results only.

### 24. Regression testing of previously verified mathematics
**PRESENT AND EXECUTABLE, narrowly.** `numerical_reproducibility_audit` performs a bitwise re-run comparison
of registry files across two runs of the identical compiler — this catches non-determinism, not mathematical
regression from a code change. The 734-test pytest suite is real regression coverage for the *code*, run on
every session in this project's history, but there is no dedicated "this theorem, once VERIFIED, is
automatically re-checked whenever any of its dependencies' code changes" mechanism distinct from re-running
the whole test suite by hand.

### 25. External established-mathematics references
**DOCUMENTATION ONLY.** Citations exist as prose in docstrings and the `literature_support: list[dict]` field
on `Protocol` (e.g. Belkin-Niyogi 2005/2008, Coifman-Lafon 2006, Gilkey 1975, Vassilevich 2003) — genuinely
present as text, correctly cited, but not a queryable library: there is no code path that looks up "spectral
theorem" or "Lovelock's theorem" and returns its formal statement, hypotheses, and applicability conditions.

### 26. Equation normalization
**ABSENT.** No canonical-form/normal-form reduction of any equation exists anywhere in `compiler/`.

### 27. Canonical mathematical type checking
**ABSENT as a general system.** `compiler/ir/registry.py`'s `TypeRegistry` records a flat `(name, description,
parent)` triple per registered type (e.g. `"graph_laplacian_operator"` with parent `"mathematical_object"`) —
this is a documentation taxonomy, not an enforced type system: nothing in the codebase rejects, at
construction time, an attempt to use a bare numpy matrix as if it were a metric tensor, or checks operator
domain/codomain compatibility before a computation runs.

### 28. Branch comparison
**PARTIAL.** Comparisons exist for specific, manually identified pairs (e.g. the KO-sign-convention scan
comparing `(+1,+1,+1)` vs `(-1,-1,-1)`; TFT-002B vs the 2-block D_B, compared via `edge_block_max_abs_difference`).
No general "compare branch X against branch Y for structural equivalence" utility exists.

### 29. Uniqueness testing
**PARTIAL.** Two genuine, executed uniqueness *rejections* exist: `eigen_uniqueness.py` (Spec(H) does not
determine H — a real counterexample, not an assertion) and the diffusion-metric non-uniqueness finding
(`FALS-METRIC-UNIQUENESS-*`, free time parameter `t`). Both are one-off, hand-constructed counterexample
scripts, not instances of a general "formulate admissibility constraints A(T), search {T : A(T)}, classify the
solution set as empty/singleton/finite/continuous" engine. No such general engine exists.

### 30. Equivalence testing
**ABSENT as a general system.** The KO-sign-convention scan and the TFT-002B vs D_B comparison are the closest
analogues, and both are hand-written, single-purpose comparisons, not a general equivalence-testing utility
that could tell "gauge-equivalent" from "coordinate transformation" from "genuinely different theory."

---

## 2. Summary table

| # | Capability | Status |
|---|---|---|
| 1 | Symbolic mathematics | PRESENT AND EXECUTABLE |
| 2 | Symbolic equation manipulation | PARTIAL |
| 3 | Numerical linear algebra | PRESENT AND EXECUTABLE |
| 4 | Arbitrary precision arithmetic | ABSENT |
| 5 | Graph construction | PRESENT AND EXECUTABLE |
| 6 | Spectral decomposition | PRESENT AND EXECUTABLE |
| 7 | Differential operators | PARTIAL |
| 8 | Tensor algebra | PARTIAL |
| 9 | Differential geometry | PARTIAL |
| 10 | Variational calculus | ABSENT |
| 11 | Euler–Lagrange derivation | ABSENT |
| 12 | Constraint solving | PARTIAL |
| 13 | Dimensional analysis | ABSENT |
| 14 | Theorem/proof representation | PARTIAL |
| 15 | Proof obligations | PARTIAL |
| 16 | Numerical verification | PRESENT AND EXECUTABLE |
| 17 | Falsification protocols | PRESENT AND EXECUTABLE |
| 18 | Alternative-hypothesis generation | ABSENT |
| 19 | Dependency invalidation | PARTIAL (detection only, no propagation) |
| 20 | Downstream re-derivation | ABSENT |
| 21 | Registry promotion/demotion | PRESENT AND EXECUTABLE (single-node only) |
| 22 | Provenance tracking | PRESENT AND EXECUTABLE |
| 23 | Derivation trace storage | PARTIAL (input/output record, not step trace) |
| 24 | Regression testing | PRESENT AND EXECUTABLE (narrow: bitwise re-run + full test suite) |
| 25 | External math references | DOCUMENTATION ONLY |
| 26 | Equation normalization | ABSENT |
| 27 | Canonical type checking | ABSENT |
| 28 | Branch comparison | PARTIAL |
| 29 | Uniqueness testing | PARTIAL |
| 30 | Equivalence testing | ABSENT |

**Tally: 7 PRESENT AND EXECUTABLE, 10 PARTIAL, 1 DOCUMENTATION ONLY, 12 ABSENT, 0 STUB.**

No STUB findings — everything present in this codebase, however narrow, is genuine, executing code; nothing
found merely pretends to work.

---

## 3. Independent verification of the two named executable spines

### 3.1 G → L → Spec(L) → K_t → persistence

Confirmed directly from `compiler/protocol/derivation_chainlinks.py` and `compiler/backends/*`:

- `CL-G-TO-L` (`compiler/backends/graph_laplacian.py`) — `L = D − A`, status CALCULATED.
- `CL-L-TO-SPECL` (`compiler/backends/spectral.py`) — real eigendecomposition, VERIFIED, exact sympy
  cross-check for n≤8.
- `CL-SPECL-TO-HEATFLOW` (`compiler/backends/pipeline_graph_heatflow.py`) — `R(t)=e^{-tL}`, VERIFIED.
- `CL-HEATFLOW-TO-KERNEL` — `lim_{t→∞} e^{-tL} = P_ker(L)`, VERIFIED.

This chain is real and independently confirmed. It is the strongest executable spine in the repository,
exactly as the prior audit reported.

### 3.2 Finite spectral triple / Connes inner-fluctuation

Confirmed directly from `compiler/backends/finite_spectral_triple_*.py` and this session's own new module
`finite_spectral_triple_coupled_recovery_spectral_action.py`:

- `D_F = D_B = [[0,d1],[d1^T,0]]` — a real, finite, discrete block-incidence matrix (not a general Dirac
  operator), self-adjointness and grading-anticommutation verified by direct matrix computation.
- `D_F² ` — verified exactly block-diagonal (`diag(d1d1ᵀ, d1ᵀd1)`), an exact numpy matrix identity, not merely
  asserted.
- The original candidate's first-order condition genuinely FAILS (closed-form commutator, confirmed both
  numerically and via small-n sympy symbolic check).
- The coupled-recovery candidate's inner fluctuation `ω = i·[D_F'',π'(f)]`, `D_A'' = D_F''+ω+ε'J''ωJ''⁻¹`,
  is real: self-adjointness of `D_A''` and non-vanishing of `Ω_B''=D_A''²−D_F''²` (max abs ≈36.3) were
  computed by direct numpy matrix arithmetic this session, not asserted.
- What remains merely represented, not derived: the physical interpretation of any of these finite quantities
  as continuum Seeley-DeWitt coefficients (explicitly disclaimed in every relevant module's own docstring),
  and the choice of generator `ω` (one specific, arbitrarily chosen real function `f`, not derived from a
  general `Ω¹_D(A_F)` construction).

Both named spines are real. Neither extends past where this audit's summary table already says the
corresponding capabilities (differential geometry, variational calculus, equivalence/uniqueness testing) stop.

---

## 4. What this means for the program ahead

The repository already has strong numerical/symbolic *calculation* primitives (items 1, 3, 5, 6, 16, 17, 22)
and a real, if node-local rather than graph-wide, status-and-provenance discipline (items 21, 22, and the
detection half of 19). It has essentially no *derivation-search*, *type-checked composition*, or
*invalidation-propagation* infrastructure (items 10, 11, 13, 18, 20, 26, 27, 30 are all ABSENT; item 19 is
detection-only). The task ahead is therefore not "add missing physics modules" — it is "build the derivation,
type, and propagation infrastructure the existing calculation modules should sit underneath," exactly as
`DERIVATION_ENGINE_SPEC.md` (Deliverable 2) proposes.
