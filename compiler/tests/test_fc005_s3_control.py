"""FC-005 build command section 21, items 1-4: S^3 spectral spectrum,
heat trace, coefficient extraction, curvature residual. This is the
mandatory regression test that must pass before any DESI work."""
import numpy as np

from compiler.backends.heat_kernel_sphere import (
    EXACT_A0, EXACT_A1, EXACT_A2, EXACT_KAPPA, EXACT_R,
    fit_window, heat_trace, run_s3_control, s3_spectrum,
)


def test_s3_spectrum_closed_form():
    lam, mult = s3_spectrum(5)
    assert lam.tolist() == [0, 3, 8, 15, 24, 35]  # l(l+2) for l=0..5
    assert mult.tolist() == [1, 4, 9, 16, 25, 36]  # (l+1)^2


def test_s3_heat_trace_positive_and_decreasing():
    lam, mult = s3_spectrum(2000)
    ts = np.array([0.01, 0.1, 1.0])
    K = heat_trace(ts, lam, mult)
    assert np.all(K > 0)
    assert np.all(np.diff(K) < 0)  # heat trace decreases with t


def test_s3_curvature_identities_exact_reference():
    # DC-014/DC-015/DC-016/DC-017: R=6*kappa, a0=V, a1=V*kappa, a2=0.5*V*kappa^2
    V = EXACT_A0
    assert abs(EXACT_R - 6 * EXACT_KAPPA) < 1e-12
    assert abs(EXACT_A1 - V * EXACT_KAPPA) < 1e-12
    assert abs(EXACT_A2 - 0.5 * V * EXACT_KAPPA ** 2) < 1e-12


def test_s3_control_regression_passes():
    report = run_s3_control()
    assert report.passed, f"S^3 control regression FAILED: max|E_kappa|={report.max_abs_e_kappa}"
    assert report.max_abs_e_kappa < 1e-4


def test_s3_control_reproduces_workbook_order_of_magnitude():
    # workbook nominal: E_kappa ~ 3.2e-6 at window [0.0015, 0.006]
    r = fit_window(0.0015, 0.006, degree=3)
    assert 1e-7 < abs(r.e_kappa) < 1e-5


def test_s3_fit_degree_2_is_measurably_biased():
    # confirms the degree>=3 justification in heat_kernel_sphere.py is not
    # an arbitrary choice: degree-2 alone is off by ~1000x
    r2 = fit_window(0.0015, 0.006, degree=2)
    r3 = fit_window(0.0015, 0.006, degree=3)
    assert abs(r2.e_kappa) > 100 * abs(r3.e_kappa)


def test_s3_control_fit_window_stability():
    report = run_s3_control()
    e_kappas = [abs(r.e_kappa) for r in report.fit_results]
    assert max(e_kappas) < 1e-4
    assert all(e < 2e-5 for e in e_kappas)
