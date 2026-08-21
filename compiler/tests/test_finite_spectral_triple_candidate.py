"""Tests for compiler/backends/finite_spectral_triple_candidate.py."""
from __future__ import annotations

from compiler.backends.finite_spectral_triple_candidate import (
    compute_dirac_squared_decomposition,
    run_spectral_triple_certification,
)


def test_trivial_axioms_all_hold():
    r = run_spectral_triple_certification()
    assert r.self_adjoint is True
    assert r.grading_squares_to_identity is True
    assert r.anticommutes_with_grading is True
    assert r.algebra_commutes_with_grading is True


def test_real_structure_signs_are_degenerate():
    r = run_spectral_triple_certification()
    assert (r.real_structure_epsilon, r.real_structure_epsilon_prime,
            r.real_structure_epsilon_doubleprime) == (1, 1, 1)


def test_first_order_condition_fails_numeric():
    r = run_spectral_triple_certification()
    assert r.first_order_condition_holds_numeric is False
    assert r.first_order_commutator_norm > 1.0  # not numerical noise


def test_first_order_condition_fails_symbolic_general():
    # The structural finding, not an artifact of one random f,g pair.
    r = run_spectral_triple_certification()
    assert r.first_order_closed_form_matches is True
    assert r.first_order_condition_holds_symbolic_general is False


def test_first_order_condition_holds_for_degenerate_fg_product():
    # Sanity check on the closed form itself: if f*g=0 everywhere, the
    # commutator SHOULD vanish -- confirms the closed form is really
    # being computed, not a constant "always fails" stub.
    import numpy as np

    from compiler.backends.finite_spectral_triple_candidate import (
        build_h2b_operator, pi_representation,
    )
    build = build_h2b_operator(n=20, k_neighbors=2)
    N0, N1, D = build["N0"], build["N1"], build["D_F"]
    f = np.zeros(N0)
    f[:10] = 1.0
    g = np.zeros(N0)
    g[10:] = 1.0  # disjoint support from f -- f*g == 0 everywhere
    piF, piG = pi_representation(f, N0, N1), pi_representation(g, N0, N1)
    comm1 = D @ piF - piF @ D
    comm2 = comm1 @ piG - piG @ comm1
    assert np.allclose(comm2, 0)


def test_dirac_squared_is_block_diagonal_bare_E_B_zero():
    d2 = compute_dirac_squared_decomposition()
    assert d2.block_diagonal is True
    assert d2.vertex_block_is_graph_laplacian is True
    assert d2.edge_block_is_up_laplacian is True
    assert d2.E_B_bare_is_zero is True


def test_omega_B_honestly_not_certifiable():
    d2 = compute_dirac_squared_decomposition()
    assert d2.Omega_B_certifiable is False
    assert "first-order condition" in d2.Omega_B_note.lower()
