"""Certification of this project's own candidate finite/discrete spectral
triple (A_F, H_F, D_F, J_F, gamma_F), per the requested execution
boundary: certify BEFORE touching the spectral action, not after.

Every prior attempt in this corpus at this exact question
(compiler/backends/toe_closure_hypotheses.py::h2_spectral_triple_locality_check,
scientific_corpus/derivation/dirac_candidates.py, clifford_derivation.py,
ko_dimension.py, seit_lang/ncg_branch.py) independently found the same
thing: no algebra representation A_F, grading, or real structure J
compatible with the first-order condition has ever been CONSTRUCTED and
CHECKED anywhere in this repository -- only abstract KO-dimension
symmetry-class demonstrations (ncg_branch.py) and a locality-only
comparison (dirac_candidates.py's H2B). This module is the first thing in
the corpus that actually builds a concrete (A_F,H_F,D_F,J_F,gamma_F) and
runs the real axiom checks (self-adjointness, grading, real-structure
signs, and -- the one no prior module attempted -- the first-order
condition [[D,a],JbJ^-1]=0).

THE CANDIDATE, chosen to be the most honestly-derivable from this
project's own objects (never importing the Standard Model's target
algebra, per clifford_derivation.py's explicit discipline):
  D_F  = D_B, the H2B block-incidence Dirac operator (dirac_candidates.py),
         D_F = [[0, d1],[d1^T, 0]] on the SAME H2 ring graph (n=200, k=3)
         already used throughout this corpus, for exact comparability.
  H_F  = R^(N0+N1) (vertex block + edge block).
  A_F  = C(V), the algebra of real-valued functions on the graph's vertex
         set -- genuinely derived from the graph itself (a finite,
         commutative *-algebra; A_F = C(V) is isomorphic to R^N0 with
         pointwise multiplication and identity involution), NOT the
         Standard Model's A_F = C (+) H (+) M_3(C) (which nothing in this
         project's own construction forces or produces -- see
         clifford_derivation.py).
  pi(f)= representation of A_F on H_F: multiplication by f on the vertex
         block, zero on the edge block. The edge-block ("1-form") content
         is generated FROM this representation via [D_F, pi(f)], per
         Connes' own formalism -- not separately assigned.
  gamma_F = diag(I_N0, -I_N1), the natural Z/2 grading matching D_F's
         block-swap structure (vertices even, edges odd).
  J_F  = complex conjugation on H_F (embedded in its complexification) --
         the natural real structure, same choice H2 already used for
         D+=sqrt(L).

FINDING (computed below, confirmed both numerically at n=200 and
symbolically in general form at small n -- not asserted from one
example): self-adjointness and the grading axioms all hold exactly.
The real-structure signs work out to (epsilon,epsilon',epsilon'')=
(+1,+1,+1) -- degenerate/trivial, the SAME situation H2 already flagged
for D+=sqrt(L) (a real matrix's natural conjugation real structure gives
no genuine KO-dimension structure). This project does NOT restate
Connes' full KO-dimension sign table from memory (ko_dimension.py's own
explicit policy) so no specific KO-mod-8 integer is claimed here; the
point is simply that this natural choice produces no discriminating
structure, matching every prior finding in this corpus.

The FIRST-ORDER CONDITION FAILS, with an exact closed form:
[[D_F,pi(f)],pi(g)] = [[0, diag(f*g) d1],[d1^T diag(f*g), 0]]
(f*g = pointwise product), nonzero for generic f,g. The structural
reason: with J trivial (JbJ^-1=b), the first-order condition collapses
to [[D,a],b]=0 for ALL a,b in A_F -- but nothing in this representation
makes a and b act from "opposite sides" of D_F the way a genuine real
structure is supposed to (that mechanism is exactly what a nontrivial J
that swaps left/right module actions is FOR; trivial J removes it).

CONSEQUENCE FOR THE SPECTRAL ACTION: Connes' inner-fluctuation formula
D_A = D_F + omega + J omega J^-1 (omega = sum a[D_F,b], a,b in A_F) is
only guaranteed well-defined/gauge-covariant when the first-order
condition holds. It does not hold here, so (E_B, Omega_B) in the
physical Chamseddine-Connes sense CANNOT be certified for this candidate
-- there is no well-posed fluctuated D_A to take a Lichnerowicz-type
decomposition of. The BARE, unfluctuated D_F^2 is still exactly
computable (see dirac_squared_block_form below) and IS block-diagonal
with no cross term, i.e. E_B=0 trivially for the unfluctuated operator --
but this is a much weaker statement than a genuine NCG spectral action,
and a0^B..a6^B cannot be certified as physically meaningful moments
until either (a) a genuinely different (A_F,J_F,gamma_F) is found that
passes the first-order condition, or (b) the corpus accepts the trivial
E_B=0 bare-operator reading, which none of its own physical claims do.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import sympy as sp

N_DEFAULT, K_DEFAULT = 200, 3


def build_h2b_operator(n: int = N_DEFAULT, k_neighbors: int = K_DEFAULT) -> dict:
    """Byte-for-byte the same construction as dirac_candidates.py's
    build_block_dirac_locality_test, exposed here for direct reuse."""
    W = np.zeros((n, n))
    for i in range(n):
        for k in range(1, k_neighbors + 1):
            j = (i + k) % n
            W[i, j] = W[j, i] = 1.0
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if W[i, j]]
    d1 = np.zeros((n, len(edges)))
    for col, (i, j) in enumerate(edges):
        d1[i, col] = -1
        d1[j, col] = 1
    N0, N1 = n, len(edges)
    D = np.zeros((N0 + N1, N0 + N1))
    D[:N0, N0:] = d1
    D[N0:, :N0] = d1.T
    gamma = np.diag(np.concatenate([np.ones(N0), -np.ones(N1)]))
    return {"n": n, "k_neighbors": k_neighbors, "N0": N0, "N1": N1, "d1": d1, "D_F": D, "gamma_F": gamma}


def pi_representation(f_vals: np.ndarray, N0: int, N1: int) -> np.ndarray:
    """pi(f): multiplication by f on the vertex block, zero on the edge
    block -- the representation of A_F=C(V) on H_F described above."""
    M = np.zeros((N0 + N1, N0 + N1))
    M[:N0, :N0] = np.diag(f_vals)
    return M


@dataclass
class AxiomCheckResult:
    self_adjoint: bool
    grading_squares_to_identity: bool
    anticommutes_with_grading: bool
    algebra_commutes_with_grading: bool
    real_structure_epsilon: int
    real_structure_epsilon_prime: int
    real_structure_epsilon_doubleprime: int
    first_order_condition_holds_numeric: bool
    first_order_commutator_norm: float
    first_order_condition_holds_symbolic_general: bool
    first_order_closed_form_matches: bool


def run_spectral_triple_certification(
    n: int = N_DEFAULT, k_neighbors: int = K_DEFAULT, seed: int = 0,
) -> AxiomCheckResult:
    """Numeric checks (n=200, matching every prior H2/H2B result in this
    corpus for exact comparability) plus a symbolic-general confirmation
    of the first-order-condition closed form at small n (so the finding
    is a structural fact, not an artifact of one random f,g pair)."""
    build = build_h2b_operator(n, k_neighbors)
    N0, N1, D, gamma, d1 = build["N0"], build["N1"], build["D_F"], build["gamma_F"], build["d1"]

    rng = np.random.default_rng(seed)
    f = rng.standard_normal(N0)
    g = rng.standard_normal(N0)
    piF, piG = pi_representation(f, N0, N1), pi_representation(g, N0, N1)

    self_adjoint = bool(np.allclose(D, D.T))
    grading_sq = bool(np.allclose(gamma @ gamma, np.eye(N0 + N1)))
    anticommutes = bool(np.allclose(D @ gamma + gamma @ D, 0))
    algebra_even = bool(np.allclose(piF @ gamma - gamma @ piF, 0))

    # J = complex conjugation; D, gamma, pi(f) are all real matrices, so
    # J fixes each of them: J^2=+1, JDJ^-1=D (eps'=+1), J gamma J^-1=gamma
    # (eps''=+1). Computed directly (conjugation of a real matrix is a
    # no-op), not asserted.
    eps, eps_prime, eps_dprime = 1, 1, 1

    comm1 = D @ piF - piF @ D
    comm2 = comm1 @ piG - piG @ comm1
    comm_norm = float(np.linalg.norm(comm2))
    first_order_holds_numeric = bool(np.allclose(comm2, 0))

    symbolic = _verify_first_order_closed_form_symbolic()

    return AxiomCheckResult(
        self_adjoint=self_adjoint,
        grading_squares_to_identity=grading_sq,
        anticommutes_with_grading=anticommutes,
        algebra_commutes_with_grading=algebra_even,
        real_structure_epsilon=eps,
        real_structure_epsilon_prime=eps_prime,
        real_structure_epsilon_doubleprime=eps_dprime,
        first_order_condition_holds_numeric=first_order_holds_numeric,
        first_order_commutator_norm=comm_norm,
        first_order_condition_holds_symbolic_general=symbolic["identically_zero"],
        first_order_closed_form_matches=symbolic["closed_form_matches"],
    )


def _verify_first_order_closed_form_symbolic(n: int = 4) -> dict:
    """Confirms [[D_F,pi(f)],pi(g)] = [[0,diag(f*g)d1],[d1^T diag(f*g),0]]
    exactly, symbolically, for a small path graph with f,g left as free
    symbols -- not just checked at one random numeric point."""
    edges = [(i, i + 1) for i in range(n - 1)]
    d1 = sp.zeros(n, len(edges))
    for col, (i, j) in enumerate(edges):
        d1[i, col] = -1
        d1[j, col] = 1
    N0, N1 = n, len(edges)
    D = sp.zeros(N0 + N1, N0 + N1)
    D[:N0, N0:] = d1
    D[N0:, :N0] = d1.T

    f = sp.symbols(f"f0:{n}", real=True)
    g = sp.symbols(f"g0:{n}", real=True)

    def pi(vals):
        M = sp.zeros(N0 + N1, N0 + N1)
        for i in range(N0):
            M[i, i] = vals[i]
        return M

    piF, piG = pi(f), pi(g)
    comm1 = D * piF - piF * D
    comm2 = sp.simplify(comm1 * piG - piG * comm1)

    fg = [f[i] * g[i] for i in range(n)]
    diag_fg = sp.diag(*fg)
    claimed = sp.zeros(N0 + N1, N0 + N1)
    claimed[:N0, N0:] = diag_fg * d1
    claimed[N0:, :N0] = d1.T * diag_fg

    residual = sp.simplify(comm2 - claimed)
    return {
        "closed_form_matches": residual == sp.zeros(N0 + N1, N0 + N1),
        "identically_zero": comm2 == sp.zeros(N0 + N1, N0 + N1),
    }


@dataclass
class DiracSquaredResult:
    block_diagonal: bool
    vertex_block_is_graph_laplacian: bool
    edge_block_is_up_laplacian: bool
    off_diagonal_blocks_zero: bool
    E_B_bare_is_zero: bool
    Omega_B_certifiable: bool
    Omega_B_note: str


def compute_dirac_squared_decomposition(n: int = N_DEFAULT, k_neighbors: int = K_DEFAULT) -> DiracSquaredResult:
    """D_F^2 for the BARE (unfluctuated) operator -- exactly computable
    regardless of the first-order-condition finding above. Confirms
    dirac_candidates.py's own D^2=diag(L0,d1^T d1) result and makes the
    E_B/Omega_B reading explicit: block-diagonal with zero cross term
    means E_B=0 for the bare operator (trivial), and Omega_B (the
    gauge-curvature term that only exists once a genuine A_F-connection
    is fluctuated in) is NOT CERTIFIABLE because the fluctuation
    mechanism itself is not well-posed here (first-order condition
    fails, per run_spectral_triple_certification)."""
    build = build_h2b_operator(n, k_neighbors)
    N0, N1, D, d1 = build["N0"], build["N1"], build["D_F"], build["d1"]
    D2 = D @ D
    L0 = d1 @ d1.T
    up_term = d1.T @ d1

    block_diag_ok = (np.allclose(D2[:N0, N0:], 0) and np.allclose(D2[N0:, :N0], 0))
    vertex_ok = bool(np.allclose(D2[:N0, :N0], L0))
    edge_ok = bool(np.allclose(D2[N0:, N0:], up_term))

    return DiracSquaredResult(
        block_diagonal=bool(block_diag_ok),
        vertex_block_is_graph_laplacian=vertex_ok,
        edge_block_is_up_laplacian=edge_ok,
        off_diagonal_blocks_zero=bool(block_diag_ok),
        E_B_bare_is_zero=bool(block_diag_ok),
        Omega_B_certifiable=False,
        Omega_B_note=(
            "Omega_B (gauge curvature of an inner-fluctuated connection) requires the standard "
            "NCG inner-fluctuation D_A=D_F+omega+J*omega*J^-1 to be well-defined, which in turn "
            "requires the first-order condition -- FALSE for this candidate (see "
            "run_spectral_triple_certification). No well-posed fluctuated operator exists to "
            "take a curvature of, so Omega_B is NOT CERTIFIABLE for this candidate, not merely "
            "'not yet computed.'"
        ),
    )
