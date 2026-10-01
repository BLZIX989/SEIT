"""The user's own requested trial: "derive something using established
physics only, just to see what happens" -- run before any branch
reorganization, as an end-to-end proof that the derivation environment can
carry a real, textbook-established physics result (not a SEIT/UOC-specific
claim) all the way to CANONICAL registration with a genuine evidence
record. Both theorems here reproduce results SRO Established Core's own
audit named as real, checked, non-hand-wavy steps.
"""
from __future__ import annotations

from compiler.derivation.certification import register_canonical_derivation
from compiler.derivation.derivation import DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.established_physics_theorems import register_established_physics_theorems
from compiler.derivation.obligations import ObligationResult
from compiler.derivation.theorems import TheoremRegistry
from compiler.derivation.types import EpistemicKind, MathObject, MathType
from compiler.core.status import Status
from compiler.ir.registry import MDCLRegistries


def _make_engine():
    return DerivationEngine(register_established_physics_theorems(TheoremRegistry()))


def test_qcd_one_loop_beta_function_reaches_canonical():
    engine = _make_engine()
    gauge_group = engine.add_object(MathObject(
        id="gauge-group-SU3", math_type=MathType.LIE_GROUP, epistemic_kind=EpistemicKind.DEFINITION,
        carrier="SU(3)",
    ))
    n_f = engine.add_object(MathObject(
        id="n_f-six-flavors", math_type=MathType.SCALAR, epistemic_kind=EpistemicKind.DEFINITION,
        carrier=6,
    ))

    d = engine.derive("D-QCD-BETA", MathType.EQUATION, {"gauge_group": gauge_group, "n_f": n_f},
                       theorem_id="THM-QCD-ONE-LOOP-BETA-FUNCTION")

    assert d.status == DerivationStatus.VERIFIED
    coeff = next(o for o in d.proof_obligations if o.obligation_id == "beta-function-coefficient-exact")
    sign = next(o for o in d.proof_obligations
                if o.obligation_id == "asymptotic-freedom-sign-for-all-positive-coupling")
    assert coeff.result == ObligationResult.SATISFIED
    assert sign.result == ObligationResult.SATISFIED

    result_obj = engine.objects[d.steps[0].output_id]
    assert result_obj.carrier.b3 == -7
    assert result_obj.carrier.asymptotically_free is True

    registries = MDCLRegistries()
    obj = register_canonical_derivation(d, registries)
    assert obj is not None
    assert d.status == DerivationStatus.CANONICAL
    assert obj.status == Status.VERIFIED  # two independent obligations = two evidence tiers


def test_su3_unimodularity_step_reaches_canonical():
    engine = _make_engine()
    algebra = engine.add_object(MathObject(
        id="u3-algebra", math_type=MathType.LIE_ALGEBRA, epistemic_kind=EpistemicKind.DEFINITION,
        carrier="u(3)",
    ))

    d = engine.derive("D-SU3-UNIMODULARITY", MathType.LIE_ALGEBRA, {"algebra": algebra},
                       theorem_id="THM-SU3-UNIMODULARITY-FROM-U3")

    assert d.status == DerivationStatus.VERIFIED
    traceless = next(o for o in d.proof_obligations if o.obligation_id == "gell-mann-generators-traceless")
    forced = next(o for o in d.proof_obligations if o.obligation_id == "trace-condition-forces-a0-to-zero")
    assert traceless.result == ObligationResult.SATISFIED
    assert forced.result == ObligationResult.SATISFIED

    result_obj = engine.objects[d.steps[0].output_id]
    assert result_obj.carrier.a0_forced_to_zero is True

    registries = MDCLRegistries()
    obj = register_canonical_derivation(d, registries)
    assert obj is not None
    assert d.status == DerivationStatus.CANONICAL
    assert obj.status == Status.VERIFIED


def test_wrong_gauge_group_is_inapplicable_not_forced():
    """The theorem must not silently apply itself to a gauge group it was
    never checked against -- SU(2), say, has a different C2(adjoint)."""
    engine = _make_engine()
    gauge_group = engine.add_object(MathObject(
        id="gauge-group-SU2", math_type=MathType.LIE_GROUP, epistemic_kind=EpistemicKind.DEFINITION,
        carrier="SU(2)",
    ))
    n_f = engine.add_object(MathObject(
        id="n_f-six-flavors-2", math_type=MathType.SCALAR, epistemic_kind=EpistemicKind.DEFINITION,
        carrier=6,
    ))
    d = engine.derive("D-QCD-BETA-WRONG-GROUP", MathType.EQUATION,
                       {"gauge_group": gauge_group, "n_f": n_f},
                       theorem_id="THM-QCD-ONE-LOOP-BETA-FUNCTION")
    assert d.status == DerivationStatus.DERIVATION_FAILED
