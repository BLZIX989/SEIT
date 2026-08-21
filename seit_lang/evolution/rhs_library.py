"""Standard, externally-established right-hand-side generators for the
evolution kernel, built on this repo's own REAL Laplacian objects
(compiler.backends.graph_laplacian.laplacian) -- not new physics
claims. Two systems:

  - heat_equation_rhs(L): dy/dt = -L y, the standard discrete heat/
    diffusion equation on a graph. Its EXACT solution is
    y(t) = expm(-tL) y0 -- already implemented, independently of this
    package, as compiler.backends.heat_flow.heat_operator -- used only
    as a correctness reference in this package's own tests, never
    duplicated as a competing "exact" claim.

  - wave_equation_rhs(L): the standard discrete wave equation on a
    graph, d^2u/dt^2 = -L u, reduced to first order via v = du/dt:
    d/dt [u, v] = [v, -L u]. A textbook reduction (not a
    project-specific claim), whose conserved discrete energy
    E = 1/2 (v^T v + u^T L u) gives this package's tests a second,
    independent correctness check beyond the heat equation's exact
    solution -- neither system's correctness here rests on the other's.

Both systems require L to be the real, symmetric, positive-semidefinite
graph Laplacian this project already builds elsewhere; neither function
constructs or validates L itself.
"""
from __future__ import annotations

import numpy as np


def heat_equation_rhs(L: np.ndarray):
    """dy/dt = -L y."""
    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        return -(L @ y)
    return rhs


def heat_total(y: np.ndarray) -> float:
    """The heat equation's conserved linear invariant: sum(y) = 1^T y,
    exactly conserved because 1^T L = 0 for any graph Laplacian
    (L = D - A has zero row AND column sums)."""
    return float(np.sum(y))


def wave_equation_rhs(L: np.ndarray):
    """State y = [u, v] with v = du/dt: d/dt[u, v] = [v, -L u]."""
    n = L.shape[0]

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        u, v = y[:n], y[n:]
        du = v
        dv = -(L @ u)
        return np.concatenate([du, dv])
    return rhs


def wave_energy(L: np.ndarray, y: np.ndarray) -> float:
    """The wave equation's conserved discrete energy
    E = 1/2 (v^T v + u^T L u)."""
    n = L.shape[0]
    u, v = y[:n], y[n:]
    return float(0.5 * (v @ v + u @ (L @ u)))
