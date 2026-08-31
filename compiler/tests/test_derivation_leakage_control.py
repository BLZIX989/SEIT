"""Phase 9 completion: leakage-control admissibility enforcement
(DERIVATION_ENGINE_SPEC.md section 9). DerivationEngine.derive must refuse a
bound premise produced by a FALSIFIED/BLOCKED/uncertified Derivation --
raising the refusal as an honest DERIVATION_FAILED record (audit trail kept)
rather than silently using it or crashing uncaught.
"""
from __future__ import annotations

from compiler.backends.graph_laplacian import build_graph
from compiler.derivation.builtin_theorems import build_default_theorem_registry
from compiler.derivation.derivation import Derivation, DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.obligations import ObligationResult, ProofObligation
from compiler.derivation.theorems import Theorem
from compiler.derivation.types import EpistemicKind, MathObject, MathType


def _register_fake_broken_theorem(registry):
    def _applicable(bound):
        return bound.get("graph") is not None and bound["graph"].math_type == MathType.GRAPH

    def _transform(bound):
        graph_obj = bound["graph"]
        output = MathObject(
            id=f"{graph_obj.id}::L-fake", math_type=MathType.MATRIX,
            epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=graph_obj.carrier.adjacency(),
        )
        bogus_check = lambda: bool((graph_obj.carrier.adjacency().sum(axis=1) > 1000).all())  # noqa: E731
        obligation = ProofObligation(
            "bogus-eigenvalue-bound", "falsely claims all Laplacian eigenvalues > 1000",
            check=bogus_check,
        ).discharge()
        return output, [obligation]

    fake = Theorem(
        theorem_id="THM-FAKE-BROKEN-PSD-LEAKAGE",
        statement="(deliberately false, for leakage-control test)", hypotheses=["graph is given"],
        conclusion="all eigenvalues of L exceed 1000",
        conclusion_type=MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
        domain="test fixture", provenance="leakage-control test fixture -- intentionally false",
        implemented=True, applicability_check=_applicable, transformation=_transform,
    )
    registry.register(fake)
    return fake


def test_falsified_premise_is_refused_as_inadmissible():
    registry = build_default_theorem_registry()
    _register_fake_broken_theorem(registry)
    engine = DerivationEngine(registry)
    g = build_graph("cycle", 6)
    graph_obj = engine.add_object(MathObject(
        id="G-leak", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    falsified = engine.derive("D-FALSIFIED", MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
                               {"graph": graph_obj}, theorem_id="THM-FAKE-BROKEN-PSD-LEAKAGE")
    assert falsified.status == DerivationStatus.FALSIFIED
    falsified_obj = engine.objects[falsified.steps[0].output_id]

    # Attempt to use the falsified object's output as a premise for a new
    # derivation -- must be refused, not silently accepted.
    downstream = engine.derive("D-DOWNSTREAM", MathType.SPECTRUM, {"operator": falsified_obj},
                                theorem_id="THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC")
    assert downstream.status == DerivationStatus.DERIVATION_FAILED
    assert "inadmissible premise" in downstream.note
    assert "D-FALSIFIED" in downstream.note
    assert "FALSIFIED" in downstream.note


def test_blocked_premise_is_refused():
    engine = DerivationEngine(build_default_theorem_registry())
    blocked_obj = MathObject(
        id="X-blocked", math_type=MathType.MATRIX, epistemic_kind=EpistemicKind.DERIVED_RESULT,
        carrier=None,
    )
    engine.derivations.add(Derivation(
        derivation_id="D-BLOCKED-SRC", target_id="X-blocked", status=DerivationStatus.BLOCKED,
    ))
    result = engine.derive("D-USES-BLOCKED", MathType.SPECTRUM, {"operator": blocked_obj},
                            theorem_id="THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC")
    assert result.status == DerivationStatus.DERIVATION_FAILED
    assert "inadmissible premise" in result.note
    assert "BLOCKED" in result.note


def test_definition_and_assumption_objects_never_need_provenance():
    """A raw Graph the caller just constructed (EpistemicKind.DEFINITION) is
    the premise itself, not a claim about one -- it must never be refused
    for lacking a producing Derivation."""
    engine = DerivationEngine(build_default_theorem_registry())
    g = build_graph("path", 5)
    graph_obj = engine.add_object(MathObject(
        id="G-raw", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    d = engine.derive("D-FROM-DEFINITION", MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
                       {"graph": graph_obj}, theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD")
    assert d.status == DerivationStatus.VERIFIED


def test_orphan_derived_result_with_no_provenance_is_refused():
    """A DERIVED_RESULT-kind object with neither a registry_ref nor a
    producing Derivation on record cannot have its admissibility checked --
    the engine must refuse it rather than assume it is fine."""
    engine = DerivationEngine(build_default_theorem_registry())
    orphan = MathObject(
        id="orphan", math_type=MathType.MATRIX, epistemic_kind=EpistemicKind.DERIVED_RESULT,
        carrier=None,
    )
    result = engine.derive("D-USES-ORPHAN", MathType.SPECTRUM, {"operator": orphan},
                            theorem_id="THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC")
    assert result.status == DerivationStatus.DERIVATION_FAILED
    assert "inadmissible premise" in result.note
