"""Spectral -> diffusion distance -> metric candidate (spec section 32).

d_t(i,j)^2 = sum_{n: lambda_n > 0} e^{-2 t lambda_n} (phi_n(i) - phi_n(j))^2

This is the standard diffusion-map distance built from Spec(L); it is
NOT declared a Riemannian metric. Spec section 32 requires we explicitly
classify the construction as exact / approximate / conditional /
divergent / non-unique across a refinement sweep, and explicitly
forbids inferring continuum geometry from numerical resemblance. The
diffusion time t is a free parameter of the construction; we test
sensitivity to it directly rather than silently fixing it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from compiler.backends.graph_laplacian import build_graph, laplacian
from compiler.backends.spectral import SpectralData, spectrum

Classification = Literal["exact", "approximate", "conditional", "divergent", "non_unique"]


def diffusion_distance_matrix(spec: SpectralData, t: float) -> np.ndarray:
    nonzero = [i for i in range(len(spec.eigenvalues)) if i not in spec.zero_modes]
    if not nonzero:
        n = spec.eigenvectors.shape[0]
        return np.zeros((n, n))
    lam = spec.eigenvalues[nonzero]
    Phi = spec.eigenvectors[:, nonzero]  # n x k
    weights = np.exp(-t * lam)  # note: single exponent, standard diffusion-map convention
    weighted = Phi * weights  # broadcast over columns
    n = Phi.shape[0]
    D2 = np.zeros((n, n))
    for k in range(weighted.shape[1]):
        col = weighted[:, k]
        D2 += (col[:, None] - col[None, :]) ** 2
    return np.sqrt(D2)


def nearest_neighbor_stats(g, D: np.ndarray) -> dict:
    vals = [D[i, j] for i, j in g.edges]
    return {"mean": float(np.mean(vals)), "std": float(np.std(vals)), "n_edges": len(vals)}


@dataclass
class RefinementPoint:
    n: int
    t: float
    nn_mean: float
    nn_std: float


@dataclass
class MetricCandidateReport:
    topology: str
    tau_multiplier: float
    points: list[RefinementPoint]
    normalized_sequence: list[float]  # nn_mean * n  (candidate O(1/n) spacing check)
    relative_changes: list[float]
    classification: Classification
    reason: str
    across_time_choice_spread: float  # sensitivity to the free parameter t

    def to_dict(self) -> dict:
        return {
            "topology": self.topology,
            "tau_multiplier": self.tau_multiplier,
            "points": [p.__dict__ for p in self.points],
            "normalized_sequence": self.normalized_sequence,
            "relative_changes": self.relative_changes,
            "classification": self.classification,
            "reason": self.reason,
            "across_time_choice_spread": self.across_time_choice_spread,
        }


def _refinement_run(topology: str, sizes: list[int], tau_multiplier: float) -> list[RefinementPoint]:
    points = []
    for n in sizes:
        g = build_graph(topology, n)
        L = laplacian(g.adjacency())
        spec = spectrum(L)
        gap = spec.spectral_gap
        tau = 1.0 / gap if gap > 1e-12 else 1.0
        t = tau_multiplier * tau
        D = diffusion_distance_matrix(spec, t)
        stats = nearest_neighbor_stats(g, D)
        points.append(RefinementPoint(n=n, t=t, nn_mean=stats["mean"], nn_std=stats["std"]))
    return points


def refinement_sweep(
    topology: str = "cycle",
    sizes: list[int] | None = None,
    tau_multipliers: list[float] | None = None,
) -> MetricCandidateReport:
    sizes = sizes or [8, 16, 32, 64, 128]
    tau_multipliers = tau_multipliers or [0.5, 1.0, 2.0]

    # Primary run at the reference tau_multiplier (first in list)
    primary_tau = tau_multipliers[0]
    points = _refinement_run(topology, sizes, primary_tau)

    # candidate O(1/n) spacing normalization: if nn distance ~ c/n, this
    # sequence should converge to a constant c as n grows.
    normalized = [p.nn_mean * p.n for p in points]
    rel_changes = [
        abs(normalized[i + 1] - normalized[i]) / max(abs(normalized[i]), 1e-15)
        for i in range(len(normalized) - 1)
    ]

    # Sensitivity to the free diffusion-time parameter: rerun refinement
    # at each tau_multiplier and compare the *limiting* normalized value.
    limiting_values = []
    for tm in tau_multipliers:
        pts = _refinement_run(topology, sizes, tm)
        limiting_values.append(pts[-1].nn_mean * pts[-1].n)
    spread = float(np.std(limiting_values) / max(abs(np.mean(limiting_values)), 1e-15))

    shrinking = all(rel_changes[i + 1] <= rel_changes[i] * 1.05 + 1e-9 for i in range(len(rel_changes) - 1)) \
        if len(rel_changes) > 1 else True
    converged_numerically = len(rel_changes) > 0 and rel_changes[-1] < 0.05

    if spread > 0.05:
        classification: Classification = "non_unique"
        reason = (
            f"limiting normalized nearest-neighbor diffusion distance depends on the "
            f"free diffusion-time parameter (relative spread {spread:.3f} across "
            f"tau multipliers {tau_multipliers}); no canonical time choice is derived "
            f"upstream, so no single metric candidate is selected"
        )
    elif not converged_numerically:
        classification = "divergent"
        reason = (
            f"normalized nearest-neighbor distance does not settle under refinement "
            f"(last relative change {rel_changes[-1] if rel_changes else float('nan'):.3f}); "
            f"no continuum metric limit is supported by this data"
        )
    else:
        classification = "conditional"
        reason = (
            "normalized nearest-neighbor diffusion distance converges numerically under "
            "refinement at a fixed diffusion-time scale, consistent with an O(1/n) "
            "spacing limit; this is NOT a proof of convergence to a continuum metric "
            "(no analytic error bound, no regularity/dimensionality argument registered) "
            "and remains conditional on the arbitrary tau_multiplier choice"
        )

    return MetricCandidateReport(
        topology=topology, tau_multiplier=primary_tau, points=points,
        normalized_sequence=normalized, relative_changes=rel_changes,
        classification=classification, reason=reason,
        across_time_choice_spread=spread,
    )
