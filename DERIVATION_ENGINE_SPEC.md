# DERIVATION_ENGINE_SPEC.md

Deliverable 2 of the Universal Mathematical Derivation Environment program. This
specification defines the architecture requested in the governing task, built
**underneath** the existing MDCL/chainlink architecture (`DERIVATION_ENVIRONMENT_AUDIT.md`
§4), not in place of it. Nothing here proposes deleting, renaming, or reinterpreting any
existing Object, Transformation, Equation, Chainlink, Protocol, or Status value.

## 0. Where this sits

```
MASTER CLOSURE DAG            (existing: master_mdcl.json, status_matrix.json)
        |
CHAINLINK REGISTRY             (existing: chainlink_registry.json, protocol_matrix.json)
        |
DERIVATION GRAPH                <- NEW: compiler/derivation/
        |
MATHEMATICAL OBJECT GRAPH        <- NEW: compiler/derivation/types.py
        |
SYMBOLIC / NUMERICAL EXECUTION   <- existing sympy/numpy calls, now invoked THROUGH
        |                            compiler/derivation/engine.py rather than ad hoc
PROOF OBLIGATIONS                <- NEW, structured: compiler/derivation/obligations.py
        |
VERIFICATION                     <- existing self-audit + NEW per-obligation checks
        |
FALSIFICATION                    <- existing compiler/falsification/, reused as-is
        |
RECOVERY                         <- NEW: compiler/derivation/recovery.py
        |
CERTIFICATION                    <- NEW mapping onto existing compiler/core/status.py
        |
CANONICAL STATE                  (existing registries, unchanged in shape)
```

A `Derivation` is a new kind of record, stored in a new `derivation_registry.json`
alongside (not replacing) `calculation_registry.json`. An existing Chainlink may
optionally reference the `Derivation` that produced it (`derivation_id: str | None`,
additive field, defaults to `None` so every existing chainlink stays valid).

## 1. Mathematical object model (the type system)

### 1.1 `MathType`

A closed enumeration matching the task's list exactly, organized as a **refinement
lattice**, not a flat list — each type optionally names a `refines: MathType | None`:

```python
class MathType(str, Enum):
    SCALAR = "Scalar"
    VECTOR = "Vector"
    COVECTOR = "Covector"
    MATRIX = "Matrix"
    LINEAR_OPERATOR = "LinearOperator"          # refines MATRIX (finite-dim case)
    SELF_ADJOINT_OPERATOR = "SelfAdjointOperator"  # refines LINEAR_OPERATOR
    POSITIVE_SEMIDEFINITE_OPERATOR = "PositiveSemidefiniteOperator"  # refines SELF_ADJOINT_OPERATOR
    HILBERT_SPACE = "HilbertSpace"
    INNER_PRODUCT_SPACE = "InnerProductSpace"    # refines HILBERT_SPACE (finite-dim, complete trivially)
    GRAPH = "Graph"
    SIMPLICIAL_COMPLEX = "SimplicialComplex"     # refines GRAPH (1-skeleton)
    CHAIN_COMPLEX = "ChainComplex"
    DIFFERENTIAL = "Differential"                 # an operator on a ChainComplex, d^2=0 checkable
    TENSOR = "Tensor"                              # carries (covariant_rank, contravariant_rank)
    METRIC = "Metric"                              # refines TENSOR, rank (0,2), symmetric + nondegenerate
    CONNECTION = "Connection"
    CURVATURE_TENSOR = "CurvatureTensor"           # refines TENSOR, rank (1,3)
    LIE_ALGEBRA = "LieAlgebra"
    LIE_GROUP = "LieGroup"
    REPRESENTATION = "Representation"
    CLIFFORD_ALGEBRA = "CliffordAlgebra"
    SPECTRAL_TRIPLE = "SpectralTriple"              # a bundle: (Algebra, HilbertSpace, LinearOperator, ...)
    PROBABILITY_DISTRIBUTION = "ProbabilityDistribution"
    FISHER_METRIC = "FisherMetric"                  # refines METRIC
    FUNCTIONAL = "Functional"
    ACTION = "Action"                                # refines FUNCTIONAL
    FIELD = "Field"
    EQUATION = "Equation"
    CONSTRAINT = "Constraint"
    OBSERVABLE = "Observable"
```

