"""Tests for seit_lang.evolution.rhs_library: correctness against a
real, independently-computed exact solution (the heat equation's
closed-form matrix exponential, compiler.backends.heat_flow.
heat_operator, never reimplemented here) and genuine conservation-law
checks (not tautologies -- each is a real property of the underlying
graph Laplacian or of Hamiltonian structure, verified numerically)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian, heat_flow

from seit_lang.evolution.integrators import evolve
from seit_lang.evolution.rhs_library import heat_equation_rhs, heat_total, wave_energy, wave_equation_rhs


def _real_laplacian(topology="cycle", n=8, seed=0):
    A = graph_laplacian.build_graph(topology, n, seed=seed).adjacency()
    return graph_laplacian.laplacian(A)


# --- heat equation: correctness against the real exact solution -----------

def test_heat_equation_rk4_matches_exact_matrix_exponential_solution():
    L = _real_laplacian(n=8)
    rng = np.random.default_rng(1)
    y0 = rng.standard_normal(8)
    t1 = 0.5

    rhs = heat_equation_rhs(L)
    traj = evolve(y0, rhs, 0.0, t1, dt=0.01, method="rk4", rhs_name="heat")
    numeric = traj.final().y

    exact = heat_flow.heat_operator(L, t1) @ y0

    assert np.allclose(numeric, exact, atol=1e-6), \
        f"max abs diff {np.max(np.abs(numeric - exact))}"


def test_heat_equation_rk4_error_shrinks_as_dt_shrinks():
    L = _real_laplacian(n=8)
    rng = np.random.default_rng(2)
    y0 = rng.standard_normal(8)
    t1 = 0.5
    exact = heat_flow.heat_operator(L, t1) @ y0
    rhs = heat_equation_rhs(L)

    err_coarse = np.max(np.abs(evolve(y0, rhs, 0.0, t1, dt=0.05, method="rk4").final().y - exact))
    err_fine = np.max(np.abs(evolve(y0, rhs, 0.0, t1, dt=0.005, method="rk4").final().y - exact))
    assert err_fine < err_coarse / 100  # 10x smaller dt, RK4 (order 4) -> ~10^4 smaller error


# --- heat equation: total heat is exactly conserved -----------------------

def test_heat_total_conserved_exactly_for_the_real_graph_laplacian():
    """sum(y) is conserved because 1^T L = 0 identically for L = D - A
    -- a real algebraic fact about the graph Laplacian, checked here on
    an actual evolved trajectory, not assumed."""
    L = _real_laplacian(topology="erdos_renyi", n=10, seed=3)
    rng = np.random.default_rng(4)
    y0 = rng.standard_normal(10)
    rhs = heat_equation_rhs(L)
    traj = evolve(y0, rhs, 0.0, 2.0, dt=0.01, method="rk4")

    total_0 = heat_total(traj.initial().y)
    for state_idx in range(traj.n_recorded):
        total_t = heat_total(traj.states[state_idx])
        assert total_t == pytest.approx(total_0, abs=1e-8)


def test_heat_total_not_conserved_under_a_deliberately_wrong_rhs():
    """Negative control: a modified RHS that adds a constant drift
    breaks the conservation law -- proving the conservation test above
    can actually detect a violation, not just always pass."""
    L = _real_laplacian(n=6)
    y0 = np.ones(6)

    def broken_rhs(t, y):
        return -(L @ y) + 1.0  # spurious source term

    traj = evolve(y0, broken_rhs, 0.0, 1.0, dt=0.01, method="rk4")
    assert heat_total(traj.final().y) != pytest.approx(heat_total(traj.initial().y), abs=1e-3)


# --- wave equation: energy conservation, and convergence of that conservation

def test_wave_energy_approximately_conserved_and_improves_with_smaller_dt():
    L = _real_laplacian(topology="path", n=6)
    n = L.shape[0]
    rng = np.random.default_rng(5)
    u0 = rng.standard_normal(n)
    v0 = rng.standard_normal(n)
    y0 = np.concatenate([u0, v0])
    rhs = wave_equation_rhs(L)
    E0 = wave_energy(L, y0)

    traj_coarse = evolve(y0, rhs, 0.0, 2.0, dt=0.05, method="rk4")
    traj_fine = evolve(y0, rhs, 0.0, 2.0, dt=0.005, method="rk4")

    drift_coarse = abs(wave_energy(L, traj_coarse.final().y) - E0)
    drift_fine = abs(wave_energy(L, traj_fine.final().y) - E0)

    assert drift_fine < drift_coarse  # smaller dt -> better energy conservation
    assert drift_fine < 1e-3 * max(E0, 1.0)  # fine-dt drift is small relative to E0


def test_wave_equation_reduces_state_correctly_shape_and_split():
    L = _real_laplacian(n=4)
    rhs = wave_equation_rhs(L)
    y = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # u=[1,0,0,0], v=[0,0,0,0]
    dydt = rhs(0.0, y)
    du, dv = dydt[:4], dydt[4:]
    assert np.array_equal(du, np.zeros(4))  # du/dt = v = 0 initially
    assert not np.array_equal(dv, np.zeros(4))  # dv/dt = -Lu, and Lu != 0 for u=[1,0,0,0]
