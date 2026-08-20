"""Spectral action branch as executable `.seit` primitives (Phase 12):
implements Tr f(D/Lambda) and finite heat-kernel-style moments, gated
by an explicit spectral-triple prerequisites check, tracking which
assumptions produce each reported value.

THE GATE, TAKEN LITERALLY: the brief says implement these "only after
spectral-triple prerequisites satisfied." No object anywhere in this
corpus -- including D_B from Phase 6 (seit_lang/incidence_clifford.py)
-- has ever been shown to satisfy the full set of Connes spectral-triple
axioms (a real structure J with the correct KO-dimension signs, and the
first-order condition [[D,a],JbJ^-1]=0 for algebra elements a,b; see
scientific_corpus/derivation/clifford_derivation.py's own
clifford_rank_forcing_check() and dirac_candidates.py's own
"what_this_DOES_NOT_establish"). So this module never claims a
computed value IS a physically-interpretable Seeley-DeWitt coefficient
or spectral action for this project's own construction.

What it DOES do: spectral_triple_prerequisites_report() checks exactly
what CAN be checked structurally for a candidate D (self-adjointness --
a hard requirement for any Dirac operator -- and, if a grading gamma is
supplied, {D, gamma} = 0, reusing Phase 6's own already-verified
pattern), and reports the rest (real structure J, first-order
condition) as explicitly NOT CHECKED rather than assumed satisfied.
spectral_action_trace() and finite_spectral_moment() then compute real,
finite, numerically well-defined quantities REGARDLESS of
spectral-triple status -- exactly as H2B (dirac_candidates.py) already
computed real numbers (sparsity, decay profile) about D_B without
claiming spectral-triple verification. finite_moment_report() bundles
these with an explicit assumptions_used list PER coefficient (the
brief's own "track which assumptions produce each coefficient"), and an
explicit physical_interpretation field that says NONE when prerequisites
are not met.

FINITE MOMENTS ARE NOT SEELEY-DEWITT COEFFICIENTS: Tr(D^k) computed
here is an EXACT finite-dimensional trace of a specific matrix at a
specific finite size -- it is NOT the continuum small-beta asymptotic
expansion Tr e^{-beta D^2} ~ sum_k a_k(x) beta^k, whose coefficients a_k
encode curvature invariants of an actual Riemannian manifold this
project has not constructed (the identical caution
seit_lang/persistence_kernel.py already states for K_Pi(beta), restated
here rather than silently reused across a very different-looking
function name).
"""
from __future__ import annotations

import numpy as np

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature

_CUTOFF_FUNCTIONS = {
    "step": lambda x: (np.abs(x) <= 1.0).astype(float),
    "gaussian": lambda x: np.exp(-x ** 2),
}


def spectral_triple_prerequisites_report(D: np.ndarray, gamma: np.ndarray | None = None) -> dict:
    """Checks exactly what can be structurally verified toward the
    Connes spectral-triple axioms for a candidate Dirac operator D.
    Never reports all_prerequisites_satisfied=True from this corpus,
    since the real structure J and first-order condition have no
    construction anywhere in it to check."""
    is_self_adjoint = bool(np.allclose(D, D.conj().T, atol=1e-9))
    anticommutes_with_grading = None
    if gamma is not None:
        anticommutator = gamma @ D + D @ gamma
        anticommutes_with_grading = bool(np.allclose(anticommutator, 0.0, atol=1e-9))
    return {
        "D_is_self_adjoint": is_self_adjoint,
        "grading_supplied": gamma is not None,
        "D_anticommutes_with_grading": anticommutes_with_grading,
        "real_structure_J_checked": False,
        "first_order_condition_checked": False,
        "all_prerequisites_satisfied": False,
        "note": (
            "real_structure_J_checked and first_order_condition_checked are "
            "structurally False for every object in this corpus, not merely "
            "unset -- no real structure J or algebra representation compatible with "
            "the first-order condition has been constructed anywhere in this repository "
            "(see clifford_derivation.py, dirac_candidates.py). "
            "all_prerequisites_satisfied can never be True until that changes."),
    }


