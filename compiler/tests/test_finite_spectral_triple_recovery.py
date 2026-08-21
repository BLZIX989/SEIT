"""Tests for compiler/backends/finite_spectral_triple_recovery.py."""
from __future__ import annotations

import numpy as np

from compiler.backends.finite_spectral_triple_recovery import (
    double_construction,
    pi_prime_representation,
    run_recovery_certification,
)


def test_all_axioms_hold_including_first_order_condition():
    r = run_recovery_certification()
    assert r.self_adjoint is True
    assert r.grading_squares_to_identity is True
    assert r.anticommutes_with_grading is True
    assert r.algebra_commutes_with_grading is True
    assert r.first_order_condition_holds_numeric is True
    assert r.first_order_residual_norm < 1e-9
    assert r.first_order_condition_holds_symbolic_general is True


def test_sign_variant_also_passes():
    r = run_recovery_certification()
    assert r.sign_variant_eps_minus1_also_passes_first_order is True


def test_real_structure_signs_are_plus_one_by_default():
    r = run_recovery_certification()
    assert (r.real_structure_epsilon, r.real_structure_epsilon_prime,
            r.real_structure_epsilon_doubleprime) == (1, 1, 1)


def test_minus_one_sign_convention_gives_minus_one_signs():
    # sign_eta=-1,sign_xi=+1 (an ASYMMETRIC sign choice in J) gives
    # (-1,-1,-1) -- the symmetric choice sign_eta=sign_xi=-1 instead
    # cancels back to (+1,+1,+1) (double negation), confirmed directly
    # against compiler/backends/finite_spectral_triple_recovery.py's own
    # scratch verification before this test was written.
    r = run_recovery_certification(sign_eta=-1, sign_xi=1)
    assert (r.real_structure_epsilon, r.real_structure_epsilon_prime,
            r.real_structure_epsilon_doubleprime) == (-1, -1, -1)
    assert r.first_order_condition_holds_numeric is True


def test_double_negative_sign_convention_cancels_back_to_plus_one():
    r = run_recovery_certification(sign_eta=-1, sign_xi=-1)
    assert (r.real_structure_epsilon, r.real_structure_epsilon_prime,
            r.real_structure_epsilon_doubleprime) == (1, 1, 1)


def test_algebra_acts_only_on_copy_one():
    build = double_construction(n=20, k_neighbors=2)
    N0, dim = build["N0"], build["dim"]
    f = np.ones(N0)
    piF = pi_prime_representation(f, N0, dim)
    assert np.allclose(piF[dim:, :], 0)
    assert np.allclose(piF[:, dim:], 0)


def test_original_undoubled_candidate_still_fails_first_order_condition():
    # Sanity check that this recovery module isn't accidentally testing
    # the same (already-failing) construction under a new name.
    from compiler.backends.finite_spectral_triple_candidate import (
        run_spectral_triple_certification,
    )
    original = run_spectral_triple_certification()
    assert original.first_order_condition_holds_numeric is False
