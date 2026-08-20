"""Explicit, exact (sympy, integer/rational arithmetic -- no floating-point
approximation) simplicial-complex construction: boundary operators,
Hodge Laplacians, and the discrete Dirac-squaring identity from SEIT-6 /
"This from That" section 5.

This module tests TFT-002 and TFT-003 (see TFT_BRIDGE_THEOREMS.md): the
part of the Cartan/Weitzenböck chain that is pure linear algebra on
explicitly constructed matrices, hence exactly computable, as distinct
from the part (the discrete Lie derivative L_e along a specific
combinatorial vector field) that is NOT computable from any definition
actually given in the corpus -- see WEITZENBOCK_CURVATURE_TERM below.
"""
from __future__ import annotations

import sympy as sp


class SimplicialComplex:
    """A finite abstract simplicial complex given explicitly by its vertex,
    edge, and (optionally) triangle sets. Orientations: an edge (i,j) with
    i<j is oriented i->j; a triangle (i,j,k) with i<j<k is oriented
    consistently with its three boundary edges."""

    def __init__(self, n_vertices: int, edges: list[tuple[int, int]],
                 triangles: list[tuple[int, int, int]] | None = None):
        self.n_vertices = n_vertices
        self.edges = sorted(tuple(sorted(e)) for e in edges)
        self.triangles = sorted(tuple(sorted(t)) for t in (triangles or []))
        self.edge_index = {e: i for i, e in enumerate(self.edges)}

    def boundary_1(self) -> sp.Matrix:
        """d1: C1 -> C0. Column for edge (i,j), i<j: -1 at row i, +1 at row j."""
        m = sp.zeros(self.n_vertices, len(self.edges))
        for col, (i, j) in enumerate(self.edges):
            m[i, col] = -1
            m[j, col] = 1
        return m

    def boundary_2(self) -> sp.Matrix:
        """d2: C2 -> C1. Column for triangle (i,j,k), i<j<k:
        boundary = edge(j,k) - edge(i,k) + edge(i,j)."""
        m = sp.zeros(len(self.edges), len(self.triangles))
        for col, (i, j, k) in enumerate(self.triangles):
            m[self.edge_index[(j, k)], col] += 1
            m[self.edge_index[(i, k)], col] += -1
            m[self.edge_index[(i, j)], col] += 1
        return m

    def graph_laplacian(self) -> sp.Matrix:
        d1 = self.boundary_1()
        return d1 * d1.T

    def hodge_laplacian_1(self) -> sp.Matrix:
        d1, d2 = self.boundary_1(), self.boundary_2()
        return d1.T * d1 + d2 * d2.T

    def hodge_laplacian_2(self) -> sp.Matrix:
        d2 = self.boundary_2()
        return d2.T * d2


def check_chain_complex_identity(K: SimplicialComplex) -> dict:
    """d1 . d2 = 0 -- the defining identity of a chain complex. Exact
    symbolic check, not numerical tolerance."""
    d1, d2 = K.boundary_1(), K.boundary_2()
    product = d1 * d2
    holds = product == sp.zeros(*product.shape)
    return {"claim": "d1 . d2 = 0 (chain complex identity)", "holds_exactly": bool(holds),
            "d1_shape": list(d1.shape), "d2_shape": list(d2.shape)}


def check_two_block_dirac_squaring(K: SimplicialComplex) -> dict:
    """TFT-002: the SPECIFIC construction in SEIT-6 / This-from-That 5.1:
    D = [[0, d1],[d1^T, 0]] acting on C0 (+) C1. Claim (SEIT-6, verbatim):
    D^2 = diag(L0, d1^T d1) exactly. This is pure linear algebra on
    explicit matrices -- exactly checkable, no approximation."""
    d1 = K.boundary_1()
    n0, n1 = K.n_vertices, len(K.edges)
    D = sp.zeros(n0 + n1, n0 + n1)
    D[:n0, n0:] = d1
    D[n0:, :n0] = d1.T
    D2 = D * D
    L0 = d1 * d1.T
    up_term = d1.T * d1  # NOT the full Hodge Laplacian L1 unless there are no 2-cells
    expected = sp.diag(L0, up_term)
    holds = D2 == expected
    is_symmetric = D == D.T
    return {
        "claim": "TFT-002: D=[[0,d1],[d1^T,0]] satisfies D^2 = diag(L0, d1^T d1) exactly "
                 "(This from That section 5.1, SEIT-6)",
        "holds_exactly": bool(holds),
        "D_is_self_adjoint_real_symmetric": bool(is_symmetric),
        "note": "d1^T d1 equals the FULL edge-space Hodge Laplacian L1 = d1^T d1 + d2 d2^T "
                "only when the complex has no 2-cells (d2 is the zero map / empty). When "
                "2-cells exist, this two-block Dirac's square omits the d2 d2^T ('up') "
                "term entirely -- it is not wrong as literally stated in SEIT-6, but it is "
                "a restricted special case, not the operator whose square is the full "
                "graded Hodge Laplacian.",
    }


