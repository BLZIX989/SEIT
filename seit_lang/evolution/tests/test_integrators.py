"""Tests for seit_lang.evolution.integrators: API contracts and a real
convergence-order check against an exactly-solvable ODE (independent of
this package's own graph/Laplacian machinery)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.evolution.integrators import euler_step, evolve, rk4_step


# --- API contracts -----------------------------------------------------

def test_unknown_method_raises():
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, 0.1, method="bogus")


def test_nonpositive_dt_raises():
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, -0.1)


def test_t1_not_after_t0_raises():
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 1.0, 1.0, 0.1)
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 1.0, 0.0, 0.1)


def test_record_every_less_than_1_raises():
    with pytest.raises(ValueError):
        evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, 0.1, record_every=0)


def test_evolve_records_initial_and_final_states():
    traj = evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, 0.1, rhs_name="decay")
    assert traj.times[0] == 0.0
    assert traj.times[-1] == pytest.approx(1.0)
    assert traj.rhs_name == "decay"
    assert traj.method == "rk4"


def test_record_every_subsamples_but_always_keeps_final():
    traj = evolve(np.array([1.0]), lambda t, y: -y, 0.0, 1.0, 0.1, record_every=3)
    # 10 steps, recording every 3rd (steps 3,6,9) plus the initial state
    # and the final step (10) even though 10 is not a multiple of 3.
    assert traj.times[0] == 0.0
    assert traj.times[-1] == pytest.approx(1.0)
    assert traj.n_recorded < 11  # fewer than "record every step" would give


def test_euler_and_rk4_step_are_pure_functions():
    rhs = lambda t, y: -y
    y = np.array([2.0, 3.0])
    out_euler = euler_step(rhs, 0.0, y, 0.1)
    out_rk4 = rk4_step(rhs, 0.0, y, 0.1)
    assert np.array_equal(y, np.array([2.0, 3.0]))  # input not mutated
    assert not np.array_equal(out_euler, out_rk4)  # genuinely different methods


# --- real convergence-order check, y' = -y, y(0) = 1, exact y(t) = e^-t ---

def test_rk4_converges_at_fourth_order_euler_at_first_order():
    """A real numerical-analysis check: halving dt should shrink RK4's
    error by a factor near 2^4=16 and Euler's error by a factor near
    2^1=2, on the exactly-solvable decay ODE y'=-y. This is not
    tautological -- a broken RK4 implementation could still "work" in
    the sense of producing a decaying trajectory while failing this
    specific convergence-rate check."""
    t1 = 1.0
    exact = np.exp(-t1)

    def rhs(t, y):
        return -y

    errors = {"euler": [], "rk4": []}
    for dt in (0.1, 0.05):
        for method in ("euler", "rk4"):
            traj = evolve(np.array([1.0]), rhs, 0.0, t1, dt, method=method)
            errors[method].append(abs(traj.final().y[0] - exact))

    euler_ratio = errors["euler"][0] / errors["euler"][1]
    rk4_ratio = errors["rk4"][0] / errors["rk4"][1]

    assert 1.7 < euler_ratio < 2.3, f"euler order-1 ratio out of range: {euler_ratio}"
    assert 13.0 < rk4_ratio < 19.0, f"rk4 order-4 ratio out of range: {rk4_ratio}"
    assert errors["rk4"][1] < errors["euler"][1] / 100  # rk4 dramatically more accurate
