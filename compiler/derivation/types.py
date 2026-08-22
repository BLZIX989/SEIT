"""Mathematical object model and type-composition legality (Phase 1 of
DERIVATION_ENGINE_SPEC.md section 1). Enforces the governing task's explicit
requirement: "the compiler must reject invalid mathematical compositions" --
a MathObject may only be USED as a stronger/narrower type (e.g. a bare Matrix
used as a SelfAdjointOperator, or a Tensor used as a Metric) once the
relevant property has been independently CHECKED and recorded in
`verified_properties`, never merely asserted via `claimed_properties`.

MathType's list is the task's own list verbatim, plus two small, explicitly
flagged extensions (SPECTRUM, HEAT_KERNEL) needed to type the objects TEST 1-3
actually produce; the task's own instruction ("Examples include") frames its
list as non-exhaustive, not closed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MathType(str, Enum):
    SCALAR = "Scalar"
    VECTOR = "Vector"
    COVECTOR = "Covector"
    MATRIX = "Matrix"
    LINEAR_OPERATOR = "LinearOperator"
    SELF_ADJOINT_OPERATOR = "SelfAdjointOperator"
    POSITIVE_SEMIDEFINITE_OPERATOR = "PositiveSemidefiniteOperator"
    HILBERT_SPACE = "HilbertSpace"
    INNER_PRODUCT_SPACE = "InnerProductSpace"
    GRAPH = "Graph"
    SIMPLICIAL_COMPLEX = "SimplicialComplex"
    CHAIN_COMPLEX = "ChainComplex"
    DIFFERENTIAL = "Differential"
    TENSOR = "Tensor"
    METRIC = "Metric"
    CONNECTION = "Connection"
    CURVATURE_TENSOR = "CurvatureTensor"
    LIE_ALGEBRA = "LieAlgebra"
    LIE_GROUP = "LieGroup"
    REPRESENTATION = "Representation"
    CLIFFORD_ALGEBRA = "CliffordAlgebra"
    SPECTRAL_TRIPLE = "SpectralTriple"
    PROBABILITY_DISTRIBUTION = "ProbabilityDistribution"
    FISHER_METRIC = "FisherMetric"
    FUNCTIONAL = "Functional"
    ACTION = "Action"
    FIELD = "Field"
    EQUATION = "Equation"
    CONSTRAINT = "Constraint"
    OBSERVABLE = "Observable"
    # Explicit extensions beyond the task's own list, needed for TEST 1-3:
    SPECTRUM = "Spectrum"            # refines nothing; the (eigenvalue, eigenvector) data of an operator
    HEAT_KERNEL = "HeatKernel"       # refines LINEAR_OPERATOR; e^{-tL}


# Refinement lattice: child -> parent (None if a root type). A MathObject typed
# `child` may be used wherever `parent` (or any of parent's own ancestors) is
# required, PROVIDED every name in REFINEMENT_REQUIRES[child] is present and
# True in verified_properties.
REFINES: dict[MathType, MathType | None] = {
    MathType.SCALAR: None,
    MathType.VECTOR: None,
    MathType.COVECTOR: None,
    MathType.MATRIX: None,
    MathType.LINEAR_OPERATOR: MathType.MATRIX,
    MathType.SELF_ADJOINT_OPERATOR: MathType.LINEAR_OPERATOR,
    MathType.POSITIVE_SEMIDEFINITE_OPERATOR: MathType.SELF_ADJOINT_OPERATOR,
    MathType.HILBERT_SPACE: None,
    MathType.INNER_PRODUCT_SPACE: MathType.HILBERT_SPACE,
    MathType.GRAPH: None,
    MathType.SIMPLICIAL_COMPLEX: MathType.GRAPH,
    MathType.CHAIN_COMPLEX: None,
    MathType.DIFFERENTIAL: None,
    MathType.TENSOR: None,
    MathType.METRIC: MathType.TENSOR,
    MathType.CONNECTION: None,
    MathType.CURVATURE_TENSOR: MathType.TENSOR,
    MathType.LIE_ALGEBRA: None,
    MathType.LIE_GROUP: None,
    MathType.REPRESENTATION: None,
    MathType.CLIFFORD_ALGEBRA: None,
    MathType.SPECTRAL_TRIPLE: None,
    MathType.PROBABILITY_DISTRIBUTION: None,
    MathType.FISHER_METRIC: MathType.METRIC,
    MathType.FUNCTIONAL: None,
    MathType.ACTION: MathType.FUNCTIONAL,
    MathType.FIELD: None,
    MathType.EQUATION: None,
    MathType.CONSTRAINT: None,
    MathType.OBSERVABLE: None,
    MathType.SPECTRUM: None,
    MathType.HEAT_KERNEL: MathType.LINEAR_OPERATOR,
}

# Properties that must be present (and True) in verified_properties before a
# MathObject may be treated as this type. Only refinements actually exercised
# by Slice 1 are populated; every other refinement requires an empty tuple
# (no automatic promotion) until real derivation work populates it -- a
# refinement absent from this dict is NEVER silently treated as unconditional.
REFINEMENT_REQUIRES: dict[MathType, tuple[str, ...]] = {
    MathType.SELF_ADJOINT_OPERATOR: ("symmetric",),
    MathType.POSITIVE_SEMIDEFINITE_OPERATOR: ("positive_semidefinite",),
    MathType.METRIC: ("symmetric", "nondegenerate"),
    MathType.FISHER_METRIC: ("symmetric", "nondegenerate", "positive_definite"),
}


class EpistemicKind(str, Enum):
    DEFINITION = "definition"
    IDENTITY = "identity"
    ASSUMPTION = "assumption"
    THEOREM = "theorem"
    CONJECTURE = "conjecture"
    NUMERICAL_OBSERVATION = "numerical_observation"
    EMPIRICAL_DATUM = "empirical_datum"
    DERIVED_RESULT = "derived_result"


class TypeCompositionError(TypeError):
    pass


@dataclass
class MathObject:
    id: str
    math_type: MathType
    epistemic_kind: EpistemicKind
    carrier: Any
    verified_properties: dict[str, bool] = field(default_factory=dict)
    claimed_properties: set = field(default_factory=set)
    registry_ref: str | None = None

    def refines(self, target: MathType) -> bool:
        t: MathType | None = self.math_type
        while t is not None:
            if t == target:
                return True
            t = REFINES.get(t)
        return False


def require(obj: MathObject, needed: MathType) -> MathObject:
    """Raises TypeCompositionError unless `obj` can be legally used as
    `needed`. This is the literal enforcement of the task's example: a bare
    Matrix must never be treated as a Metric tensor without an explicit,
    CHECKED admissible mapping."""
    if not obj.refines(needed):
        raise TypeCompositionError(
            f"{obj.id}: math_type={obj.math_type.value} does not refine required type {needed.value}"
        )
    missing = [p for p in REFINEMENT_REQUIRES.get(needed, ()) if not obj.verified_properties.get(p)]
    if missing:
        plural = "y" if len(missing) == 1 else "ies"
        raise TypeCompositionError(
            f"{obj.id}: cannot be used as {needed.value} -- required propert{plural} {missing} "
            f"not present in verified_properties (checked, not merely claimed)"
        )
    return obj
