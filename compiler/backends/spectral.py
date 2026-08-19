"""Spectral engine (spec section 14).

Lphi_n = lambda_n phi_n. Registers eigenvalues, eigenvectors,
multiplicity, zero modes, spectral gap, projectors. Physical
correspondence (lambda_n = physical energy) is explicitly NOT assumed
here; that would require a separate bridge transformation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class SpectralData:
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray  # columns are eigenvectors, matching eigenvalues order
    tol: float = 1e-9

    @property
    def zero_modes(self) -> list[int]:
        return [i for i, lam in enumerate(self.eigenvalues) if abs(lam) < self.tol]

    @property
    def multiplicities(self) -> dict[float, int]:
        mult: dict[float, int] = {}
        rounded = np.round(self.eigenvalues / self.tol) * self.tol
        for lam in rounded:
            key = round(float(lam), 9)
            mult[key] = mult.get(key, 0) + 1
        return mult

    @property
    def spectral_gap(self) -> float:
        nonzero = sorted(lam for lam in self.eigenvalues if abs(lam) >= self.tol)
        return float(nonzero[0]) if nonzero else 0.0

    def kernel_projector(self) -> np.ndarray:
        idx = self.zero_modes
        if not idx:
            n = self.eigenvectors.shape[0]
            return np.zeros((n, n))
        V = self.eigenvectors[:, idx]
        return V @ V.T

    def eigen_equation_residual(self, L: np.ndarray) -> float:
        """max_n || L phi_n - lambda_n phi_n || (numerical verification of
        the defining eigen-equation, spec section 14)."""
        residuals = []
        for i, lam in enumerate(self.eigenvalues):
            phi = self.eigenvectors[:, i]
            residuals.append(np.linalg.norm(L @ phi - lam * phi))
        return float(max(residuals)) if residuals else 0.0


def spectrum(L: np.ndarray, *, tol: float = 1e-9) -> SpectralData:
    """L is symmetric (graph Laplacian) so we use eigh (real symmetric
    solver) rather than a general eigensolver."""
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    return SpectralData(eigenvalues=eigenvalues, eigenvectors=eigenvectors, tol=tol)


def spectrum_exact(L_exact):
    """Exact eigenvalues via sympy's characteristic polynomial, used on
    small graphs to cross-check the numeric solver (spec section 31:
    'exact arithmetic where possible')."""
    return L_exact.eigenvals()  # {eigenvalue: algebraic multiplicity}
