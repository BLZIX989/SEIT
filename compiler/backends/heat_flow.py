"""Heat / persistence engine (spec section 15).

R(t) = e^{-tL}, R(t) phi_n = e^{-t lambda_n} phi_n, and (under the stated
hypothesis that L is symmetric positive-semidefinite with a well-defined
kernel) lim_{t->inf} e^{-tL} = P_ker(L). All hypotheses are checked
numerically before the convergence claim is registered, never assumed.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from compiler.backends.spectral import SpectralData


@dataclass
class HeatFlowResult:
    t: float
    R_t: np.ndarray
    eigen_action_residual: float  # max || R(t) phi_n - e^{-t lambda_n} phi_n ||


def heat_operator(L: np.ndarray, t: float) -> np.ndarray:
    return expm(-t * L)


def verify_eigen_action(L: np.ndarray, spec: SpectralData, t: float) -> HeatFlowResult:
    R_t = heat_operator(L, t)
    residuals = []
    for i, lam in enumerate(spec.eigenvalues):
        phi = spec.eigenvectors[:, i]
        lhs = R_t @ phi
        rhs = np.exp(-t * lam) * phi
        residuals.append(np.linalg.norm(lhs - rhs))
    return HeatFlowResult(t=t, R_t=R_t, eigen_action_residual=float(max(residuals)) if residuals else 0.0)


def verify_kernel_convergence(
    L: np.ndarray, spec: SpectralData, *, t_values: list[float]
) -> dict:
    """Checks the hypotheses of lim_{t->inf} e^{-tL} = P_ker(L) rather than
    assuming them: requires L symmetric (checked), and reports the
    residual ||R(t) - P_ker(L)|| as a function of t. If L has a nontrivial
    negative spectrum (not PSD) or the residual does not shrink with t,
    convergence is NOT claimed.
    """
    is_symmetric = bool(np.allclose(L, L.T, atol=1e-10))
    is_psd = bool(np.all(spec.eigenvalues >= -1e-8))
    P_ker = spec.kernel_projector()
    residuals = []
    for t in t_values:
        R_t = heat_operator(L, t)
        residuals.append(float(np.linalg.norm(R_t - P_ker)))
    monotone_decreasing = all(
        residuals[i + 1] <= residuals[i] + 1e-9 for i in range(len(residuals) - 1)
    )
    converges = is_symmetric and is_psd and monotone_decreasing and residuals[-1] < 1e-6
    return {
        "hypotheses": {"symmetric": is_symmetric, "positive_semidefinite": is_psd},
        "t_values": t_values,
        "residuals": residuals,
        "monotone_decreasing": monotone_decreasing,
        "converges": converges,
    }
