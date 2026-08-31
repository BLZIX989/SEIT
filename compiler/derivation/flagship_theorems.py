"""Flagship prediction theorem(s) -- Phase 14, minimal slice, per
DERIVATION_ENGINE_IMPLEMENTATION_PLAN.md's own explicit deferral note.

Only m_aP (the persistence axion mass) is attempted here, and only
honestly: the QCD axion mass relation itself (m_a = Lambda_QCD^2/f_a) is
standard, established physics and is wired as a real `implemented=True`
theorem (compiler/backends/qcd_axion_mass.py). Its input N_sub, however, is
bound as an EXPLICIT, UNRESOLVED ASSUMPTION -- reports/master_toe/
MASTER_TOE_PREDICTIONS.md's own audit ("What was NOT verified this
campaign") found that the connecting formula deriving N_sub from the
measured CMB spectral index n_s was never located in the source corpus, so
N_sub cannot honestly be typed as a DERIVED_RESULT here.

The resulting Derivation is therefore, correctly, CONDITIONAL -- never
VERIFIED or CANONICAL. This is the intended behavior, not a bug: the task's
own absolute requirement ("do not force the theory to be true") means this
engine must not silently promote a prediction whose upstream derivation
chain has an acknowledged, unresolved link, no matter how well the
downstream arithmetic itself checks out.

f_GW (166.48 Hz) and R_c (120-150 pc) are explicitly NOT attempted in this
pass: unlike N_sub, their upstream derivation chains have not yet been
localized and audited anywhere in this repository the way N_sub's chain was
audited in MASTER_TOE_PREDICTIONS.md. Wiring them now would mean either
inventing the missing upstream mathematics ad hoc (exactly what the task
warns against) or hardcoding their target values as unexamined assumptions,
which would make the resulting Derivation look more complete than the
audit trail actually supports. Both are next-session backlog items,
contingent on first doing for f_GW and R_c what MASTER_TOE_PREDICTIONS.md
already did for m_aP: locating and checking their connecting formulas.
"""
from __future__ import annotations

from compiler.backends.qcd_axion_mass import qcd_axion_mass
from compiler.derivation.obligations import ProofObligation
from compiler.derivation.theorems import Theorem, TheoremRegistry
from compiler.derivation.types import EpistemicKind, MathObject, MathType

# The independently-checked target value from reports/master_toe/
# MASTER_TOE_PREDICTIONS.md's own hand computation (SEIT v2.pdf Sec VI),
# used here only as a cross-check tolerance, not as a fitted target.
_EXPECTED_M_AP_EV = 6.885e-13


def _axion_mass_applicable(bound: dict) -> bool:
    n_sub_obj = bound.get("n_sub")
    return n_sub_obj is not None and n_sub_obj.epistemic_kind == EpistemicKind.ASSUMPTION


def _axion_mass_transform(bound: dict):
    n_sub_obj = bound["n_sub"]
    n_sub = float(n_sub_obj.carrier)
    result = qcd_axion_mass(n_sub)

    arithmetic_ok = abs(result.m_a_ev - _EXPECTED_M_AP_EV) / _EXPECTED_M_AP_EV < 1e-3
    arithmetic_check = ProofObligation(
        "qcd-axion-mass-arithmetic",
        "m_aP = Lambda_QCD^2 / (N_sub * M_Planck) evaluates to the independently-checked "
        "reports/master_toe/MASTER_TOE_PREDICTIONS.md value (6.885e-13 eV) to 0.1%",
        check=lambda: arithmetic_ok,
    ).discharge()

    # N_sub's OWN provenance (N_sub <- CMB spectral index n_s) is an
    # acknowledged, unresolved gap -- honestly recorded as NOT_TESTED
    # (check=None), never silently skipped or upgraded to SATISFIED.
    free_parameter = ProofObligation(
        "free-parameter:n_sub-not-independently-derived",
        "N_sub is stated (SEIT v2.pdf Sec VI) to follow from the measured CMB spectral index "
        "n_s=0.965, but the connecting formula was not located/verified anywhere in this "
        "repository's corpus (see MASTER_TOE_PREDICTIONS.md's own 'What was NOT verified' "
        "section) -- N_sub is bound here as an unresolved ASSUMPTION, not a DERIVED_RESULT",
        check=None,
    ).discharge()

    output = MathObject(
        id="m_aP", math_type=MathType.OBSERVABLE, epistemic_kind=EpistemicKind.DERIVED_RESULT,
        carrier=result,
    )
    return output, [arithmetic_check, free_parameter]


THM_QCD_AXION_MASS = Theorem(
    theorem_id="THM-QCD-AXION-MASS-RELATION",
    statement="m_a ~ Lambda_QCD^2 / f_a for a QCD axion with decay constant f_a (standard axion "
              "mass relation from the QCD chiral Lagrangian / instanton potential).",
    hypotheses=["f_a >> Lambda_QCD (the usual axion window)",
                "f_a = N_sub * M_Planck (this repository's own substitution for the usual "
                "Peccei-Quinn scale, per SEIT v2.pdf Sec VI -- NOT a standard PQ-scale identity)"],
    conclusion="m_aP = Lambda_QCD^2 / (N_sub * M_Planck)",
    conclusion_type=MathType.OBSERVABLE,
    domain="particle physics / axion cosmology",
    provenance="standard QCD axion mass relation; N_sub substitution and numeric evaluation "
               "independently re-derived from reports/master_toe/MASTER_TOE_PREDICTIONS.md "
               "(itself sourced from this repository's own SEIT v2.pdf Sec VI corpus entry)",
    implemented=True,
    applicability_check=_axion_mass_applicable,
    transformation=_axion_mass_transform,
)


def register_flagship_theorems(registry: TheoremRegistry) -> TheoremRegistry:
    registry.register(THM_QCD_AXION_MASS)
    return registry
