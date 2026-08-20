"""Independent construction and locality test of a genuinely different
Dirac-operator candidate, on the EXACT SAME graph H2 already used
(compiler/backends/toe_closure_hypotheses.py::h2_spectral_triple_locality_check),
so the comparison against the existing FAIL result is apples-to-apples.

This produces a NEW claim, H2B, coexisting with (never overwriting)
H2-SPECTRAL-TRIPLE-LOCALITY = FAIL.
"""
from __future__ import annotations

import itertools

import numpy as np


def _build_h2_ring_graph(n: int = 200, k_neighbors: int = 3) -> np.ndarray:
    """Byte-for-byte the same construction as
    h2_spectral_triple_locality_check's W matrix."""
    W = np.zeros((n, n))
    for i in range(n):
        for k in range(1, k_neighbors + 1):
            j = (i + k) % n
            W[i, j] = W[j, i] = 1.0
    return W


def _extract_triangles(W: np.ndarray) -> list[tuple[int, int, int]]:
    """All 3-cliques of the adjacency matrix -- the natural 2-cells this
    graph actually supports (a k>=2 nearest-neighbour ring has many, since
    i, i+1, i+2 are mutually adjacent)."""
    n = W.shape[0]
    triangles = []
    for i, j, k in itertools.combinations(range(n), 3):
        if W[i, j] and W[j, k] and W[i, k]:
            triangles.append((i, j, k))
    return triangles


def build_block_dirac_locality_test(n: int = 200, k_neighbors: int = 3) -> dict:
    W = _build_h2_ring_graph(n, k_neighbors)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if W[i, j]]
    edge_index = {e: idx for idx, e in enumerate(edges)}
    triangles = _extract_triangles(W)

    d1 = np.zeros((n, len(edges)))
    for col, (i, j) in enumerate(edges):
        d1[i, col] = -1
        d1[j, col] = 1

    N0, N1 = n, len(edges)
    D = np.zeros((N0 + N1, N0 + N1))
    D[:N0, N0:] = d1
    D[N0:, :N0] = d1.T

    max_abs = float(np.max(np.abs(D))) or 1.0
    nnz_strict = int(np.count_nonzero(np.abs(D) > 1e-10))
    nnz_relative = int(np.count_nonzero(np.abs(D) > 1e-3 * max_abs))
    total_entries = (N0 + N1) ** 2

    # Row 0 (vertex 0's row). D has zero vertex-vertex and edge-edge blocks by
    # construction (off-diagonal block form), so the only nonzero entries in
    # row 0 are in the edge block -- report |D[0, edge]| against the graph
    # distance from vertex 0 to that edge's nearer endpoint, the same
    # distance axis H2 uses for D+=sqrt(L)'s row0_decay_by_graph_distance.
    def ring_distance(a: int, b: int) -> int:
        return min((a - b) % n, (b - a) % n)

    edge_dist_from_0 = [min(ring_distance(0, i), ring_distance(0, j)) for (i, j) in edges]
    decay_profile = {}
    for d in [0, 1, 2, 3, 10, 50, min(100, n - 1)]:
        vals_at_d = [abs(D[0, N0 + col]) for col, dist in enumerate(edge_dist_from_0) if dist == d]
        decay_profile[str(d)] = float(max(vals_at_d)) if vals_at_d else 0.0

    is_self_adjoint = bool(np.allclose(D, D.T))
    L0 = d1 @ d1.T
    up_term = d1.T @ d1
    D2 = D @ D
    squaring_holds = bool(
        np.allclose(D2[:N0, :N0], L0) and np.allclose(D2[N0:, N0:], up_term)
        and np.allclose(D2[:N0, N0:], 0) and np.allclose(D2[N0:, :N0], 0)
    )

    return {
        "claim_id": "H2B",
        "hypothesis": "H2B -- locality of the block-incidence Dirac operator D=[[0,d1],[d1^T,0]] "
                      "on the SAME graph H2 tested (independent of, and not overwriting, "
                      "H2-SPECTRAL-TRIPLE-LOCALITY=FAIL for D+=sqrt(L))",
        "test_graph": f"n={n} nearest-neighbour ring, k={k_neighbors} -- identical construction to H2",
        "n_triangles_available_as_2_cells": len(triangles),
        "D_self_adjoint": is_self_adjoint,
        "D_squared_equals_diag(L0,d1^T_d1)_exactly": squaring_holds,
        "D_sparsity_fraction_strict": nnz_strict / total_entries,
        "D_sparsity_fraction_relative_1e-3_of_max": nnz_relative / total_entries,
        "D_row0_decay_by_graph_distance_vertex_block": decay_profile,
        "comparison_to_H2_D_plus_sqrt_L": {
            "D_plus_sparsity_fraction_relative_1e-3_of_max_FROM_H2": "0.235 (23.5%), per H2's own recorded result",
            "D_block_sparsity_fraction_relative_1e-3_of_max_HERE": nnz_relative / total_entries,
            "interpretation": (
                "By construction (built directly from the local incidence matrix d1, never "
                "from spectral/functional calculus on L), D is exactly as sparse as d1 itself "
                "-- each nonzero entry connects a vertex to an edge it is literally an "
                "endpoint of, i.e. locality is exact and structural, not merely "
                "'improved relative to sqrt(L)'. This directly resolves the specific locality "
                "failure mode H2 found in D+=sqrt(L) (which was dense: 100% strict, 23.5% at "
                "the same 0.1%-of-peak threshold, with weight extending to graph-distance 50+)."
            ),
        },
        "what_this_DOES_NOT_establish": (
            "Locality alone does not make D a valid Dirac operator for a Standard-Model-type "
            "spectral triple. H2's other findings stand unchanged and apply equally here: the "
            "KO-dimension this construction naturally produces has not been shown to be 6 mod "
            "8 (the value the Chamseddine-Connes-Marcolli construction requires), and no "
            "algebra representation A, grading, or real structure J compatible with the "
            "first-order condition [[D,a],JbJ^-1]=0 has been constructed here or anywhere in "
            "the corpus. D2's D^2=diag(L0, d1^T d1) also only recovers the RESTRICTED "
            "(2-cell-omitting) Laplacian term, per simplicial.py::check_two_block_dirac_squaring "
            "-- see TFT-002 vs TFT-002B."
        ),
    }
