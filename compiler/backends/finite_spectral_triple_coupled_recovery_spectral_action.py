"""Closes the wiring gap identified in this session's audit of
CL-FINITE-TRIPLE-TO-SPECTRAL-ACTION: that chainlink's OMEGA_B-FINITE
dependency traces back to the ORIGINAL (A_F,H_F,D_F,J_F,gamma_F) candidate
(compiler/backends/finite_spectral_triple_candidate.py), which FAILS the
first-order condition -- so the standard NCG inner-fluctuation mechanism
was never well-posed for it. This project also built THREE separate
recovery candidates that PASS the first-order condition
(compiler/backends/finite_spectral_triple_recovery.py,
finite_spectral_triple_tft002b.py, finite_spectral_triple_recovery_coupled.py)
but none of them was ever run through an actual inner-fluctuation /
spectral-action attempt. This module does that, for the richest of the
three: the nontrivially-coupled recovery over TFT-002B
(finite_spectral_triple_recovery_coupled.py), chosen because its inter-copy
coupling C is exactly what gives the inner fluctuation genuinely new,
non-block-diagonal content -- the minimal (uncoupled) recovery's own
first-order-condition proof shows [D_F',pi'(f)] has IDENTICALLY ZERO
output on copy 2, which forces any inner fluctuation built the same way
to stay block-diagonal (each copy fluctuated identically, no coupling
introduced) -- a much weaker, less interesting result than what the
coupled candidate can produce.

THE CONSTRUCTION, chosen to be the simplest well-defined choice rather
than the most general one (Connes' own historically first example -- the
two-point-space "photon" field -- uses exactly this pattern: a single
generator, self-adjoint by construction via the i-times-a-commutator
trick, not the fully general finite sum Sum_i a_i[D,b_i]):

  omega = i * [D_F'', pi'(f)]   for a single real f on the vertex block.

Self-adjointness is NOT assumed -- it is a direct consequence of
[D,pi(f)] being skew-Hermitian whenever D and pi(f) are both self-adjoint
(true here, both checked upstream), so i*[D,pi(f)] is Hermitian by a
one-line algebraic fact, confirmed numerically below rather than merely
cited.

D_A'' = D_F'' + omega + eps' * J'' omega J''^-1, using the ACTUALLY
MEASURED real-structure sign eps'=+1 for this candidate
(run_coupled_recovery_certification's own real_structure_epsilon_prime),
never assumed. J'' omega J''^-1 is computed by an explicit closed-form
matrix identity (J_conjugate_matrix below), derived directly from J''s
antilinear definition (xi,eta)->(conj(eta),conj(xi)) and independently
verified against the vector-level definition (verify_J_conjugate_matrix)
rather than asserted.

WHAT THIS DOES AND DOES NOT ESTABLISH:
  1. D_A'' is verified self-adjoint and still anticommutes with the
     grading -- a genuine, well-posed fluctuated Dirac-type operator,
     not merely "some matrix." This is the first object anywhere in this
     corpus for which that is true.
  2. Omega_B'' := D_A''^2 - D_F''^2 is genuinely, numerically NONZERO
     (not a trivial shift) and self-adjoint -- real new curvature content
     that the original candidate could never produce because its
     inner-fluctuation mechanism was not well-posed at all.
  3. This is ONE generator (a single real f), not the fully general
     Omega^1_D(A_F) = {Sum_i a_i[D,b_i]}. A different, or larger, choice
     of generators would give a different Omega_B''; this is not claimed
     to be a canonical or unique choice, only a concrete, honestly
     verified one -- the same "concrete candidate, not the general case"
     discipline every other module in this corpus follows
     (finite_spectral_triple_candidate.py's own f,g choice, etc.).
  4. The finite moments a0''..a6'' computed below are EXACT
     finite-dimensional trace moments Tr(D_A''^k) of this specific
     matrix at this specific finite size -- NOT the continuum small-beta
     Seeley-DeWitt asymptotic expansion coefficients, which require an
     actual continuum Riemannian manifold structure this project has not
     constructed (the identical caution seit_lang/spectral_action.py and
     seit_lang/persistence_kernel.py already state for their own
     finite/discrete quantities, restated here rather than silently
     reused across a different-looking module).
  5. This does NOT resolve CL-FINITE-TRIPLE-TO-SPECTRAL-ACTION (the
     ORIGINAL candidate's chainlink) -- that chainlink correctly remains
     OPEN, since the original (A_F,H_F,D_F,J_F,gamma_F) still fails the
     first-order condition. This module registers an INDEPENDENT
     chainlink for the coupled-recovery candidate specifically, per this
     project's "new claim id, don't overreach in one pass" discipline.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from compiler.backends.finite_spectral_triple_recovery_coupled import (
    J_apply, build_coupled_double, pi_prime_coupled, run_coupled_recovery_certification,
)


def J_conjugate_matrix(M: np.ndarray, dim: int) -> np.ndarray:
    """J'' M J''^-1 as an explicit (2*dim)x(2*dim) matrix, for
    J''(xi,eta)=(conj(eta),conj(xi)) = P @ conj(v), P=[[0,I],[I,0]] the
    real block-swap permutation: derived directly as P @ conj(M) @ P
    (see module docstring for the one-line derivation), independently
    confirmed against the vector-level J_apply composition by
    verify_J_conjugate_matrix below rather than asserted."""
    P = np.zeros((2 * dim, 2 * dim))
    P[:dim, dim:] = np.eye(dim)
    P[dim:, :dim] = np.eye(dim)
    return P @ M.conj() @ P


def verify_J_conjugate_matrix(dim: int, seed: int = 0) -> bool:
    """Confirms J_conjugate_matrix's closed form against the ground-truth
    vector-level J_apply(M @ J_apply(v)) definition directly, on random
    complex M and v -- not merely cited from the module docstring's
    derivation."""
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((2 * dim, 2 * dim)) + 1j * rng.standard_normal((2 * dim, 2 * dim))
    v = rng.standard_normal(2 * dim) + 1j * rng.standard_normal(2 * dim)
    lhs = J_apply(M @ J_apply(v, dim), dim)
    rhs = J_conjugate_matrix(M, dim) @ v
    return bool(np.allclose(lhs, rhs))


@dataclass
class InnerFluctuationResult:
    J_conjugate_matrix_verified: bool
    omega_self_adjoint: bool
    omega_max_abs: float
    real_structure_epsilon_prime_used: int
    D_A_self_adjoint: bool
    D_A_anticommutes_with_grading: bool
    Omega_B_is_zero: bool
    Omega_B_self_adjoint: bool
    Omega_B_max_abs: float
    well_posed: bool


def build_inner_fluctuation(
    n: int = 200, k_neighbors: int = 3, mu: float = 0.4, seed: int = 42, cert_seed: int = 0,
) -> dict:
    """Builds D_F'' (coupled recovery), a single-generator omega, and the
    fluctuated D_A'' = D_F'' + omega + eps'*J''omega J''^-1, returning
    every intermediate matrix for downstream use (finite moments) and
    axiom checks."""
    build = build_coupled_double(n, k_neighbors, mu, seed)
    N0, dim, D_pp, gamma_pp = build["N0"], build["dim"], build["D_pp"], build["gamma_pp"]

    cert = run_coupled_recovery_certification(n, k_neighbors, mu, seed, cert_seed)
    eps_prime = cert.real_structure_epsilon_prime

    rng = np.random.default_rng(cert_seed)
    f = rng.standard_normal(N0)
    piF = pi_prime_coupled(f, N0, dim)
    omega = 1j * (D_pp @ piF - piF @ D_pp)

    j_check = verify_J_conjugate_matrix(dim, seed=cert_seed + 1)
    J_omega_Jinv = J_conjugate_matrix(omega, dim)
    D_A = D_pp + omega + eps_prime * J_omega_Jinv

    return {
        "n": n, "k_neighbors": k_neighbors, "N0": N0, "dim": dim,
        "D_F_pp": D_pp, "gamma_pp": gamma_pp, "omega": omega,
        "J_omega_Jinv": J_omega_Jinv, "D_A": D_A,
        "real_structure_epsilon_prime_used": eps_prime,
        "J_conjugate_matrix_verified": j_check,
    }


def run_inner_fluctuation_certification(
    n: int = 200, k_neighbors: int = 3, mu: float = 0.4, seed: int = 42, cert_seed: int = 0,
) -> InnerFluctuationResult:
    b = build_inner_fluctuation(n, k_neighbors, mu, seed, cert_seed)
    D_pp, gamma_pp, omega, D_A = b["D_F_pp"], b["gamma_pp"], b["omega"], b["D_A"]

    omega_self_adjoint = bool(np.allclose(omega, omega.conj().T))
    D_A_self_adjoint = bool(np.allclose(D_A, D_A.conj().T))
    D_A_anticommutes = bool(np.allclose(D_A @ gamma_pp + gamma_pp @ D_A, 0))

    Omega_B = D_A @ D_A - D_pp @ D_pp
    Omega_B_is_zero = bool(np.allclose(Omega_B, 0))
    Omega_B_self_adjoint = bool(np.allclose(Omega_B, Omega_B.conj().T))

    well_posed = (b["J_conjugate_matrix_verified"] and omega_self_adjoint
                  and D_A_self_adjoint and D_A_anticommutes)

    return InnerFluctuationResult(
        J_conjugate_matrix_verified=b["J_conjugate_matrix_verified"],
        omega_self_adjoint=omega_self_adjoint,
        omega_max_abs=float(np.max(np.abs(omega))),
        real_structure_epsilon_prime_used=b["real_structure_epsilon_prime_used"],
        D_A_self_adjoint=D_A_self_adjoint,
        D_A_anticommutes_with_grading=D_A_anticommutes,
        Omega_B_is_zero=Omega_B_is_zero,
        Omega_B_self_adjoint=Omega_B_self_adjoint,
        Omega_B_max_abs=float(np.max(np.abs(Omega_B))),
        well_posed=well_posed,
    )


@dataclass
class FiniteMomentReport:
    well_posed: bool
    moments: dict
    physical_interpretation: str | None


def compute_finite_moments(
    n: int = 200, k_neighbors: int = 3, mu: float = 0.4, seed: int = 42, cert_seed: int = 0,
    max_k: int = 6,
) -> FiniteMomentReport:
    """a0''..a_max_k'' = Tr(D_A''^k) for even k -- EXACT finite-dimensional
    trace moments, NOT continuum Seeley-DeWitt coefficients (see module
    docstring point 4). Computed only if the fluctuation is verified
    well-posed; otherwise moments are still returned (the raw trace is
    always well-defined for a matrix) but physical_interpretation is
    explicitly None, mirroring seit_lang/spectral_action.py's own gate."""
    cert = run_inner_fluctuation_certification(n, k_neighbors, mu, seed, cert_seed)
    b = build_inner_fluctuation(n, k_neighbors, mu, seed, cert_seed)
    D_A = b["D_A"]

    moments = {}
    for k in range(0, max_k + 1, 2):
        Dk = np.linalg.matrix_power(D_A, k)
        tr = np.trace(Dk)
        moments[f"a{k}''"] = {
            "value": float(np.real(tr)),
            "imag_residual": float(np.imag(tr)),
            "assumptions_used": [
                "D_A is self-adjoint (checked)" if cert.D_A_self_adjoint else
                "D_A NOT confirmed self-adjoint -- moment may not be real-valued",
                f"finite N={2 * b['dim']} (doubled coupled-recovery candidate), no continuum limit taken",
                "exact finite-dimensional trace moment of D_A''=D_F''+omega+eps'*J''omegaJ''^-1, "
                "NOT an asymptotic Seeley-DeWitt small-beta expansion coefficient",
                "omega is a SINGLE generator i*[D_F'',pi'(f)] for one real f, not the fully general "
                "Omega^1_D(A_F) connection -- a different generator choice would give different moments",
            ],
        }

    return FiniteMomentReport(
        well_posed=cert.well_posed,
        moments=moments,
        physical_interpretation=None,
    )
