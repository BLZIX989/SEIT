"""Unit tests for the executed (not copied) Fisher-Rao and eigenvalue-
uniqueness demonstrations that back the two established rejections in
the FC-005 build command (section 7)."""
import numpy as np

from compiler.falsification.eigen_uniqueness import run_counterexample
from compiler.verification.fisher_information import (
    gaussian_family_fisher_matrix, run_fisher_lorentzian_obstruction_demo,
)


def test_gaussian_fisher_matrix_matches_known_closed_form():
    import sympy
    F = gaussian_family_fisher_matrix()
    sigma = sympy.symbols("sigma", positive=True)
    expected = sympy.Matrix([[1 / sigma ** 2, 0], [0, 2 / sigma ** 2]])
    assert sympy.simplify(F - expected) == sympy.zeros(2, 2)


def test_fisher_demo_confirms_psd_and_falsifies_lorentzian_identification():
    d = run_fisher_lorentzian_obstruction_demo()
    assert d.is_positive_semidefinite
    assert all(e >= 0 for e in d.numeric_eigenvalues_at_sigma1)


def test_eigen_uniqueness_counterexample_confirms_spectrum_insufficient():
    c = run_counterexample(n=3, n_trials=15, seed=1)
    assert c.matrices_differ
    assert c.n_confirmed >= 1
    assert c.spectra_match_max_residual < 1e-6


def test_eigen_uniqueness_larger_matrix():
    c = run_counterexample(n=4, n_trials=10, seed=2)
    assert c.n_confirmed == c.n_trials  # every trial should confirm it for generic Hermitian H
