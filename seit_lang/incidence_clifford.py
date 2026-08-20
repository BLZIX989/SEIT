"""Incidence/Clifford branch as executable `.seit` primitives (Phase 6):
registers B, L_A=BB^T, L_B=B^TB, D_B=[[0,B],[B^T,0]], and gamma (the
natural Z/2 grading) as separate, composable `.seit` primitives,
building on -- not modifying -- the already-verified construction in
scientific_corpus/derivation/dirac_candidates.py (H2B: block-incidence
Dirac locality test).

Why new functions here rather than editing dirac_candidates.py: that
module's own build_block_dirac_locality_test() is a single function
that builds a ring graph, forms d1 (called B here, per the brief's own
Phase 6 naming) and D=[[0,d1],[d1^T,0]] internally, and returns one
aggregate report dict -- there is no existing public, composable API for
"B alone", "L_A=BB^T alone", etc. to bind individually, and the brief's
Phase 6 explicitly wants B/L_A/L_B/D_B/gamma as SEPARATE executable
derivations a `.seit` program can build up step by step. Rather than
refactor an already-tested, already-reported module (H2B's existing
numeric claims in scientific_corpus/derivation/
INCIDENCE_CLIFFORD_RESULTS.json and its committed report must not
shift), this module implements the SAME incidence-matrix construction
(a signed vertex-edge matrix: B[i,col]=-1, B[j,col]=+1 for edge (i,j),
identical to dirac_candidates.py's d1) as small, separately callable,
separately tested functions, and ALSO exposes the existing
build_block_dirac_locality_test() unchanged as its own primitive
(h2b_block_dirac_report) so a `.seit` program can reach the full,
already-verified H2B result too.

`ring_incidence_matrix(n, k_neighbors)` builds B for the SAME
k-nearest-neighbour ring graph dirac_candidates.py's H2B test uses
(the same edge construction) -- a `.seit` program cannot yet express an
arbitrary edge list as a call argument (Phase 1's grammar has no
list-literal syntax, the same gap noted in seit_lang/primitives.py's
module docstring for a different function), so this is parameterized
the same honest way seit_lang.primitives.build_graph() is: by scalars
only, never by an arbitrary graph.

L_A (on vertices) and L_B (on edges) are both typed "Laplacian" -- the
.seit type system has no separate "up-Laplacian"/"line-graph-Laplacian"
type, and both are legitimately Laplacians in discrete Hodge theory
(symmetric PSD operators arising from a coboundary/incidence operator),
just acting on different chain spaces. This is a deliberate, documented
broadening, not an assumption that the two are interchangeable.

CAUTION, stated as plainly as the brief itself states it: `block_dirac`
returns an OPERATOR, not a verified Connes Dirac operator for a real
spectral triple. Its .seit return type is deliberately "Operator", not
"SpectralTriple" -- promoting it to SpectralTriple would require the
algebra representation, real structure J, and first-order condition
dirac_candidates.py's own "what_this_DOES_NOT_establish" section says
have not been constructed anywhere in this corpus. Nothing here changes
that; H2 (D+=sqrt(L), FAIL) and H2B (this D_B, locality holds but
spectral-triple status unresolved) both stand exactly as previously
recorded.
"""
from __future__ import annotations

import numpy as np

from scientific_corpus.derivation import dirac_candidates

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def _ring_edges(n: int, k_neighbors: int) -> list[tuple[int, int]]:
    """Identical construction to dirac_candidates.py's
    _build_h2_ring_graph + its own edge extraction -- a k-nearest-
    neighbour ring on n vertices."""
    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        for k in range(1, k_neighbors + 1):
            j = (i + k) % n
            edge = (min(i, j), max(i, j))
            if edge[0] != edge[1] and edge not in seen:
                seen.add(edge)
                edges.append(edge)
    return edges


def build_incidence_matrix(n: int, edges: list[tuple[int, int]]) -> np.ndarray:
    """B: signed vertex-edge incidence matrix, B[i,col]=-1, B[j,col]=+1
    for edge (i,j) -- identical construction to dirac_candidates.py's
    d1. Not itself bound as a .seit primitive (edges is a Python list,
    which `.seit` cannot yet express as a call argument) -- used
    internally by ring_incidence_matrix() and directly importable for
    Python-level use."""
    B = np.zeros((n, len(edges)))
    for col, (i, j) in enumerate(edges):
        B[i, col] = -1.0
        B[j, col] = 1.0
    return B


def ring_incidence_matrix(n: float, k_neighbors: float) -> np.ndarray:
    return build_incidence_matrix(int(n), _ring_edges(int(n), int(k_neighbors)))


def vertex_laplacian(B: np.ndarray) -> np.ndarray:
    """L_A = B B^T -- the vertex-space graph Laplacian recovered from
    the incidence matrix (a standard incidence-matrix identity: B B^T
    equals D-A for a simple graph; not independently re-derived here)."""
    return B @ B.T


def edge_laplacian(B: np.ndarray) -> np.ndarray:
    """L_B = B^T B -- the edge-space (up-)Laplacian."""
    return B.T @ B


def block_dirac(B: np.ndarray) -> np.ndarray:
    """D_B = [[0, B], [B^T, 0]] -- the block-incidence candidate Dirac
    operator (see module docstring's CAUTION)."""
    n, m = B.shape
    D = np.zeros((n + m, n + m))
    D[:n, n:] = B
    D[n:, :n] = B.T
    return D


def grading_operator(B: np.ndarray) -> np.ndarray:
    """gamma = diag(+1 on the n vertex rows, -1 on the m edge rows).
    Algebraically anticommutes with D_B EXACTLY ({gamma, D_B} = 0),
    verified numerically in this phase's tests, not assumed."""
    n, m = B.shape
    return np.diag(np.concatenate([np.ones(n), -np.ones(m)]))


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("ring_incidence_matrix", ["Scalar", "Scalar"], "IncidenceMatrix",
                      ring_incidence_matrix,
                      "seit_lang.incidence_clifford.ring_incidence_matrix (same construction as "
                      "scientific_corpus.derivation.dirac_candidates._build_h2_ring_graph)"),
    PrimitiveBinding("vertex_laplacian", ["IncidenceMatrix"], "Laplacian",
                      vertex_laplacian, "seit_lang.incidence_clifford.vertex_laplacian (L_A = B B^T)"),
    PrimitiveBinding("edge_laplacian", ["IncidenceMatrix"], "Laplacian",
                      edge_laplacian, "seit_lang.incidence_clifford.edge_laplacian (L_B = B^T B)"),
    PrimitiveBinding("block_dirac", ["IncidenceMatrix"], "Operator",
                      block_dirac,
                      "seit_lang.incidence_clifford.block_dirac (D_B = [[0,B],[B^T,0]]) -- NOT "
                      "asserted to be a verified Connes Dirac operator, see module docstring"),
    PrimitiveBinding("grading_operator", ["IncidenceMatrix"], "Operator",
                      grading_operator, "seit_lang.incidence_clifford.grading_operator (gamma)"),
    PrimitiveBinding("h2b_block_dirac_report", ["Scalar", "Scalar"], "Dataset",
                      lambda n, k: dirac_candidates.build_block_dirac_locality_test(int(n), int(k)),
                      "scientific_corpus.derivation.dirac_candidates.build_block_dirac_locality_test "
                      "(unchanged, existing H2B result)"),
]

INCIDENCE_CLIFFORD_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
INCIDENCE_CLIFFORD_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
