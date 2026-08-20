"""Ollivier-Ricci discrete curvature (Ollivier 2009; Lin-Lu-Yau 2011;
Jost-Liu 2014) computed directly from graph G's own random-walk structure.

This is an established, parameter-free alternative route around the
blocked CL-METRIC-TO-CONNECTION chainlink
(compiler/protocol/derivation_chainlinks.py): the diffusion-distance
metric candidate is non-unique because it depends on a freely chosen time
parameter t, but Ollivier-Ricci curvature has one canonical definition
using only the graph's own adjacency structure -- the alpha=0 ("no
laziness") convention, where each vertex's one-step random-walk measure
is uniform over its immediate neighbors. There is no free parameter to
choose here, unlike the diffusion-distance construction.

THIS DOES NOT RESOLVE CL-METRIC-TO-CONNECTION. It is an independent,
established discrete-geometry curvature notion, not a continuum
Levi-Civita-connection/Riemann-curvature construction built from
METRIC-CANDIDATE. See compiler/protocol/derivation_chainlinks.py's
CL-OPERATOR-TO-CURVATURE-DISCRETE for how this is represented without
conflating the two, and why the original chainlink stays OPEN.

Definition: for an edge (x,y), let m_x, m_y be the one-step random-walk
measures at x, y (uniform over neighbors, alpha=0):

    kappa(x,y) = 1 - W1(m_x, m_y) / d(x,y)

where W1 is the Wasserstein-1 (earth mover's) distance under the graph's
shortest-path metric and d(x,y) is that same shortest-path distance
(=1 on an edge).

W1 is computed two independent ways and cross-checked (this module's own
falsification obligation -- see compiler/ir/ollivier_ricci_ir.py for the
mathematical_invariance_test that runs this check):

1. PRIMAL: the discrete optimal-transport linear program (minimize total
   transport cost over a coupling matching the two marginals).
2. DUAL: the Kantorovich-Rubinstein dual of that exact LP (maximize
   sum_i f_i mu_i - sum_j f_j nu_j over a 1-Lipschitz potential f on the
   union of the two supports, w.r.t. the same shortest-path metric).

Strong LP duality guarantees these must agree exactly (up to solver
tolerance) for a correctly implemented pair of formulations -- a nonzero
duality gap indicates an implementation bug, not a physics finding.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog
from scipy.sparse.csgraph import shortest_path

from compiler.backends.graph_laplacian import Graph


@dataclass
class EdgeCurvature:
    u: int
    v: int
    w1_primal: float
    w1_dual: float
    duality_gap: float
    kappa: float


@dataclass
class OllivierRicciResult:
    graph_label: str
    edge_curvatures: list[EdgeCurvature]
    mean_kappa: float
    vertex_kappa: dict[int, float]
    max_duality_gap: float

    def to_summary(self) -> dict:
        return {
            "graph_label": self.graph_label,
            "n_edges": len(self.edge_curvatures),
            "mean_kappa": self.mean_kappa,
            "max_duality_gap": self.max_duality_gap,
            "edge_curvatures": [
                {"u": e.u, "v": e.v, "kappa": e.kappa, "w1_primal": e.w1_primal,
                 "w1_dual": e.w1_dual, "duality_gap": e.duality_gap}
                for e in self.edge_curvatures
            ],
        }


def _neighbor_measure(adjacency: np.ndarray, x: int) -> tuple[list[int], np.ndarray]:
    neighbors = list(np.nonzero(adjacency[x])[0])
    if not neighbors:
        return [], np.array([])
    mass = np.full(len(neighbors), 1.0 / len(neighbors))
    return neighbors, mass


def _w1_primal(support_x: list[int], mass_x: np.ndarray,
                support_y: list[int], mass_y: np.ndarray, dist: np.ndarray) -> float:
    nx, ny = len(support_x), len(support_y)
    if nx == 0 or ny == 0:
        return 0.0
    cost = np.array([[dist[i, j] for j in support_y] for i in support_x]).ravel()
    A_eq = []
    b_eq = []
    for i in range(nx):
        row = np.zeros(nx * ny)
        row[i * ny:(i + 1) * ny] = 1.0
        A_eq.append(row)
        b_eq.append(mass_x[i])
    for j in range(ny):
        row = np.zeros(nx * ny)
        row[j::ny] = 1.0
        A_eq.append(row)
        b_eq.append(mass_y[j])
    res = linprog(cost, A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"Ollivier-Ricci OT primal LP failed to solve: {res.message}")
    return float(res.fun)


def _w1_dual(support_x: list[int], mass_x: np.ndarray,
             support_y: list[int], mass_y: np.ndarray, dist: np.ndarray) -> float:
    """Kantorovich-Rubinstein dual of the exact same transportation LP
    _w1_primal solves -- see module docstring for the derivation."""
    support = list(dict.fromkeys(list(support_x) + list(support_y)))
    idx = {v: k for k, v in enumerate(support)}
    m = len(support)
    if m == 0:
        return 0.0
    c = np.zeros(m)
    for i, v in enumerate(support_x):
        c[idx[v]] -= mass_x[i]
    for j, v in enumerate(support_y):
        c[idx[v]] += mass_y[j]
    A_ub, b_ub = [], []
    for p in support:
        for q in support:
            if p == q:
                continue
            row = np.zeros(m)
            row[idx[p]] = 1.0
            row[idx[q]] = -1.0
            A_ub.append(row)
            b_ub.append(dist[p, q])
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=(None, None), method="highs")
    if not res.success:
        raise RuntimeError(f"Ollivier-Ricci OT dual LP failed to solve: {res.message}")
    return float(-res.fun)


def ollivier_ricci_curvature(graph: Graph) -> OllivierRicciResult:
    A = graph.adjacency()
    n = graph.n
    dist = shortest_path(A, method="D", unweighted=True, directed=False)
    edge_curvatures = []
    for u, v in graph.edges:
        sx, mx = _neighbor_measure(A, u)
        sy, my = _neighbor_measure(A, v)
        w1p = _w1_primal(sx, mx, sy, my, dist)
        w1d = _w1_dual(sx, mx, sy, my, dist)
        d_uv = dist[u, v]
        kappa = 1.0 - w1p / d_uv if d_uv > 0 else 0.0
        edge_curvatures.append(EdgeCurvature(
            u=int(u), v=int(v), w1_primal=w1p, w1_dual=w1d,
            duality_gap=abs(w1p - w1d), kappa=kappa,
        ))
    mean_kappa = float(np.mean([e.kappa for e in edge_curvatures])) if edge_curvatures else 0.0
    vertex_incident: dict[int, list[float]] = {i: [] for i in range(n)}
    for e in edge_curvatures:
        vertex_incident[e.u].append(e.kappa)
        vertex_incident[e.v].append(e.kappa)
    vertex_kappa = {i: (float(np.mean(v)) if v else 0.0) for i, v in vertex_incident.items()}
    max_gap = max((e.duality_gap for e in edge_curvatures), default=0.0)
    return OllivierRicciResult(
        graph_label=graph.label, edge_curvatures=edge_curvatures,
        mean_kappa=mean_kappa, vertex_kappa=vertex_kappa, max_duality_gap=max_gap,
    )
