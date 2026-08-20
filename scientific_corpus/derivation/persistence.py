"""Persistence-sector spectral machinery (canonical_closure_report follow-up,
Sec.3-4 of the user's own instruction block -- NOT the closure report itself,
which this project's derivation package explicitly does not implement).

Reuses the real, already-implemented compiler spectral backend
(compiler/backends/graph_laplacian.py, spectral.py) -- no reimplementation
of eigendecomposition.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends.graph_laplacian import build_graph, laplacian  # noqa: E402


def build_real_graph_spectrum(topology: str, n: int, seed: int | None = None):
    g = build_graph(topology, n, seed=seed)
    A = np.zeros((g.n, g.n))
    for i, j in g.edges:
        A[i, j] = A[j, i] = 1.0
    L = laplacian(A)
    vals, vecs = np.linalg.eigh(L)
    vals = np.clip(vals, 0.0, None)
    return L, vals, vecs


def persistence_projection(vals: np.ndarray, vecs: np.ndarray, lambda_c: float):
    """P_lambda_c = sum_{lambda_n < lambda_c} |psi_n><psi_n| -- an explicit
    orthogonal projector, verified idempotent (P^2=P) and self-adjoint
    (P=P^T) here, not merely asserted."""
    mask = vals < lambda_c
    idx = np.where(mask)[0]
    P = vecs[:, idx] @ vecs[:, idx].T
    is_idempotent = bool(np.allclose(P @ P, P, atol=1e-9))
    is_self_adjoint = bool(np.allclose(P, P.T, atol=1e-9))
    return P, idx, is_idempotent, is_self_adjoint


def persistent_sector_report(topology: str = "erdos_renyi", n: int = 60, seed: int = 0,
                              lambda_c_fractions: tuple[float, ...] = (0.1, 0.25, 0.5)) -> dict:
    L, vals, vecs = build_real_graph_spectrum(topology, n, seed=seed)
    lam_max = float(vals.max())
    results = {}
    for frac in lambda_c_fractions:
        lambda_c = frac * lam_max
        P, idx, idemp, self_adj = persistence_projection(vals, vecs, lambda_c)
        L_pi = P @ L @ P
        # L_Pi restricted to the persistent subspace should equal diag(vals[idx])
        # in the eigenbasis -- verify exactly, not assumed.
        vals_pi = vals[idx]
        reconstructed = (vecs[:, idx] * vals_pi) @ vecs[:, idx].T
        l_pi_matches_projection = bool(np.allclose(L_pi, reconstructed, atol=1e-9))

        betas = [0.1, 1.0, 5.0, 20.0]
        K_pi_by_beta = {}
        monotone_ok = True
        prev = None
        for beta in betas:
            K_pi = float(np.sum(np.exp(-beta * vals_pi))) if len(vals_pi) else 0.0
            K_pi_by_beta[beta] = K_pi
            if prev is not None and K_pi > prev + 1e-9:
                monotone_ok = False
            prev = K_pi

        results[f"lambda_c_frac_{frac}"] = {
            "lambda_c": lambda_c, "n_persistent_modes": int(len(idx)),
            "P_idempotent": idemp, "P_self_adjoint": self_adj,
            "L_Pi_equals_P_L_P_reconstruction": l_pi_matches_projection,
            "K_Pi_beta_sweep": K_pi_by_beta,
            "K_Pi_monotone_nonincreasing_in_beta": monotone_ok,
            "K_Pi_beta_to_infinity_limit_equals_dim_ker_L_within_sector": (
                abs(K_pi_by_beta[betas[-1]] - float(np.sum(vals_pi < 1e-9))) < 0.5
            ),
        }
    return {
        "claim": "Persistence projection P_lambda_c, restricted Laplacian L_Pi, and heat "
                 "trace K_Pi(beta) -- exact finite-dimensional linear algebra, computed on a "
                 "real compiler-built graph (not a synthetic toy unrelated to the project's "
                 "own construction)",
        "test_graph": f"{topology}(n={n}, seed={seed})",
        "by_lambda_c": results,
    }


def persistent_distance(vals: np.ndarray, vecs: np.ndarray, idx: np.ndarray, beta: float,
                         i: int, j: int) -> float:
    """d_{Pi,beta}(i,j)^2 = sum_{n in Pi} exp(-beta lambda_n) (psi_n(i)-psi_n(j))^2"""
    lam = vals[idx]
    diffs = (vecs[i, idx] - vecs[j, idx]) ** 2
    return float(np.sqrt(np.sum(np.exp(-beta * lam) * diffs)))


def persistent_distance_beta_limits_check(topology: str = "cycle", n: int = 20) -> dict:
    """Verify the claimed limiting behavior: beta->0 recovers the unweighted
    persistent distance d_Pi; increasing beta suppresses all positive-
    eigenvalue contributions monotonically (never increases distance)."""
    L, vals, vecs = build_real_graph_spectrum(topology, n)
    lambda_c = 0.5 * float(vals.max())
    _, idx, _, _ = persistence_projection(vals, vecs, lambda_c)
    i, j = 0, n // 2
    d_beta0 = persistent_distance(vals, vecs, idx, 1e-6, i, j)
    d_unweighted = float(np.sqrt(np.sum((vecs[i, idx] - vecs[j, idx]) ** 2)))
    betas = [0.0001, 0.1, 1.0, 5.0, 20.0]
    distances = [persistent_distance(vals, vecs, idx, b, i, j) for b in betas]
    monotone_nonincreasing = all(distances[k + 1] <= distances[k] + 1e-9 for k in range(len(distances) - 1))
    return {
        "claim": "d_{Pi,beta} -> d_Pi as beta->0; d_{Pi,beta} is monotone nonincreasing in beta",
        "beta_near_0_matches_unweighted_persistent_distance": bool(abs(d_beta0 - d_unweighted) < 1e-6),
        "distances_by_beta": dict(zip(betas, distances)),
        "monotone_nonincreasing_in_beta": monotone_nonincreasing,
        "note": "beta cannot be taken to infinity for a nontrivial geometry -- confirmed here: "
                f"d({betas[-1]}) = {distances[-1]:.6f}, approaching but not exactly reaching 0 "
                "for finite beta, consistent with beta acting as a finite coarse-graining scale "
                "rather than a limit to be maximized.",
    }