### 1.2 `EpistemicKind`

Every `MathObject` also carries what *kind* of claim it is — this is the distinction
the task calls out explicitly in §5 ("definition / identity / assumption / theorem /
conjecture / numerical observation / empirical datum / derived result"):

```python
class EpistemicKind(str, Enum):
    DEFINITION = "definition"
    IDENTITY = "identity"
    ASSUMPTION = "assumption"
    THEOREM = "theorem"
    CONJECTURE = "conjecture"
    NUMERICAL_OBSERVATION = "numerical_observation"
    EMPIRICAL_DATUM = "empirical_datum"
    DERIVED_RESULT = "derived_result"
```

### 1.3 `MathObject`

```python
@dataclass
class MathObject:
    id: str
    math_type: MathType
    epistemic_kind: EpistemicKind
    carrier: Any                 # the real payload: np.ndarray, sympy.Matrix, a small
                                  # dataclass for Graph/SpectralTriple/etc.
    verified_properties: dict[str, bool]   # e.g. {"symmetric": True, "positive_semidefinite": True}
                                  # populated ONLY by an executed check (never asserted)
    claimed_properties: set[str] # properties asserted but not (yet) checked
    registry_ref: str | None     # id of the existing Object/Transformation/Equation this
                                  # corresponds to, if any (additive cross-reference)
```

### 1.4 Composition legality

`compiler/derivation/types.py` exposes:

```python
def require(obj: MathObject, needed: MathType) -> MathObject:
    """Raises TypeCompositionError unless obj.math_type refines (or equals) needed
    AND every property that refinement requires is in obj.verified_properties (not
    merely claimed_properties). This is the literal implementation of the task's
    'the compiler must reject invalid mathematical compositions' requirement."""
```

Example enforced today by Slice 1 (§5 of the implementation plan): a `Matrix` may be
used as a `SelfAdjointOperator` only if `verified_properties["symmetric"] is True`,
and as a `PositiveSemidefiniteOperator` only if `verified_properties["positive_semidefinite"]
is True` — both populated by an executed numeric or symbolic check, never by
construction-time assertion. A bare numpy matrix can never be passed where the type
system requires `Metric` (rank-(0,2), symmetric, nondegenerate tensor) without an
explicit, checked `as_metric()` conversion — directly implementing §5's example.

## 2. The Derivation object

```python
@dataclass
class DerivationStep:
    step_id: str
    rule_id: str                  # references a Theorem in the TheoremRegistry (§3)
    input_ids: list[str]          # MathObject ids bound as this rule's hypotheses
    output_id: str                # MathObject id this step produces
    symbolic_form: str | None     # human/sympy-readable form of what this step states
    numeric_evidence: dict | None # e.g. {"residual": 1.1e-16, "method": "np.allclose"}
    symbolic_evidence: dict | None # e.g. {"sympy_equal": True, "n": 4}

@dataclass
class Derivation:
    derivation_id: str
    target_id: str                 # the MathObject this derivation is trying to produce
    inputs: list[str]               # MathObject ids taken as given
    assumptions: list[str]          # MathObject ids of EpistemicKind.ASSUMPTION
    definitions: list[str]          # MathObject ids of EpistemicKind.DEFINITION
    steps: list[DerivationStep]     # the ACTUAL sequence of transformations (never
                                     # a bare "therefore X follows" — see task §4)
    proof_obligations: list["ProofObligation"]   # see §4
    dependencies: list[str]         # other derivation_ids this one depends on
    provenance: dict                 # same shape as compiler/provenance/provenance.py's output
    status: "DerivationStatus"       # see §6
```

This directly implements the task's requirement that a derivation "must contain the
actual sequence of transformations that produced the equation," using the task's own
worked example (`L=D-A` → `xᵀLx=xᵀ(D-A)x` → graph identity → `xᵀLx≥0` → obligations) as
the literal shape of `steps`.

## 3. The established-mathematics library (Theorem/Rule registry)

```python
@dataclass
class Theorem:
    theorem_id: str
    statement: str
    hypotheses: list[str]           # human-readable; §7's applicability_check enforces them
    conclusion: str
    domain: str                      # e.g. "linear algebra", "spectral graph theory"
    provenance: str                  # citation, e.g. "standard linear algebra" or "Belkin-Niyogi 2005"
    applicability_check: Callable[[dict[str, MathObject]], bool]
    transformation: Callable[[dict[str, MathObject]], MathObject]
    verification_tests: list[Callable[[dict[str, MathObject], MathObject], bool]]
    implemented: bool                # False = statement/citation recorded but
                                       # applicability_check/transformation are NotImplemented stubs;
                                       # NEVER silently treated as usable by the engine (§7)
```

`TheoremRegistry` is a plain `dict[str, Theorem]`. Per the audit's finding that this
repository already has zero queryable established-mathematics library (item 25:
DOCUMENTATION ONLY), Slice 1 populates exactly the theorems needed for TEST 1–3
(`THM-SYMMETRIC-QUADRATIC-FORM-PSD`, `THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC`,
`THM-MATRIX-EXPONENTIAL-SEMIGROUP`) as **fully implemented**, and records the rest of
the task's §6 list (Hodge decomposition, `d²=0`, Euler–Lagrange, Noether, Levi-Civita
uniqueness, Bianchi identities, Lichnerowicz formula, heat-kernel expansion,
Seeley-DeWitt coefficients, Clifford relations) as **registered but `implemented=False`**
— present in the library as citable, structured entries with real statements and
provenance, but the engine refuses to invoke an unimplemented theorem's
`applicability_check`/`transformation` (raises `TheoremNotImplemented`, a distinct,
honest failure mode from "theorem does not apply here").

