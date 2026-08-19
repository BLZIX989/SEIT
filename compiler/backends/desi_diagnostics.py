"""FC-005 continuum-limit failure diagnostics (spec: full diagnostic
investigation of the CONTINUUM-LIMIT-L-DESI Gate 1 failure). Every
function here is a MEASUREMENT, not a fix -- corrections derived from
these measurements are applied explicitly and separately, with their
justification recorded, never silently.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy.spatial import cKDTree

from compiler.backends.desi_graph import build_kernel_graph, graph_laplacian_from_weights


# ---------------------------------------------------------------------
# 1. Graph construction audit (spec section 3)
# ---------------------------------------------------------------------

@dataclass
class GraphAudit:
    n_nodes: int
    W_nonneg: bool
    W_symmetric: bool
    L_symmetric: bool
    L_row_sum_max_abs: float
    vTLv_min_over_200: float
    n_connected_components: int
    largest_component_fraction: float
    n_isolated_nodes: int
    degree_min: float
    degree_max: float
    degree_mean: float
    degree_median: float
    avg_neighbors_above_threshold: float
    sparsity_fraction_nonzero: float
    edge_length_median: float
    edge_length_p10: float
    edge_length_p90: float

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def _connected_components(W: np.ndarray) -> tuple[int, np.ndarray]:
    n = W.shape[0]
    labels = -np.ones(n, dtype=int)
    comp = 0
    for start in range(n):
        if labels[start] != -1:
            continue
        stack = [start]
        labels[start] = comp
        while stack:
            i = stack.pop()
            for j in np.nonzero(W[i] > 1e-12)[0]:
                if labels[j] == -1:
                    labels[j] = comp
                    stack.append(j)
        comp += 1
    return comp, labels


def audit_graph(points: np.ndarray, W: np.ndarray, *, seed: int = 0) -> GraphAudit:
    n = W.shape[0]
    D, L = graph_laplacian_from_weights(W)

    rng = np.random.default_rng(seed)
    vtlv_min = min(float(v @ L @ v) for v in (rng.normal(size=n) for _ in range(200)))

    n_components, labels = _connected_components(W)
    comp_sizes = np.bincount(labels)
    largest_fraction = float(comp_sizes.max() / n)

    degree = W.sum(axis=1)
    n_isolated = int(np.sum(degree < 1e-10))

    above = W > 1e-6
    avg_neighbors = float(np.mean(np.sum(above, axis=1)))
    sparsity = float(np.mean(above))

    ii, jj = np.triu_indices(n, k=1)
    mask = W[ii, jj] > 1e-6
    if mask.any():
        edge_lengths = np.linalg.norm(points[ii[mask]] - points[jj[mask]], axis=1)
        el_median, el_p10, el_p90 = (float(np.median(edge_lengths)),
                                      float(np.percentile(edge_lengths, 10)),
                                      float(np.percentile(edge_lengths, 90)))
    else:
        el_median = el_p10 = el_p90 = float("nan")

    return GraphAudit(
        n_nodes=n, W_nonneg=bool(np.all(W >= 0)), W_symmetric=bool(np.allclose(W, W.T, atol=1e-12)),
        L_symmetric=bool(np.allclose(L, L.T, atol=1e-10)),
        L_row_sum_max_abs=float(np.max(np.abs(L.sum(axis=1)))),
        vTLv_min_over_200=vtlv_min,
        n_connected_components=n_components, largest_component_fraction=largest_fraction,
        n_isolated_nodes=n_isolated,
        degree_min=float(degree.min()), degree_max=float(degree.max()),
        degree_mean=float(degree.mean()), degree_median=float(np.median(degree)),
        avg_neighbors_above_threshold=avg_neighbors, sparsity_fraction_nonzero=sparsity,
        edge_length_median=el_median, edge_length_p10=el_p10, edge_length_p90=el_p90,
    )


# ---------------------------------------------------------------------
# 2. Sampling density diagnostics (spec section 4)
# ---------------------------------------------------------------------

def median_nn_distance(points: np.ndarray, k: int = 1) -> float:
    tree = cKDTree(points)
    nn_dist, _ = tree.query(points, k=k + 1)
    return float(np.median(nn_dist[:, k]))


def local_density_variation(points: np.ndarray, k: int = 8) -> dict:
    """kNN-radius-based local density estimate: rho_i ~ k / (V_d * r_{i,k}^d)."""
    tree = cKDTree(points)
    dist, _ = tree.query(points, k=k + 1)
    r_k = dist[:, k]
    d = points.shape[1]
    vol_unit_ball = np.pi ** (d / 2) / np.math.gamma(d / 2 + 1)
    density = k / (vol_unit_ball * r_k ** d)
    return {
        "k": k, "r_k_median": float(np.median(r_k)), "r_k_p10": float(np.percentile(r_k, 10)),
        "r_k_p90": float(np.percentile(r_k, 90)),
        "density_median": float(np.median(density)),
        "density_coefficient_of_variation": float(np.std(density) / np.mean(density)),
    }


# ---------------------------------------------------------------------
# 3. Bandwidth / k sweep (spec section 7)
# ---------------------------------------------------------------------

@dataclass
class BandwidthPoint:
    epsilon_multiplier: float
    epsilon: float
    connected: bool
    largest_component_fraction: float
    avg_neighbors: float
    sparsity: float
    spectral_gap: float
    low_eigenvalues: list[float]
    operator_row_sum_max_abs: float

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def bandwidth_sweep(points: np.ndarray, weights: np.ndarray | None, *,
                     multipliers: list[float], n_modes: int = 20) -> list[BandwidthPoint]:
    base_nn = median_nn_distance(points)
    results = []
    for m in multipliers:
        eps = m * base_nn
        W = build_kernel_graph(points, epsilon=eps, weights=weights)
        D, L = graph_laplacian_from_weights(W)
        n_components, labels = _connected_components(W)
        comp_sizes = np.bincount(labels)
        largest_fraction = float(comp_sizes.max() / len(points))
        avg_neighbors = float(np.mean(np.sum(W > 1e-6, axis=1)))
        sparsity = float(np.mean(W > 1e-6))
        eigvals = np.linalg.eigvalsh(L)
        nonzero = eigvals[eigvals > 1e-8]
        gap = float(nonzero[0]) if len(nonzero) else 0.0
        results.append(BandwidthPoint(
            epsilon_multiplier=m, epsilon=eps, connected=(n_components == 1),
            largest_component_fraction=largest_fraction, avg_neighbors=avg_neighbors,
            sparsity=sparsity, spectral_gap=gap,
            low_eigenvalues=eigvals[:n_modes].tolist(),
            operator_row_sum_max_abs=float(np.max(np.abs(L.sum(axis=1)))),
        ))
    return results


# ---------------------------------------------------------------------
# 4. Operator-action test (spec section 11)
# ---------------------------------------------------------------------

def operator_action_residual(L_tilde: np.ndarray, points: np.ndarray,
                              f: Callable[[np.ndarray], np.ndarray],
                              delta_f: Callable[[np.ndarray], np.ndarray] | None) -> dict:
    """||L_tilde f - Delta f|| when a reference Delta f is known (synthetic
    controls with a flat/known metric only); otherwise reports ||L_tilde f||
    alone as a self-consistency diagnostic (e.g. for a harmonic f, this
    should be small in the well-resolved regime -- NOT a proof of
    convergence to any particular Delta_h, since none is independently
    available for the real DESI point cloud's unknown metric)."""
    f_vals = f(points)
    Lf = L_tilde @ f_vals
    if delta_f is not None:
        ref = delta_f(points)
        residual = float(np.linalg.norm(Lf - ref) / max(np.linalg.norm(ref), 1e-12))
        return {"has_reference": True, "relative_residual": residual}
    return {"has_reference": False, "note": "no independent continuum Delta_h available for this "
                                            "point set (unknown metric) -- reporting ||L_tilde f|| "
                                            "as a self-consistency diagnostic only, not a convergence proof",
            "L_tilde_f_norm": float(np.linalg.norm(Lf)), "f_norm": float(np.linalg.norm(f_vals))}
