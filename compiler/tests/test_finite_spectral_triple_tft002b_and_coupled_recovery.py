"""Tests for compiler/backends/finite_spectral_triple_tft002b.py and
compiler/backends/finite_spectral_triple_recovery_coupled.py (Phase 1/2
of the 3-block-substrate + nontrivial-coupling recovery)."""
from __future__ import annotations

from compiler.backends.finite_spectral_triple_recovery_coupled import (
    run_coupled_recovery_certification,
)
from compiler.backends.finite_spectral_triple_tft002b import evaluate_tft002b


def test_tft002b_all_invariants_hold_at_full_scale():
    r = evaluate_tft002b()
    assert r.self_adjoint is True
    assert r.grading_squares_to_identity is True
    assert r.anticommutes_with_grading is True
    assert r.squares_to_full_hodge_laplacian is True


def test_tft002b_genuinely_differs_from_2block_operator():
    r = evaluate_tft002b()
    assert r.n_triangles == 600
    assert r.edge_block_differs_from_2block_up_term is True
    assert r.edge_block_max_abs_difference > 0


def test_tft002b_promoted_given_all_invariants_hold():
    r = evaluate_tft002b()
    assert r.promote_to_canonical is True


def test_coupled_recovery_all_axioms_hold_to_machine_precision():
    r = run_coupled_recovery_certification()
    assert r.self_adjoint is True
    assert r.grading_squares_to_identity is True
    assert r.anticommutes_with_grading is True
    assert r.algebra_commutes_with_grading is True
    assert r.first_order_condition_holds_numeric is True
    assert r.first_order_residual_norm < 1e-15
    assert r.first_order_condition_holds_symbolic_general is True


def test_coupling_is_genuinely_nonzero_and_not_proportional():
    r = run_coupled_recovery_certification()
    assert r.coupling_is_nonzero is True
    assert r.coupling_is_not_proportional_to_D is True
    assert r.coupling_anticommutes_with_grading is True


def test_coupled_signs_are_uniform_plus_one():
    r = run_coupled_recovery_certification()
    assert (r.real_structure_epsilon, r.real_structure_epsilon_prime,
            r.real_structure_epsilon_doubleprime) == (1, 1, 1)
