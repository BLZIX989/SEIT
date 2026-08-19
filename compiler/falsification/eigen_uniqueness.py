"""Executed counterexample: Spec(H) alone does not determine H (spec
section 7B of the FC-005 build command / workbook R-003, TEST-006:
"H' = U H U^dagger has same spectrum" but H' != H in general).

This is not asserted -- a concrete Hermitian H and random unitary U are
constructed, Spec(H) and Spec(U H U^dagger) are verified numerically
equal (up to floating point), and H != U H U^dagger is verified directly,
for several random instances.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class EigenUniquenessCounterexample:
    n: int
    n_trials: int
    n_confirmed: int
    example_H: list
    example_U: list
    example_H_prime: list
    spectra_match_max_residual: float
    matrices_differ: bool

    def to_dict(self) -> dict:
        return {
            "n": self.n, "n_trials": self.n_trials, "n_confirmed": self.n_confirmed,
            "example_H": self.example_H, "example_U": self.example_U,
            "example_H_prime": self.example_H_prime,
            "spectra_match_max_residual": self.spectra_match_max_residual,
            "matrices_differ": self.matrices_differ,
        }


def random_unitary(n: int, rng: np.random.Generator) -> np.ndarray:
    z = (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diagonal(r)
    ph = d / np.abs(d)
    return q * ph


def run_counterexample(n: int = 2, n_trials: int = 25, seed: int = 0) -> EigenUniquenessCounterexample:
    rng = np.random.default_rng(seed)
    max_residual = 0.0
    n_confirmed = 0
    example_H = example_U = example_Hp = None
    for trial in range(n_trials):
        A = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
        H = (A + A.conj().T) / 2  # Hermitian
        U = random_unitary(n, rng)
        H_prime = U @ H @ U.conj().T

        lam_H = np.sort(np.linalg.eigvalsh(H))
        lam_Hp = np.sort(np.linalg.eigvalsh(H_prime))
        residual = float(np.max(np.abs(lam_H - lam_Hp)))
        max_residual = max(max_residual, residual)

        differs = not np.allclose(H, H_prime, atol=1e-8)
        if residual < 1e-8 and differs:
            n_confirmed += 1
            if example_H is None:
                example_H, example_U, example_Hp = H, U, H_prime

    return EigenUniquenessCounterexample(
        n=n, n_trials=n_trials, n_confirmed=n_confirmed,
        example_H=np.round(example_H, 4).tolist() if example_H is not None else [],
        example_U=np.round(example_U, 4).tolist() if example_U is not None else [],
        example_H_prime=np.round(example_Hp, 4).tolist() if example_Hp is not None else [],
        spectra_match_max_residual=max_residual,
        matrices_differ=n_confirmed > 0,
    )
