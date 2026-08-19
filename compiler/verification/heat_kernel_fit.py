"""Shared heat-kernel coefficient fit + curvature closure arithmetic
(spec: K(t) ~ (4*pi*t)^{-3/2}(a0 + a1 t + a2 t^2 + ...), curvature
residual E_kappa = a1/a0 - sgn(a1)*sqrt(2*a2/a0)).

Factored out of compiler/backends/heat_kernel_sphere.py so the S^3
analytic control and the (numeric, real-data) DESI pipeline use
identical fitting/closure arithmetic -- the two must be comparable, not
two independently-tuned implementations that could silently diverge.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def fit_polynomial_coefficients(t: np.ndarray, Y: np.ndarray, degree: int) -> np.ndarray:
    """Returns [a0, a1, a2, ...] (ascending order) from a degree-N local
    polynomial least-squares fit of Y(t)."""
    coeffs = np.polyfit(t, Y, degree)[::-1]
    return np.asarray(coeffs, dtype=float)


@dataclass
class CurvatureClosure:
    a0: float
    a1: float
    a2: float
    kappa_a1: float
    kappa_a2: float
    e_kappa: float

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def curvature_closure(a0: float, a1: float, a2: float) -> CurvatureClosure:
    # Cast every input/output to native Python float here, once, at the
    # boundary -- numpy scalar types (np.float64, and especially np.bool_
    # from comparisons on them) must never leak into a dataclass whose
    # fields end up in a JSON-serialized registry (np.bool_ is NOT a
    # subclass of bool and json.dumps rejects it; a chained `and` over
    # numpy booleans silently returns the last numpy operand untouched).
    a0, a1, a2 = float(a0), float(a1), float(a2)
    kappa_a1 = float(a1 / a0)
    kappa_a2 = float(np.sign(a1) * np.sqrt(2 * a2 / a0)) if a0 != 0 and a2 / a0 >= 0 else float("nan")
    e_kappa = float(kappa_a1 - kappa_a2)
    return CurvatureClosure(a0=a0, a1=a1, a2=a2, kappa_a1=kappa_a1, kappa_a2=kappa_a2, e_kappa=e_kappa)