## 4. Proof obligations

```python
class ObligationResult(str, Enum):
    SATISFIED = "SATISFIED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    NOT_TESTED = "NOT_TESTED"

@dataclass
class ProofObligation:
    obligation_id: str
    description: str
    check: Callable[[], bool] | None   # None => result is forced to NOT_TESTED
    result: ObligationResult
    evidence: str
```

Every `Theorem.transformation` call that produces a new `MathObject` also emits the
obligations its `hypotheses` implied (e.g. recovering a `Metric` emits obligations
for symmetry, nondegeneracy, signature, representation-invariance, continuum
compatibility — the exact list the task gives in §16). Each obligation is discharged
independently and recorded; a derivation's overall status can never exceed what its
weakest **tested** obligation supports, and any `NOT_TESTED` obligation caps the
derivation at `CONDITIONAL` at best (see §6).

## 5. Execution model

`compiler/derivation/engine.py::DerivationEngine`:

```python
class DerivationEngine:
    def __init__(self, registries: MDCLRegistries, theorems: TheoremRegistry,
                 objects: dict[str, MathObject]):
        ...

    def derive(self, target_id: str) -> Derivation:
        """
        1. Resolve target_id's required MathType and known premises from `objects`
           and from the existing MDCLRegistries (Objects/Transformations/Equations
           already registered there are visible as premises with EpistemicKind
           inferred from their compiler Status: VERIFIED/DERIVED -> THEOREM-tier
           premise; CALCULATED -> NUMERICAL_OBSERVATION-tier premise; OPEN/PROPOSED
           -> unusable as a premise, per the leakage-control discipline in
           compiler/verification/self_audit.py, reused unchanged here).
        2. Enumerate theorems in `theorems` whose `conclusion` type-matches target_id's
           required MathType. Only `implemented=True` theorems are candidates.
        3. For each candidate, evaluate `applicability_check` against the bound
           premises. Reject and record (not silently drop) every candidate whose
           applicability_check fails.
        4. For the first (or, if `search_all=True`, every) applicable candidate,
           execute `transformation`, run `verification_tests`, discharge the
           resulting ProofObligations, and append a DerivationStep.
        5. Compute the Derivation's DerivationStatus (see §6) from the obligation
           results and verification_tests outcomes.
        6. Persist the Derivation to derivation_registry.json. If status reaches
           CANONICAL, optionally register/update the corresponding compiler Object/
           Transformation via the EXISTING registries.objects.add_object /
           make_provenance calls -- never by hand-editing JSON.
        """
```

