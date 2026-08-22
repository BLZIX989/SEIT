"""TEST 8 from the Universal Mathematical Derivation Environment task
(section 20): "FALSIFICATION/RECOVERY -- Deliberately provide a false
intermediate theorem and verify that the system: detects failure,
invalidates dependents, searches alternatives, derives replacement, verifies
replacement, restores downstream computation only after successful
certification."

Exercises InvalidationEngine (compiler/derivation/invalidation.py) and
RecoveryEngine (compiler/derivation/recovery.py) together with
DerivationEngine, using a deliberately-broken theorem registered alongside
the real ones -- the falsification is real (an obligation genuinely fails),
not simulated by hand-setting a status.
"""
from __future__ import annotations

from compiler.backends.graph_laplacian import build_graph
from compiler.derivation.builtin_theorems import build_default_theorem_registry
from compiler.derivation.derivation import DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.invalidation import InvalidationEngine
from compiler.derivation.obligations import ObligationResult, ProofObligation
from compiler.derivation.recovery import RecoveryEngine
from compiler.derivation.theorems import Theorem
from compiler.derivation.types import EpistemicKind, MathObject, MathType


def _register_fake_broken_theorem(registry):
    """A theorem that is applicable and claims to conclude
    PositiveSemidefiniteOperator, but whose own proof obligation genuinely
    fails when actually checked (a rigged, false numeric claim) -- this is
    the "deliberately false intermediate theorem" the task's TEST 8 asks
    for, not a hand-set status."""

    def _applicable(bound):
        return bound.get("graph") is not None and bound["graph"].math_type == MathType.GRAPH

    def _transform(bound):
        graph_obj = bound["graph"]
        output = MathObject(
            id=f"{graph_obj.id}::L-fake", math_type=MathType.MATRIX,
            epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=graph_obj.carrier.adjacency(),
        )
        # A deliberately false claim: asserts every eigenvalue exceeds 1000,
        # which is false for any ordinary graph Laplacian -- the obligation
        # is actually evaluated and actually fails.
        bogus_check = lambda: bool((graph_obj.carrier.adjacency().sum(axis=1) > 1000).all())  # noqa: E731
        obligation = ProofObligation(
            "bogus-eigenvalue-bound", "falsely claims all Laplacian eigenvalues > 1000",
            check=bogus_check,
        ).discharge()
        return output, [obligation]

    fake = Theorem(
        theorem_id="THM-FAKE-BROKEN-PSD",
        statement="(deliberately false, for TEST 8) claims a stronger PSD bound than holds.",
        hypotheses=["graph is given"], conclusion="all eigenvalues of L exceed 1000",
        conclusion_type=MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
        domain="test fixture", provenance="TEST 8 fixture -- intentionally false",
        implemented=True, applicability_check=_applicable, transformation=_transform,
    )
    registry.register(fake)
    return fake


def _setup():
    registry = build_default_theorem_registry()
    _register_fake_broken_theorem(registry)
    engine = DerivationEngine(registry)
    g = build_graph("cycle", 6)
    graph_obj = engine.add_object(MathObject(
        id="G-test8", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    return engine, graph_obj


def test_falsification_is_detected():
    engine, graph_obj = _setup()
    d2 = engine.derive("D2", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                        theorem_id="THM-FAKE-BROKEN-PSD")
    assert d2.status == DerivationStatus.FALSIFIED
    assert d2.proof_obligations[0].result == ObligationResult.FAILED


def test_falsification_invalidates_dependents():
    engine, graph_obj = _setup()
    engine.derive("D2", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                  theorem_id="THM-FAKE-BROKEN-PSD")
    # D3 is a genuine, independently-derivable result that nonetheless
    # declares a provenance dependency on D2 (as a downstream computation
    # that built on D2's now-falsified conclusion would).
    d3 = engine.derive("D3", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                        theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD", dependencies=["D2"])
    assert d3.status == DerivationStatus.VERIFIED  # correct in isolation, before invalidation runs

    invalidation = InvalidationEngine(engine.derivations)
    blocked = invalidation.on_falsified("D2")

    assert "D3" in blocked
    assert engine.derivations.get("D3").status == DerivationStatus.BLOCKED
    assert "falsified 'D2'" in engine.derivations.get("D3").note
    # the falsified node itself is left exactly as it is -- never overwritten
    assert engine.derivations.get("D2").status == DerivationStatus.FALSIFIED


def test_recovery_finds_admissible_alternative_and_restores_downstream():
    engine, graph_obj = _setup()
    engine.derive("D2", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                  theorem_id="THM-FAKE-BROKEN-PSD")
    d3 = engine.derive("D3", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                        theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD", dependencies=["D2"])
    InvalidationEngine(engine.derivations).on_falsified("D2")
    assert engine.derivations.get("D3").status == DerivationStatus.BLOCKED

    recovery = RecoveryEngine(engine)
    recovered = recovery.recover(
        "D3", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
        exclude_theorem_ids=frozenset({"THM-FAKE-BROKEN-PSD"}),
    )

    # restored only via a NEW, separately-certified Derivation record
    assert recovered.derivation_id == "D3-recovery"
    assert recovered.status == DerivationStatus.CANONICAL
    assert recovered.recovers == "D3"
    assert recovered.provenance["theorem"] == "THM-SYMMETRIC-QUADRATIC-FORM-PSD"
    # the original BLOCKED record is preserved (never deleted), only marked superseded
    original = engine.derivations.get("D3")
    assert original.status == DerivationStatus.SUPERSEDED
    assert original.superseded_by == "D3-recovery"
    assert "D3" in engine.derivations.ids()  # still readable for audit


def test_recovery_honestly_fails_when_no_admissible_alternative_exists():
    engine, graph_obj = _setup()
    engine.derive("D2", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                  theorem_id="THM-FAKE-BROKEN-PSD")
    # D4 targets a type (Connection) whose only registered theorem
    # (THM-LEVI-CIVITA-UNIQUENESS) is a real citation but `implemented=False`
    # -- there genuinely is no admissible, executable alternative yet.
    d4 = engine.add_object(MathObject(
        id="D4-target", math_type=MathType.CONNECTION, epistemic_kind=EpistemicKind.ASSUMPTION,
        carrier=None,
    ))
    from compiler.derivation.derivation import Derivation
    engine.derivations.add(Derivation(
        derivation_id="D4", target_id="D4-target", dependencies=["D2"],
        status=DerivationStatus.DERIVED,
    ))
    InvalidationEngine(engine.derivations).on_falsified("D2")
    assert engine.derivations.get("D4").status == DerivationStatus.BLOCKED

    recovery = RecoveryEngine(engine)
    recovered = recovery.recover("D4", MathType.CONNECTION, {})

    assert recovered.status == DerivationStatus.DERIVATION_FAILED
    assert "not implemented" in recovered.note
    # the original stays BLOCKED -- recovery must never force a closure
    original = engine.derivations.get("D4")
    assert original.status == DerivationStatus.BLOCKED
    assert original.superseded_by is None
