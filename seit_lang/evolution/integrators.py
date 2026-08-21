"""Fixed-step ODE integrators for the evolution kernel: two real,
standard, well-known methods -- explicit (forward) Euler, order 1, and
classic Runge-Kutta, order 4 -- external, established numerical
analysis (any introductory numerical-methods reference), not a new
scheme invented for this project. evolve() is the stepping driver;
its correctness (convergence order, invariant preservation) is
verified against real reference solutions in
tests/test_correctness_against_exact_solution.py, not merely asserted.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .state import Trajectory

RHS = Callable[[float, np.ndarray], np.ndarray]


def euler_step(rhs: RHS, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    return y + dt * rhs(t, y)


def rk4_step(rhs: RHS, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    k1 = rhs(t, y)
    k2 = rhs(t + dt / 2.0, y + (dt / 2.0) * k1)
    k3 = rhs(t + dt / 2.0, y + (dt / 2.0) * k2)
    k4 = rhs(t + dt, y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


_STEPPERS: dict[str, Callable[[RHS, float, np.ndarray, float], np.ndarray]] = {
    "euler": euler_step,
    "rk4": rk4_step,
}


def evolve(
    y0: np.ndarray,
    rhs: RHS,
    t0: float,
    t1: float,
    dt: float,
    method: str = "rk4",
    rhs_name: str = "unnamed",
    record_every: int = 1,
) -> Trajectory:
    """Integrates dy/dt = rhs(t, y) from t0 to t1 with fixed step dt,
    recording every `record_every`-th step (plus always the initial and
    final states). Raises ValueError for an unknown method or a
    non-positive dt/step count -- fails loudly rather than silently
    producing a nonsensical trajectory."""
    if method not in _STEPPERS:
        raise ValueError(f"unknown method {method!r}, expected one of {sorted(_STEPPERS)}")
    if dt <= 0:
        raise ValueError(f"dt must be positive, got {dt!r}")
    if t1 <= t0:
        raise ValueError(f"t1 ({t1!r}) must be greater than t0 ({t0!r})")
    if record_every < 1:
        raise ValueError(f"record_every must be >= 1, got {record_every!r}")

    stepper = _STEPPERS[method]
    n_steps = int(round((t1 - t0) / dt))
    if n_steps < 1:
        raise ValueError(f"t1 - t0 ({t1 - t0!r}) is smaller than one step dt ({dt!r})")

    y = np.array(y0, dtype=float)
    t = float(t0)
    times: list[float] = [t]
    states: list[np.ndarray] = [y.copy()]
    for i in range(1, n_steps + 1):
        y = stepper(rhs, t, y, dt)
        t = t0 + i * dt
        if i % record_every == 0 or i == n_steps:
            times.append(t)
            states.append(y.copy())

    return Trajectory(
        times=times, states=states, method=method, rhs_name=rhs_name,
        metadata={"t0": t0, "t1": t1, "dt": dt, "n_steps": n_steps, "record_every": record_every},
    )
