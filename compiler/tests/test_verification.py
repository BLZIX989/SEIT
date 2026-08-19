import numpy as np
import sympy

from compiler.verification.verify import numeric_verify, sweep_verify, symbolic_verify


def test_symbolic_verify_passes_for_identity():
    x = sympy.symbols("x")
    r = symbolic_verify((x + 1) ** 2, x**2 + 2 * x + 1, test="binomial expansion")
    assert r.passed
    assert r.precision == "exact"


def test_symbolic_verify_fails_for_nonequal():
    x = sympy.symbols("x")
    r = symbolic_verify(x + 1, x + 2, test="broken identity")
    assert not r.passed


def test_numeric_verify_within_tolerance():
    r = numeric_verify(np.array([1.0, 2.0]), np.array([1.0 + 1e-12, 2.0]), test="close", tolerance=1e-9)
    assert r.passed


def test_numeric_verify_outside_tolerance_fails():
    r = numeric_verify(np.array([1.0]), np.array([1.1]), test="far", tolerance=1e-9)
    assert not r.passed
    assert r.residual > 0


def test_sweep_verify_fails_if_any_case_fails():
    good = numeric_verify(1.0, 1.0, test="a", tolerance=1e-9)
    bad = numeric_verify(1.0, 2.0, test="b", tolerance=1e-9)
    agg = sweep_verify("sweep", [good, bad])
    assert not agg.passed
    assert agg.details["n_passed"] == 1
