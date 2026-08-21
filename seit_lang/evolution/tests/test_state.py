"""Tests for seit_lang.evolution.state."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.evolution.state import Trajectory


def _traj(n=4):
    times = [float(i) for i in range(n)]
    states = [np.array([float(i), float(i) * 2]) for i in range(n)]
    return Trajectory(times=times, states=states, method="rk4", rhs_name="test")


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        Trajectory(times=[0.0, 1.0], states=[np.array([1.0])], method="rk4", rhs_name="x")


def test_empty_trajectory_raises():
    with pytest.raises(ValueError):
        Trajectory(times=[], states=[], method="rk4", rhs_name="x")


def test_initial_and_final():
    traj = _traj()
    assert traj.initial().t == 0.0
    assert np.array_equal(traj.initial().y, traj.states[0])
    assert traj.final().t == 3.0
    assert np.array_equal(traj.final().y, traj.states[-1])


def test_at_step():
    traj = _traj()
    s = traj.at_step(2)
    assert s.t == 2.0
    assert np.array_equal(s.y, traj.states[2])


def test_nearest():
    traj = _traj()
    assert traj.nearest(1.4).t == 1.0
    assert traj.nearest(1.6).t == 2.0
    assert traj.nearest(-5.0).t == 0.0
    assert traj.nearest(500.0).t == 3.0


def test_y0_and_n_recorded():
    traj = _traj()
    assert np.array_equal(traj.y0, traj.states[0])
    assert traj.n_recorded == 4


def test_as_array_stacks_states():
    traj = _traj()
    arr = traj.as_array()
    assert arr.shape == (4, 2)
    assert np.array_equal(arr[2], traj.states[2])
