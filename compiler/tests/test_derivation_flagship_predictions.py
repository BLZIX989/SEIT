"""Phase 14 (minimal slice): the m_aP flagship prediction, run through the
derivation engine rather than re-verified by hand. The point of this test
is the NEGATIVE result: the arithmetic checks out, but the Derivation must
stay CONDITIONAL (never VERIFIED/CANONICAL) because N_sub's own upstream
derivation (N_sub <- CMB spectral index n_s) is an acknowledged,
unresolved gap -- exactly the finding reports/master_toe/
MASTER_TOE_PREDICTIONS.md already reached by hand. This is the task's own
"do not force the theory to be true" requirement in action.
"""
from __future__ import annotations

from compiler.core.status import Status
from compiler.derivation.certification import register_canonical_derivation, to_canonical_status
from compiler.derivation.derivation import DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.flagship_theorems import register_flagship_theorems
from compiler.derivation.obligations import ObligationResult
from compiler.derivation.theorems import TheoremRegistry
from compiler.derivation.types import EpistemicKind, MathObject, MathType
from compiler.ir.registry import MDCLRegistries


def test_qcd_axion_mass_arithmetic_matches_but_stays_conditional():
    registry = register_flagship_theorems(TheoremRegistry())
    engine = DerivationEngine(registry)
    n_sub_obj = engine.add_object(MathObject(
        id="N_sub", math_type=MathType.SCALAR, epistemic_kind=EpistemicKind.ASSUMPTION,
        carrier=4.7619,
    ))

    d = engine.derive("D-M-AP", MathType.OBSERVABLE, {"n_sub": n_sub_obj},
                       theorem_id="THM-QCD-AXION-MASS-RELATION")

    arithmetic = next(o for o in d.proof_obligations if o.obligation_id == "qcd-axion-mass-arithmetic")
    free_param = next(o for o in d.proof_obligations
                       if o.obligation_id == "free-parameter:n_sub-not-independently-derived")
    assert arithmetic.result == ObligationResult.SATISFIED
    assert free_param.result == ObligationResult.NOT_TESTED

    # The core requirement: an unresolved upstream link must cap the status
    # at CONDITIONAL, never let a downstream-correct arithmetic check alone
    # promote it to VERIFIED/CANONICAL.
    assert d.status == DerivationStatus.CONDITIONAL

    m_ap_obj = engine.objects[d.steps[0].output_id]
    result = m_ap_obj.carrier
    assert abs(result.m_a_ev - 6.885e-13) / 6.885e-13 < 1e-3


def test_conditional_flagship_prediction_registers_as_conditional_not_canonical():
    registry = register_flagship_theorems(TheoremRegistry())
    engine = DerivationEngine(registry)
    n_sub_obj = engine.add_object(MathObject(
        id="N_sub2", math_type=MathType.SCALAR, epistemic_kind=EpistemicKind.ASSUMPTION,
        carrier=4.7619,
    ))
    d = engine.derive("D-M-AP-2", MathType.OBSERVABLE, {"n_sub": n_sub_obj},
                       theorem_id="THM-QCD-AXION-MASS-RELATION")
    assert d.status == DerivationStatus.CONDITIONAL

    registries = MDCLRegistries()
    obj = register_canonical_derivation(d, registries)
    # CONDITIONAL is not VERIFIED/CANONICAL -- register_canonical_derivation
    # must refuse it, exactly like any other non-canonical Derivation.
    assert obj is None
    assert d.status == DerivationStatus.CONDITIONAL  # untouched, not force-promoted
    assert to_canonical_status(d) == Status.CONDITIONAL
