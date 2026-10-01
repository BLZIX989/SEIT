"""Established-physics-only theorems (the user's own requested test: "derive
something using established physics only, just to see what happens"). Both
theorems here reproduce, via genuine executed sympy computation rather than
restated prose, the two derivations SRO Established Core's own audit
flagged as real, checked, non-hand-wavy steps: the one-loop QCD beta
function / asymptotic freedom (section 6) and the U(3)->SU(3)_c
unimodularity step (section 4). Neither is SEIT/UOC-specific -- both are
standard, textbook, peer-reviewed physics, independent of the graph/
spectral-triple machinery elsewhere in this package.
"""
from __future__ import annotations

from compiler.backends.qcd_beta_function import one_loop_qcd_beta_function
from compiler.backends.su3_unimodularity import unimodularity_step
from compiler.derivation.obligations import ObligationResult, ProofObligation
from compiler.derivation.theorems import Theorem, TheoremRegistry
from compiler.derivation.types import EpistemicKind, MathObject, MathType


def _beta_function_applicable(bound: dict) -> bool:
    gauge_group = bound.get("gauge_group")
    n_f = bound.get("n_f")
    return gauge_group is not None and gauge_group.carrier == "SU(3)" and n_f is not None


def _beta_function_transform(bound: dict):
    n_f = int(bound["n_f"].carrier)
    result = one_loop_qcd_beta_function(n_colors=3, n_f=n_f)

    coefficient_check = ProofObligation(
        "beta-function-coefficient-exact",
        "b_3 = -(11/3)*C2(adjoint) + (4/3)*n_f*T(fundamental) evaluates EXACTLY "
        "(sympy Rational arithmetic, no floating point) to -7 for SU(3), n_f=6",
        check=lambda: result.b3 == -7,
    ).discharge()

    sign_check = ProofObligation(
        "asymptotic-freedom-sign-for-all-positive-coupling",
        "beta_{g_s}(g_s) = b_3/(16 pi^2) g_s^3 has b_3 < 0 exactly (symbolic sign, not a "
        "sampled point), and since g_s^3>0 and 16 pi^2>0 for every real g_s>0, "
        "beta_{g_s}(g_s) < 0 for ALL g_s>0 -- the defining sign of asymptotic freedom",
        check=lambda: result.asymptotically_free,
    ).discharge()

    output = MathObject(
        id="beta_gs_one_loop_SU3", math_type=MathType.EQUATION,
        epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=result,
    )
    return output, [coefficient_check, sign_check]


THM_QCD_BETA_FUNCTION = Theorem(
    theorem_id="THM-QCD-ONE-LOOP-BETA-FUNCTION",
    statement="For SU(N) Yang-Mills with n_f fundamental Dirac flavors, the one-loop beta "
              "function is beta_{g_s}(g_s) = (b_3/16pi^2) g_s^3 with "
              "b_3 = -(11/3)C2(G) + (4/3)n_f T(R). For SU(3) with n_f=6, b_3=-7<0, giving "
              "asymptotic freedom: the coupling decreases at short distance / high energy.",
    hypotheses=["gauge group is SU(N)", "n_f fundamental Dirac fermion flavors",
                "one-loop (leading order) renormalization group approximation"],
    conclusion="b_3 = -7 for SU(3), n_f=6; beta_{g_s}(g_s) < 0 for all g_s > 0",
    conclusion_type=MathType.EQUATION,
    domain="quantum chromodynamics / renormalization group",
    provenance="Gross & Wilczek, Phys. Rev. Lett. 30 (1973); Politzer, Phys. Rev. Lett. 30 "
               "(1973); 2004 Nobel Prize in Physics. Standard, established, peer-reviewed "
               "QCD -- independent of any SEIT/UOC-specific construction.",
    implemented=True,
    applicability_check=_beta_function_applicable,
    transformation=_beta_function_transform,
)


def _unimodularity_applicable(bound: dict) -> bool:
    algebra = bound.get("algebra")
    return algebra is not None and algebra.carrier == "u(3)"


def _unimodularity_transform(bound: dict):
    result = unimodularity_step()

    traceless_generators_check = ProofObligation(
        "gell-mann-generators-traceless",
        "each of the 8 Gell-Mann matrices lambda^a has Tr(lambda^a)=0 (exact sympy check)",
        check=lambda: result.trace_of_traceless_part_is_zero,
    ).discharge()

    unimodularity_check = ProofObligation(
        "trace-condition-forces-a0-to-zero",
        "Tr(A_mu) = 3*a0 for A_mu = a0*I_3 + sum_a a^a*lambda^a (symbolic trace, exact); "
        "solving Tr(A_mu)=0 for a0 yields EXACTLY a0=0, stripping U(3) to the traceless "
        "SU(3) subalgebra -- solved algebraically, not merely asserted",
        check=lambda: result.a0_forced_to_zero,
    ).discharge()

    output = MathObject(
        id="su3_from_u3_unimodularity", math_type=MathType.LIE_ALGEBRA,
        epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=result,
    )
    return output, [traceless_generators_check, unimodularity_check]


THM_SU3_UNIMODULARITY = Theorem(
    theorem_id="THM-SU3-UNIMODULARITY-FROM-U3",
    statement="A trace-free (unimodularity) condition Tr(A_mu)=0 on a u(3)-valued gauge "
              "connection A_mu = a0*I_3 + sum_a a^a*lambda^a forces a0=0, restricting the "
              "connection to the traceless su(3) subalgebra -- the algebraic step isolating "
              "SU(3)_c from U(3) in the noncommutative-geometry Standard Model construction.",
    hypotheses=["A_mu takes values in u(3) = span{I_3, lambda^1, ..., lambda^8}",
                "unimodularity: Tr(A_mu) = 0 is imposed"],
    conclusion="a0 = 0, i.e. A_mu in su(3) = span{lambda^1, ..., lambda^8}",
    conclusion_type=MathType.LIE_ALGEBRA,
    domain="Lie algebra / noncommutative-geometry Standard Model construction",
    provenance="Standard step in the Chamseddine-Connes NCG Standard Model construction "
               "(Chamseddine & Connes, hep-th/9606001 and follow-up literature); pure linear "
               "algebra (trace linearity), independent of any SEIT/UOC-specific claim.",
    implemented=True,
    applicability_check=_unimodularity_applicable,
    transformation=_unimodularity_transform,
)


def register_established_physics_theorems(registry: TheoremRegistry) -> TheoremRegistry:
    registry.register(THM_QCD_BETA_FUNCTION)
    registry.register(THM_SU3_UNIMODULARITY)
    return registry
