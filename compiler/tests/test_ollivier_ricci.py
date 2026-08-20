"""Tests for compiler/backends/ollivier_ricci.py -- the discrete curvature
backend behind CL-OPERATOR-TO-CURVATURE-DISCRETE. These check the actual
mathematics, not just wiring: the primal/dual LP duality gap, and hand-
computable cases verified against the definition directly (not just
against the code's own internal consistency).
"""
from __future__ import annotations

import numpy as np

from compiler.backends.graph_laplacian import build_graph
from compiler.backends.ollivier_ricci import ollivier_ricci_curvature


def test_primal_dual_duality_gap_is_near_zero_across_topologies():
    """Strong LP duality guarantees the primal transportation LP and its
    Kantorovich-Rubinstein dual must agree exactly for a correct
    implementation; a real gap here would mean a bug, not a finding."""
    for topology, n in [("cycle", 6), ("cycle", 12), ("path", 10),
                         ("complete", 5), ("star", 7), ("grid2d", 4)]:
        g = build_graph(topology, n)
        r = ollivier_ricci_curvature(g)
        assert r.max_duality_gap < 1e-6, f"{g.label}: duality gap {r.max_duality_gap}"


def test_path_interior_edge_curvature_hand_verified():
    """path(n=4): vertices 0-1-2-3, edge (1,2). m_1 uniform over {0,2},
    m_2 uniform over {1,3}. By 1D optimal-transport sorting, the optimal
    coupling pairs 0->1 and 2->3, both distance 1, so W1=1 and
    kappa = 1 - 1/1 = 0 -- verified here against a value computed by hand
    from the definition, not against the code's own other outputs."""
    g = build_graph("path", 4)
    r = ollivier_ricci_curvature(g)
    edge12 = next(e for e in r.edge_curvatures if {e.u, e.v} == {1, 2})
    assert abs(edge12.kappa - 0.0) < 1e-9
    assert abs(edge12.w1_primal - 1.0) < 1e-9


def test_star_leaf_edge_curvature_hand_verified():
    """star(n=8): center=0, leaves 1..7. Edge (0,1): m_0 uniform over all
    7 leaves, m_1 = point mass at {0}. Every leaf is distance 1 from the
    center, so W1 = sum_i (1/7)*1 = 1, and kappa = 1 - 1/1 = 0 -- again
    checked against the definition by hand, not the code's self-consistency."""
    g = build_graph("star", 8)
    r = ollivier_ricci_curvature(g)
    edge01 = next(e for e in r.edge_curvatures if {e.u, e.v} == {0, 1})
    assert abs(edge01.kappa - 0.0) < 1e-9
    assert abs(edge01.w1_primal - 1.0) < 1e-9


def test_triangle_has_positive_curvature():
    """cycle(n=3) is a triangle: each vertex's only neighbors are the
    other two, so the random-walk measures at any two adjacent vertices
    already share substantial mass -- established qualitative fact that
    triangles/short cycles show positive Ollivier-Ricci curvature due to
    this clustering effect (Ollivier 2009; Jost-Liu 2014)."""
    g = build_graph("cycle", 3)
    r = ollivier_ricci_curvature(g)
    assert all(e.kappa > 0 for e in r.edge_curvatures)


def test_curvature_is_isomorphism_invariant():
    """The sorted multiset of edge-curvature values must be identical
    under any relabeling of the graph's vertices -- curvature depends
    only on graph structure, not on how vertices happen to be indexed."""
    g = build_graph("cycle", 10)
    base = tuple(sorted(round(e.kappa, 8) for e in ollivier_ricci_curvature(g).edge_curvatures))
    rng = np.random.default_rng(3)
    for _ in range(3):
        perm = rng.permutation(g.n)
        remap = {old: int(new) for old, new in zip(range(g.n), perm)}
        from compiler.backends.graph_laplacian import Graph
        g2 = Graph(topology=g.topology, n=g.n, seed=g.seed, nodes=list(range(g.n)),
                   edges=[(remap[i], remap[j]) for i, j in g.edges])
        relabeled = tuple(sorted(round(e.kappa, 8) for e in ollivier_ricci_curvature(g2).edge_curvatures))
        assert relabeled == base


def test_complete_graph_more_positively_curved_than_cycle():
    """A dense/complete graph should show markedly higher mean curvature
    than a sparse cycle of comparable size -- established qualitative
    behavior (denser local connectivity => more positive curvature)."""
    cycle = ollivier_ricci_curvature(build_graph("cycle", 6))
    complete = ollivier_ricci_curvature(build_graph("complete", 6))
    assert complete.mean_kappa > cycle.mean_kappa
