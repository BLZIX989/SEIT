"""Persistence/heat-kernel branch as executable `.seit` primitives
(Phase 7): exposes P_lambda_c, L_Pi, H_Pi(beta), K_Pi(beta), and
d_{Pi,beta} as compiler operators, building on -- reusing directly, not
reimplementing -- scientific_corpus/derivation/persistence.py, which
itself already reuses the real compiler spectral backend
(compiler/backends/graph_laplacian.py, spectral.py, heat_flow.py).

persistence.py's own functions operate on raw (vals, vecs) arrays; this
module's primitives operate on the real compiler.backends.spectral.
SpectralData object (`.seit` type "Spectrum") that Phase 5's spectrum()
primitive already produces, so a `.seit` program can chain
spectrum(L) -> P_lambda_c(spec, lambda_c) -> ... without a type
mismatch between phases.

H_Pi(beta) is exposed as the actual RESTRICTED HEAT OPERATOR
P e^{-beta L} P (an "Operator"-typed matrix, built from the REAL
compiler.backends.heat_flow.heat_operator -- not a new exponentiation
formula), and K_Pi(beta) as its trace (a "Scalar") -- kept as two
separate primitives because the brief lists them as two separate
objects, and because persistence.py's own K_Pi computation uses an
eigenvalue-sum shortcut (valid only because e^{-beta L_Pi} is diagonal
in the persistent eigenbasis) that this module's tests cross-check
against the actual matrix trace, rather than trusting the shortcut on
its own say-so.

CAUTION (the brief's own explicit requirement): the finite discrete
heat trace K_Pi(beta) = Tr(e^{-beta L_Pi}) computed here is an EXACT
finite sum over a finite eigenvalue spectrum of a finite-dimensional
operator on a discrete graph, evaluated at fixed finite N and beta. It
is NOT the continuum Seeley-DeWitt small-beta ASYMPTOTIC expansion
Tr e^{-beta D^2} ~ (4*pi*beta)^{-d/2} * sum_k a_k(x) beta^k (a series
in a continuum Riemannian manifold's dimension d, whose coefficients
a_k encode curvature invariants). Computing that continuum expansion
would require an actual continuum limit / manifold structure this
discrete graph construction has not been shown to possess -- see
DERIVATION_FRONTIER.md's own g_munu-reconstruction gap and CONV-001's
real DESI N-scaling assessment (both already on record as unresolved).
No heat-kernel coefficients a_0, a_2, a_4, ... are extracted here.
Phase 12 (spectral action) is where any such extraction would need to
happen, and only after its own stated prerequisites are met -- not
here, and not by silently reinterpreting K_Pi(beta) as one.
"""
from __future__ import annotations

import numpy as np

from compiler.backends.heat_flow import heat_operator
from compiler.backends.spectral import SpectralData
from scientific_corpus.derivation import persistence

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def persistence_projector(spec: SpectralData, lambda_c: float) -> np.ndarray:
    """P_lambda_c = sum_{lambda_n < lambda_c} |psi_n><psi_n| -- reuses
    persistence.py's real persistence_projection() (which itself
    verifies idempotence and self-adjointness, not just asserts them)."""
    P, _idx, _idemp, _self_adj = persistence.persistence_projection(
        spec.eigenvalues, spec.eigenvectors, lambda_c)
    return P


def restricted_laplacian(L: np.ndarray, P: np.ndarray) -> np.ndarray:
    """L_Pi = P L P."""
    return P @ L @ P


def persistent_heat_operator(L: np.ndarray, P: np.ndarray, beta: float) -> np.ndarray:
    """H_Pi(beta) = P e^{-beta L} P -- built from the REAL
    compiler.backends.heat_flow.heat_operator, not a new exponentiation
    formula."""
    return P @ heat_operator(L, beta) @ P


def persistent_heat_trace(H_pi: np.ndarray) -> float:
    """K_Pi(beta) = Tr H_Pi(beta)."""
    return float(np.trace(H_pi))


def _persistent_indices(spec: SpectralData, lambda_c: float) -> np.ndarray:
    _P, idx, _idemp, _self_adj = persistence.persistence_projection(
        spec.eigenvalues, spec.eigenvectors, lambda_c)
    return idx


def persistent_distance_pair(spec: SpectralData, lambda_c: float, beta: float,
                              i: float, j: float) -> float:
    """d_{Pi,beta}(i,j) -- reuses persistence.py's real
    persistent_distance() directly."""
    idx = _persistent_indices(spec, lambda_c)
    return persistence.persistent_distance(spec.eigenvalues, spec.eigenvectors, idx, beta, int(i), int(j))


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("persistence_projector", ["Spectrum", "Scalar"], "Projector",
                      persistence_projector,
                      "seit_lang.persistence_kernel.persistence_projector (calls "
                      "scientific_corpus.derivation.persistence.persistence_projection)"),
    PrimitiveBinding("restricted_laplacian", ["Laplacian", "Projector"], "Laplacian",
                      restricted_laplacian, "seit_lang.persistence_kernel.restricted_laplacian (L_Pi = P L P)"),
    PrimitiveBinding("persistent_heat_operator", ["Laplacian", "Projector", "Scalar"], "Operator",
                      persistent_heat_operator,
                      "seit_lang.persistence_kernel.persistent_heat_operator (H_Pi(beta) = P e^{-beta L} P, "
                      "via compiler.backends.heat_flow.heat_operator)"),
    PrimitiveBinding("persistent_heat_trace", ["Operator"], "Scalar",
                      persistent_heat_trace, "seit_lang.persistence_kernel.persistent_heat_trace (K_Pi(beta) = Tr H_Pi(beta))"),
    PrimitiveBinding("persistent_distance_pair", ["Spectrum", "Scalar", "Scalar", "Scalar", "Scalar"], "Scalar",
                      persistent_distance_pair,
                      "seit_lang.persistence_kernel.persistent_distance_pair (calls "
                      "scientific_corpus.derivation.persistence.persistent_distance)"),
]

PERSISTENCE_KERNEL_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
PERSISTENCE_KERNEL_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
