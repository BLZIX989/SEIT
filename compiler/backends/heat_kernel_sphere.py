"""S^3 analytic heat-kernel control (FC-005 mandatory regression test,
run BEFORE any DESI calculation). Unit 3-sphere: lambda_l = l(l+2) with
multiplicity m_l = (l+1)^2 (l=0,1,2,...). Exact heat-kernel coefficients
for this constant-curvature manifold: a0 = V = 2*pi^2, a1 = V*kappa = 2*pi^2,
a2 = (1/2)*V*kappa^2 = pi^2, with sectional curvature kappa=1 and scalar
curvature R=6 (R=6*kappa).

Fitting note: K(t) ~ (4*pi*t)^{-3/2} * (a0 + a1 t + a2 t^2 + ...) is an
open-ended asymptotic series (the workbook's own equation ends in "...").
A plain quadratic (degree-2) least-squares fit over a finite window is
therefore biased by the neglected a3 t^3 term -- confirmed numerically
below (a degree-2 fit over the workbook's windows gives |E_kappa| ~ 1e-3,
two orders of magnitude worse than reported). Including a3 (degree-3 fit)
removes the leading-order bias and reproduces the workbook's ~1e-6 result
independently; this module treats the fit degree as a swept parameter
(spec section 14: fit-window stability) rather than a fixed hidden choice.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from compiler.verification.heat_kernel_fit import curvature_closure, fit_polynomial_coefficients

EXACT_KAPPA = 1.0
EXACT_R = 6.0
EXACT_A0 = 2 * np.pi**2
EXACT_A1 = 2 * np.pi**2
EXACT_A2 = np.pi**2

DEFAULT_FIT_WINDOWS = [(0.001, 0.004), (0.0015, 0.006), (0.002, 0.008), (0.003, 0.01)]


def s3_spectrum(l_max: int) -> tuple[np.ndarray, np.ndarray]:
    l = np.arange(0, l_max + 1)
    lam = l * (l + 2)
    mult = (l + 1) ** 2
    return lam.astype(float), mult.astype(float)


def required_l_max(t_min: float, margin: float = 80.0) -> int:
    """l_max such that exp(-t_min * l_max^2) << machine epsilon (margin=80
    gives exp(-80) ~ 1.8e-35, far below double precision, so truncation
    error is not the limiting error source at any t in the fit windows)."""
    return max(50, int(np.ceil(np.sqrt(margin / t_min))))


def heat_trace(t: np.ndarray | float, lam: np.ndarray, mult: np.ndarray) -> np.ndarray:
    t = np.atleast_1d(np.asarray(t, dtype=float))
    return np.array([np.sum(mult * np.exp(-tt * lam)) for tt in t])


def heat_trace_scaled(t: np.ndarray, lam: np.ndarray, mult: np.ndarray) -> np.ndarray:
    """Y(t) = K(t) * (4 pi t)^{3/2}, the d=3 rescaling that turns the
    leading heat-kernel divergence into a regular polynomial in t."""
    K = heat_trace(t, lam, mult)
    return K * (4 * np.pi * t) ** 1.5


@dataclass
class FitWindowResult:
    t_min: float
    t_max: float
    degree: int
    npts: int
    l_max: int
    a0: float
    a1: float
    a2: float
    kappa_a1: float
    kappa_a2: float
    e_kappa: float

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def fit_window(t_min: float, t_max: float, *, degree: int = 3, npts: int = 50) -> FitWindowResult:
    l_max = required_l_max(t_min)
    lam, mult = s3_spectrum(l_max)
    ts = np.linspace(t_min, t_max, npts)
    ys = heat_trace_scaled(ts, lam, mult)
    coeffs = fit_polynomial_coefficients(ts, ys, degree)  # coeffs[0]=a0, coeffs[1]=a1, coeffs[2]=a2
    closure = curvature_closure(coeffs[0], coeffs[1], coeffs[2])
    return FitWindowResult(t_min=t_min, t_max=t_max, degree=degree, npts=npts, l_max=l_max,
                            a0=closure.a0, a1=closure.a1, a2=closure.a2,
                            kappa_a1=closure.kappa_a1, kappa_a2=closure.kappa_a2, e_kappa=closure.e_kappa)


@dataclass
class S3ControlReport:
    fit_results: list[FitWindowResult]
    degree_sweep: dict[int, list[FitWindowResult]]
    tolerance: float
    max_abs_e_kappa: float
    a0_max_residual: float
    a1_max_residual: float
    a2_max_residual: float
    passed: bool

    def to_dict(self) -> dict:
        return {
            "fit_results": [r.to_dict() for r in self.fit_results],
            "degree_sweep": {str(d): [r.to_dict() for r in rs] for d, rs in self.degree_sweep.items()},
            "tolerance": self.tolerance,
            "max_abs_e_kappa": self.max_abs_e_kappa,
            "a0_max_residual": self.a0_max_residual,
            "a1_max_residual": self.a1_max_residual,
            "a2_max_residual": self.a2_max_residual,
            "passed": self.passed,
            "exact": {"kappa": EXACT_KAPPA, "R": EXACT_R, "a0": EXACT_A0, "a1": EXACT_A1, "a2": EXACT_A2},
        }


def run_s3_control(
    windows: list[tuple[float, float]] | None = None,
    *, degree: int = 3, npts: int = 50, tolerance: float = 1e-4,
) -> S3ControlReport:
    windows = windows or DEFAULT_FIT_WINDOWS
    fit_results = [fit_window(tmin, tmax, degree=degree, npts=npts) for tmin, tmax in windows]

    degree_sweep: dict[int, list[FitWindowResult]] = {}
    for d in (2, 3, 4, 5):
        degree_sweep[d] = [fit_window(tmin, tmax, degree=d, npts=npts) for tmin, tmax in windows]

    max_abs_e_kappa = max(abs(r.e_kappa) for r in fit_results)
    a0_res = max(abs(r.a0 - EXACT_A0) / EXACT_A0 for r in fit_results)
    a1_res = max(abs(r.a1 - EXACT_A1) / EXACT_A1 for r in fit_results)
    a2_res = max(abs(r.a2 - EXACT_A2) / EXACT_A2 for r in fit_results)
    passed = bool(max_abs_e_kappa < tolerance and a0_res < tolerance and a1_res < tolerance and a2_res < tolerance)

    return S3ControlReport(
        fit_results=fit_results, degree_sweep=degree_sweep, tolerance=tolerance,
        max_abs_e_kappa=max_abs_e_kappa, a0_max_residual=a0_res, a1_max_residual=a1_res,
        a2_max_residual=a2_res, passed=passed,
    )