def spectral_action_trace(D: np.ndarray, Lambda: float, cutoff: str = "step") -> float:
    """Tr f(D/Lambda) -- a real, finite, numerically well-defined trace,
    computed regardless of spectral-triple status (see module
    docstring). `cutoff` selects f: "step" is the characteristic
    function of [-1,1] (the simplest, standard choice, counting
    eigenvalues within the cutoff scale); "gaussian" is exp(-x^2)."""
    if cutoff not in _CUTOFF_FUNCTIONS:
        raise ValueError(f"unknown cutoff {cutoff!r}, expected one of {sorted(_CUTOFF_FUNCTIONS)}")
    is_hermitian = bool(np.allclose(D, D.conj().T, atol=1e-9))
    eigvals = np.linalg.eigvalsh(D) if is_hermitian else np.linalg.eigvals(D)
    x = eigvals / Lambda
    return float(np.sum(_CUTOFF_FUNCTIONS[cutoff](x)))


def finite_spectral_moment(D: np.ndarray, k: float) -> float:
    """Tr(D^k) -- an EXACT finite-dimensional trace moment, NOT a
    continuum Seeley-DeWitt coefficient a_k (see module docstring)."""
    k_i = int(k)
    Dk = np.linalg.matrix_power(D, k_i)
    return float(np.real(np.trace(Dk)))


def finite_moment_report(D: np.ndarray, max_k: float = 4, gamma: np.ndarray | None = None) -> dict:
    """Bundles spectral_triple_prerequisites_report() with a set of even
    finite moments (0, 2, 4, ..., max_k), each carrying its own
    assumptions_used list -- the brief's "track which assumptions
    produce each coefficient," made concrete per coefficient rather
    than as one blanket disclaimer."""
    max_k_i = int(max_k)
    prereq = spectral_triple_prerequisites_report(D, gamma)
    n = D.shape[0]
    self_adjoint_note = ("D is self-adjoint (checked)" if prereq["D_is_self_adjoint"]
                          else "D is NOT confirmed self-adjoint -- moment may not be real-valued")
    moments = {}
    for k in range(0, max_k_i + 1, 2):
        moments[f"moment_{k}"] = {
            "value": finite_spectral_moment(D, k),
            "assumptions_used": [
                self_adjoint_note,
                f"finite N={n}, no continuum limit taken",
                "exact finite-dimensional trace moment, not an asymptotic Seeley-DeWitt "
                "small-beta expansion coefficient",
            ],
        }
    return {
        "spectral_triple_prerequisites": prereq,
        "moments": moments,
        "physical_interpretation": (
            None if not prereq["all_prerequisites_satisfied"] else "unreachable in this corpus"),
        "physical_interpretation_note": (
            "NONE -- these are finite linear-algebra trace moments of the specific matrix D "
            "supplied, not physically-interpretable Seeley-DeWitt heat-kernel coefficients, "
            "which require an actual continuum Riemannian manifold structure this project has "
            "not constructed (the same caution seit_lang.persistence_kernel states for "
            "K_Pi(beta))."),
    }


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("spectral_triple_prerequisites_report", ["Operator"], "Dataset",
                      lambda D: spectral_triple_prerequisites_report(D),
                      "seit_lang.spectral_action.spectral_triple_prerequisites_report"),
    PrimitiveBinding("spectral_action_trace", ["Operator", "Scalar"], "Scalar",
                      lambda D, Lambda: spectral_action_trace(D, Lambda),
                      "seit_lang.spectral_action.spectral_action_trace (Tr f(D/Lambda), step cutoff)"),
    PrimitiveBinding("finite_spectral_moment", ["Operator", "Scalar"], "Scalar",
                      finite_spectral_moment,
                      "seit_lang.spectral_action.finite_spectral_moment (Tr(D^k), NOT a "
                      "Seeley-DeWitt coefficient)"),
    PrimitiveBinding("finite_moment_report", ["Operator", "Scalar"], "Dataset",
                      lambda D, max_k: finite_moment_report(D, max_k),
                      "seit_lang.spectral_action.finite_moment_report"),
]

SPECTRAL_ACTION_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
SPECTRAL_ACTION_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