def check_three_block_hodge_dirac_squaring(K: SimplicialComplex) -> dict:
    """TFT-002B (new claim ID, not a merge with TFT-002): the STANDARD
    discrete-exterior-calculus Hodge-Dirac operator D = d + delta, written
    in block form over C0 (+) C1 (+) C2 as
        D = [[0, d1, 0], [d1^T, 0, d2], [0, d2^T, 0]]
    This is external, established mathematics (discrete exterior calculus;
    e.g. Horak & Jost 2013, cited directly in the Universal Rosetta Vol.4
    Ch.23 text this project already read), not a This-from-That-specific
    claim. Its square gives the FULL graded Hodge Laplacian diag(L0,L1,L2)
    -- tested here exactly on the same complex used for TFT-002, to make
    the restricted-vs-full distinction concrete rather than asserted."""
    d1, d2 = K.boundary_1(), K.boundary_2()
    n0, n1, n2 = K.n_vertices, len(K.edges), len(K.triangles)
    N = n0 + n1 + n2
    D = sp.zeros(N, N)
    D[:n0, n0:n0 + n1] = d1
    D[n0:n0 + n1, :n0] = d1.T
    D[n0:n0 + n1, n0 + n1:] = d2
    D[n0 + n1:, n0:n0 + n1] = d2.T
    D2 = D * D
    L0 = d1 * d1.T
    L1 = d1.T * d1 + d2 * d2.T
    L2 = d2.T * d2
    expected = sp.diag(L0, L1, L2)
    holds = D2 == expected
    return {
        "claim": "TFT-002B: the standard (established, external) 3-graded Hodge-Dirac "
                 "operator D=d+delta satisfies D^2 = diag(L0,L1,L2) exactly on a complex "
                 "with nonempty 2-cells",
        "external_established_mathematics": True,
        "holds_exactly": bool(holds),
        "n_triangles_in_test_complex": n2,
    }


WEITZENBOCK_CURVATURE_TERM = {
    "claim": "This from That section 5.2's antisymmetric/curvature term: "
             "R_ab = iota_{e_a} L_{e_b} - iota_{e_b} L_{e_a}, requiring a discrete "
             "directional Lie derivative L_e along a specific combinatorial vector field e",
    "status": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS",
    "missing_object": (
        "A concrete combinatorial definition of the discrete Lie derivative operator "
        "L_e (as a matrix/operator on cochains) for a specific choice of discrete vector "
        "field e on the simplicial complex, satisfying Cartan's formula L_e = d.iota_e + "
        "iota_e.d by construction (not merely asserted). This-from-That section 5.1 states "
        "the desired adjoint relations (<d a,b> = <a, delta b>, (e^.)^dagger = iota_e) and "
        "'evaluates the inner product sum over arbitrary test cochains' to arrive at the "
        "Cartan identity, but never gives L_e, iota_e, or the vector field e as explicit "
        "matrices/maps on a concrete complex the way d1 and d2 are given here -- so this "
        "half of the claimed derivation cannot be independently re-run; it can only be "
        "re-run once a specific discrete vector-field/Lie-derivative construction (several "
        "exist in the discrete exterior calculus literature, e.g. Desbrun-Hirani-Leok-"
        "Marsden's flat/sharp-operator-based discrete Lie derivative) is chosen and cited "
        "as the definition actually being used."
    ),
    "what_IS_computable_and_was_computed_instead": (
        "The symmetric term of the same Weitzenbock decomposition (the D^2 = diag(L0, L1) "
        "identity for the full 3-graded Hodge-Dirac operator) requires no Lie derivative at "
        "all -- it is pure boundary-operator algebra, and is verified exactly above "
        "(TFT-002B)."
    ),
}
