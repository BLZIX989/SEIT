"""Phase 12: UniquenessEngine. The required verification (implementation
plan, Phase 12) is a re-run against the project's own already-known GEO-001
case: compiler/falsification/eigen_uniqueness.py's executed counterexample
that Spec(H) does not determine H (H and H'=UHU^dagger share an identical
spectrum but H != H'). UniquenessEngine.admissible_set must report 'unknown'
or 'continuous' for that scenario -- never 'singleton' -- confirming it does
not accidentally certify what this project's own prior audit already
falsified.
"""
from __future__ import annotations

import numpy as np

from compiler.derivation.engine import DerivationEngine
from compiler.derivation.obligations import ObligationResult, ProofObligation
from compiler.derivation.theorems import Theorem, TheoremRegistry
from compiler.derivation.types import EpistemicKind, MathObject, MathType
from compiler.derivation.uniqueness import UniquenessEngine
from compiler.falsification.eigen_uniqueness import run_counterexample


def _reconstruction_theorem(theorem_id: str, candidate_matrix: np.ndarray, *,
                             proves_uniqueness: bool = False) -> Theorem:
    """A synthetic 'reconstruct H from Spec(H)' theorem whose only obligation
    is the one the counterexample actually turns on: does the candidate have
    the target spectrum. Mirrors a real recovery-construction shape without
    inventing new physics -- the point under test is UniquenessEngine's own
    honesty discipline, not this fixture."""

    def _applicable(bound):
        return bound.get("target_spectrum") is not None

    def _transform(bound):
        target_spectrum = bound["target_spectrum"]
        # atol accounts for eigen_uniqueness.run_counterexample's own
        # 4-decimal rounding of example_H/example_H_prime for display -- the
        # counterexample's underlying claim (residual < 1e-8 pre-rounding)
        # is independently established there, not re-derived here.
        matches = bool(np.allclose(
            sorted(np.linalg.eigvalsh(candidate_matrix)), sorted(target_spectrum), atol=1e-3,
        ))
        obligation = ProofObligation(
            "matches-target-spectrum", "candidate's eigenvalues equal the target spectrum",
            check=lambda: matches,
        ).discharge()
        output = MathObject(
            id=f"{theorem_id}::H", math_type=MathType.SELF_ADJOINT_OPERATOR,
            epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=candidate_matrix,
        )
        return output, [obligation]

    return Theorem(
        theorem_id=theorem_id,
        statement="(test fixture) a candidate H reconstructed from a target spectrum",
        hypotheses=["target_spectrum is given"], conclusion="H has the target spectrum",
        conclusion_type=MathType.SELF_ADJOINT_OPERATOR, domain="test fixture",
        provenance="GEO-001 uniqueness test fixture", implemented=True,
        applicability_check=_applicable, transformation=_transform,
        proves_uniqueness=proves_uniqueness,
    )


def test_geo001_two_distinct_operators_sharing_a_spectrum_are_never_singleton():
    cx = run_counterexample(n=2, n_trials=25, seed=0)
    assert cx.matrices_differ, "fixture precondition: the counterexample must actually confirm H != H'"
    H = np.array(cx.example_H)
    H_prime = np.array(cx.example_H_prime)
    target_spectrum = np.linalg.eigvalsh(H)

    registry = TheoremRegistry()
    registry.register(_reconstruction_theorem("THM-RECON-A", H))
    registry.register(_reconstruction_theorem("THM-RECON-B", H_prime))
    engine = DerivationEngine(registry)
    uniqueness = UniquenessEngine(engine)

    classification, satisfying = uniqueness.admissible_set(
        MathType.SELF_ADJOINT_OPERATOR, {"target_spectrum": target_spectrum},
    )
    assert classification in ("unknown", "continuous")
    assert classification != "singleton"
    assert len(satisfying) == 2


def test_single_candidate_without_uniqueness_proof_is_unknown_not_singleton():
    registry = TheoremRegistry()
    registry.register(_reconstruction_theorem("THM-ONLY-ONE", np.eye(2)))
    engine = DerivationEngine(registry)
    uniqueness = UniquenessEngine(engine)

    classification, satisfying = uniqueness.admissible_set(
        MathType.SELF_ADJOINT_OPERATOR, {"target_spectrum": np.array([1.0, 1.0])},
    )
    assert classification == "unknown"
    assert len(satisfying) == 1


def test_single_candidate_with_genuine_uniqueness_proof_is_singleton():
    registry = TheoremRegistry()
    registry.register(_reconstruction_theorem("THM-PROVEN-UNIQUE", np.eye(2), proves_uniqueness=True))
    engine = DerivationEngine(registry)
    uniqueness = UniquenessEngine(engine)

    classification, satisfying = uniqueness.admissible_set(
        MathType.SELF_ADJOINT_OPERATOR, {"target_spectrum": np.array([1.0, 1.0])},
    )
    assert classification == "singleton"
    assert len(satisfying) == 1


def test_no_satisfying_candidate_is_unknown_not_empty():
    registry = TheoremRegistry()
    engine = DerivationEngine(registry)
    uniqueness = UniquenessEngine(engine)
    classification, satisfying = uniqueness.admissible_set(
        MathType.SELF_ADJOINT_OPERATOR, {"target_spectrum": np.array([1.0, 1.0])},
    )
    assert classification == "unknown"
    assert satisfying == []
