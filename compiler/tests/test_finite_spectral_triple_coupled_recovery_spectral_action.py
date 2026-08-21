"""Tests for compiler/backends/
finite_spectral_triple_coupled_recovery_spectral_action.py -- the
inner-fluctuation / finite-moment attempt over the coupled recovery
candidate, closing the CL-FINITE-TRIPLE-TO-SPECTRAL-ACTION wiring gap
this session's audit found."""
from __future__ import annotations

import numpy as np

from compiler.backends.finite_spectral_triple_coupled_recovery_spectral_action import (
    J_conjugate_matrix, compute_finite_moments, run_inner_fluctuation_certification,
    verify_J_conjugate_matrix,
)


def test_J_conjugate_matrix_matches_vector_level_definition():
    assert verify_J_conjugate_matrix(dim=50, seed=0) is True
    assert verify_J_conjugate_matrix(dim=50, seed=7) is True


def test_J_conjugate_matrix_is_an_involution_on_self_adjoint_input():
    rng = np.random.default_rng(3)
    dim = 20
    A = rng.standard_normal((2 * dim, 2 * dim)) + 1j * rng.standard_normal((2 * dim, 2 * dim))
    M = A + A.conj().T  # self-adjoint, full (2*dim)x(2*dim) operator on the doubled space
    once = J_conjugate_matrix(M, dim)
    twice = J_conjugate_matrix(once, dim)
    assert np.allclose(twice, M)


def test_inner_fluctuation_is_well_posed():
    r = run_inner_fluctuation_certification()
    assert r.J_conjugate_matrix_verified is True
    assert r.omega_self_adjoint is True
    assert r.D_A_self_adjoint is True
    assert r.D_A_anticommutes_with_grading is True
    assert r.well_posed is True


def test_real_structure_epsilon_prime_measured_not_assumed():
    r = run_inner_fluctuation_certification()
    assert r.real_structure_epsilon_prime_used == 1


def test_omega_B_is_genuinely_nonzero_and_self_adjoint():
    r = run_inner_fluctuation_certification()
    assert r.Omega_B_is_zero is False
    assert r.Omega_B_self_adjoint is True
    assert r.Omega_B_max_abs > 0


def test_finite_moments_are_real_valued_to_float_precision():
    report = compute_finite_moments()
    assert report.well_posed is True
    assert set(report.moments) == {"a0''", "a2''", "a4''", "a6''"}
    for entry in report.moments.values():
        assert abs(entry["imag_residual"]) < 1e-8


def test_finite_moments_are_not_claimed_as_physical():
    report = compute_finite_moments()
    assert report.physical_interpretation is None


def test_zeroth_moment_equals_operator_dimension():
    report = compute_finite_moments()
    # Tr(D_A''^0) = Tr(Identity) = dimension of the doubled candidate.
    assert report.moments["a0''"]["value"] == 2 * 1400.0