This is intentionally a thin orchestrator: it does not reimplement numpy/sympy calls;
it calls into existing `compiler/backends/*` functions as the `transformation` payload
wherever one already exists (e.g. `THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC`'s
transformation literally calls `compiler.backends.spectral.spectrum`), so no existing
calculation code is duplicated or forked.

## 6. Failure and certification model — `DerivationStatus`

The task's governing principle (§0) specifies a 7-stage forward chain plus 7 failure
branches. This is a **new, additive** enum, used only on `Derivation` records — it does
**not** replace `compiler.core.status.Status`, which continues to govern canonical
Objects/Transformations/Equations exactly as today:

```python
class DerivationStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"                # a claim exists in source material only
    FORMALIZED = "FORMALIZED"                # restated as typed MathObjects + a target
    DERIVABLE = "DERIVABLE"                   # an applicable theorem chain was found
    DERIVED = "DERIVED"                       # the chain was executed once, symbolically and/or numerically
    EXECUTED = "EXECUTED"                     # all steps ran without error
    VERIFIED = "VERIFIED"                     # every proof obligation SATISFIED
    CANONICAL = "CANONICAL"                   # VERIFIED + registered into the existing MDCL registries
    DERIVATION_FAILED = "DERIVATION_FAILED"   # no applicable theorem chain found
    FALSIFIED = "FALSIFIED"                   # a verification_test or obligation returned FAILED
    CONDITIONAL = "CONDITIONAL"               # >=1 obligation NOT_TESTED or a free/unjustified parameter
    BLOCKED = "BLOCKED"                       # depends on a derivation that is itself not CANONICAL
    SUPERSEDED = "SUPERSEDED"                 # a later Derivation for the same target_id was preferred
    RETIRED = "RETIRED"                       # explicitly closed, kept for audit (task's §0.1 "Retired")
    UNRESOLVED = "UNRESOLVED"                 # open research question, no candidate attempted
```

**Mapping onto the existing `compiler.core.status.Status`**, applied only at the
moment a Derivation is registered into the canonical MDCL registries (step 6 above) —
this is the single integration point, and it is one-directional (Derivation → Status,
never the reverse):

| DerivationStatus | Status (existing enum) |
|---|---|
| CANONICAL (all obligations SATISFIED, ≥1 numeric+symbolic cross-check) | VERIFIED |
| CANONICAL (obligations SATISFIED via a single evidence tier only) | DERIVED or CALCULATED (per existing DERIVED-vs-CALCULATED distinction in compiler/core/status.py's own docstring) |
| CONDITIONAL | CONDITIONAL |
| DERIVATION_FAILED, BLOCKED, UNRESOLVED | OPEN |
| FALSIFIED | FALSIFIED |
| everything else (DOCUMENTED, FORMALIZED, DERIVABLE, DERIVED-not-yet-EXECUTED, EXECUTED-not-yet-VERIFIED, SUPERSEDED, RETIRED) | never registered into the canonical registries at all — these are pre-canonical or historical Derivation-layer-only states |

`SUPERSEDED`/`RETIRED` Derivations are never deleted (task §30): they remain in
`derivation_registry.json` forever, with a `superseded_by: derivation_id` field, giving
the historical-audit guarantee the task requires without needing a new terminal value
on the existing `Status` enum.

## 7. Falsification → invalidation → recovery loop

This is the architectural centerpiece the task calls "the most important addition."

### 7.1 Invalidation (closing the gap the audit found in item 19)

```python
class InvalidationEngine:
    def on_falsified(self, node_id: str, graph: DependencyGraph) -> list[str]:
        """Reuses the EXISTING DependencyGraph (compiler/verification/self_audit.py's
        build_dependency_graph, built on compiler/dependencies/graph.py) rather than
        building a parallel one. Walks graph.descendants(node_id) -- already
        implemented there, symmetric with the existing .ancestors(), confirmed present
        during the Phase-1 audit rather than assumed. For each descendant lacking its
        own INDEPENDENT derivation_id (one whose `dependencies` list does not transit
        node_id), marks the corresponding Derivation's status DerivationStatus.BLOCKED
        and records why. Returns the list of newly-blocked derivation_ids."""
```

This turns `leakage_control_audit`'s existing passive detection into an active
consequence: falsifying a node now visibly blocks its dependents in
`derivation_registry.json`, rather than merely failing an audit if a human lets it
happen.

### 7.2 Recovery

```python
class RecoveryEngine:
    def recover(self, blocked_derivation_id: str) -> list[Derivation]:
        """
        1. Read the blocked Derivation's target_id and its ORIGINAL admissibility
           requirements (the proof obligations it was supposed to discharge).
        2. Re-run DerivationEngine.derive(target_id, search_all=True) against the
           THEOREM REGISTRY, excluding the specific transformation(s) that produced
           the falsified upstream object.
        3. For every newly-applicable candidate chain, execute it, discharge
           obligations, and report its DerivationStatus honestly -- INCLUDING
           DERIVATION_FAILED if no candidate is admissible. The task is explicit
           (§9, §23) that 'no currently admissible construction exists' is a valid,
           terminal answer this engine must be able to return, not a bug to fix by
           relaxing an obligation.
        4. Never mutates or deletes the original falsified Derivation; only ever adds
           new Derivation records with `recovers: blocked_derivation_id` provenance.
        """
```

## 8. Equivalence and uniqueness engines

```python
class EquivalenceEngine:
    def classify(self, a: MathObject, b: MathObject) -> Literal[
        "distinct_theory", "same_theory_different_representation",
        "equivalent_parameterization", "gauge_equivalent",
        "coordinate_transformation", "basis_transformation",
        "numerical_approximation", "distinct_candidate", "unknown"]:
        """Only ever returns a classification stronger than 'unknown' when a
        registered, implemented equivalence CHECK (e.g. an explicit change-of-basis
        matrix verified to intertwine a and b's carriers) actually ran. Absent such a
        check, returns 'unknown' -- never infers equivalence from matching output
        values alone (task Sec 14's own warning against exactly that mistake)."""

class UniquenessEngine:
    def admissible_set(self, target_type: MathType, constraints: list[ProofObligation]
                        ) -> Literal["empty", "singleton", "finite", "continuous", "unknown"]:
        """Runs every implemented theorem whose conclusion matches target_type against
        the given constraints, collects every candidate whose obligations are
        SATISFIED, and reports the CARDINALITY FINDING ONLY -- 'singleton' requires an
        actual argument that no other candidate can satisfy the constraints (e.g. a
        cited uniqueness theorem's applicability_check also holding), not merely that
        the search found exactly one candidate among those it happened to try. Default
        finding when only one candidate was found and no uniqueness argument was run:
        'unknown', explicitly NOT 'singleton' (task Sec 15's central requirement)."""
```

## 9. Registry integration and the leakage-control rule (task §18)

`DerivationEngine.derive` only accepts premises whose existing compiler `Status` is in
`{VERIFIED, DERIVED, CALCULATED}` (mirrors `LEAKAGE_ACTIVE_STATUSES` in
`compiler/verification/self_audit.py`, imported not reimplemented) or whose
`DerivationStatus` is `CANONICAL`. `FALSIFIED`, `FAIL`, `CONDITIONAL`-without-explicit-
opt-in, `OPEN`, and `PROPOSED` nodes are refused as premises — the engine raises
`InadmissiblePremise` rather than silently proceeding. This is the same discipline
`leakage_control_audit` already checks for after the fact, now enforced *before* a new
derivation can even start.

## 10. Provenance

Every `Derivation.provenance` dict has the same shape `compiler/provenance/provenance.py::make_provenance`
already produces (`source`, `calculation_id`, `status`, `verification`), plus two new,
additive fields: `source_document` (the DER-ID / CMRC-ID / paper section a documented
claim originally came from, when applicable — using the same crosswalk built in the
Documentation Conformance Audit) and `historical_candidates: list[str]` (derivation_ids
of every superseded/retired attempt at the same target, so a recovered result B'
never erases the record of B — task §17's explicit requirement).

## 11. What Slice 1 (the first implementation) will and will not do

Per the task's own gating instruction ("do not implement until you have shown 1-7"),
this spec is deliberately silent on writing implementation code beyond describing it.
`DERIVATION_ENGINE_IMPLEMENTATION_PLAN.md` (Deliverable 3) sequences the build; the
first executable slice (TEST 1 + TEST 8) is implemented immediately after this spec
and the plan, as the concrete proof that the design above actually runs.
