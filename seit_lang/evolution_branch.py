"""Typed evolve/trajectory abstraction for `.seit` (Step 2 of 2):
exposes Step 1's standalone numerical evolution kernel
(seit_lang/evolution/) as executable `.seit` primitives, using the new
"Trajectory" type (seit_lang/types.py), WITHOUT adding any loop or
iteration construct to the grammar and WITHOUT introducing a cycle into
the dependency DAG.

HOW THIS STAYS COMPATIBLE WITH THE EXISTING DAG SEMANTICS: an entire
numerical simulation -- however many internal timesteps it takes --
collapses into exactly ONE `.seit` value, produced by exactly ONE
`derive` statement calling one of the evolve_* primitives below. The
internal time-stepping loop runs in plain Python (seit_lang.evolution.
integrators.evolve), invisible to the DAG; from the DAG's point of
view this is an ordinary primitive call with ordinary dependency edges
to its arguments (L, y0, t0, t1, dt), exactly like any other primitive
in this project. seit_lang/tests/test_evolution_branch.py confirms
this directly: dag.topological_order() for a program that runs a
1000-step simulation has exactly as many nodes as the program has named
values (a handful), never one node per timestep.

INDIVIDUAL TIMESTEPS STAY REACHABLE WITHOUT UNROLLING: rather than
representing a trajectory as N separate DAG nodes (impractical for any
real simulation) or as one opaque, unindexable blob, this module
provides typed ACCESSOR primitives -- trajectory_initial_state,
trajectory_final_state, trajectory_state_at, trajectory_times,
heat_total_series, wave_energy_series -- that pull specific,
individually-typed (Vector) values back out of a Trajectory. Each
accessor is its own DAG node with its own dependency edge to the
Trajectory node, so a `.seit` program CAN `verify` a specific extracted
quantity (e.g. conservation_holds(heat_total_series(traj), 1e-6)) with
its own proof obligation -- exactly the auditability a bare unindexable
blob would not offer -- without needing one node per timestep.

evolve_wave_equation's Trajectory stores its split point (the state
dimension n, since the wave equation's raw state is the concatenation
[u, v]) in Trajectory.metadata["n"] -- read by the wave-specific
accessors below, not re-derived or assumed by them.
"""
from __future__ import annotations

import numpy as np

from .evolution.integrators import evolve
from .evolution.rhs_library import heat_equation_rhs, heat_total, wave_energy, wave_equation_rhs
from .evolution.state import Trajectory
from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def evolve_heat_equation(L: np.ndarray, y0: np.ndarray, t0: float, t1: float,
                          dt: float, method: str = "rk4") -> Trajectory:
    rhs = heat_equation_rhs(L)
    return evolve(y0, rhs, float(t0), float(t1), float(dt), method=method, rhs_name="heat_equation")


def evolve_wave_equation(L: np.ndarray, u0: np.ndarray, v0: np.ndarray, t0: float,
                          t1: float, dt: float, method: str = "rk4") -> Trajectory:
    rhs = wave_equation_rhs(L)
    y0 = np.concatenate([np.asarray(u0, dtype=float), np.asarray(v0, dtype=float)])
    traj = evolve(y0, rhs, float(t0), float(t1), float(dt), method=method, rhs_name="wave_equation")
    traj.metadata["n"] = L.shape[0]
    return traj


def trajectory_initial_state(traj: Trajectory) -> np.ndarray:
    return traj.initial().y


def trajectory_final_state(traj: Trajectory) -> np.ndarray:
    return traj.final().y


def trajectory_state_at(traj: Trajectory, t: float) -> np.ndarray:
    return traj.nearest(float(t)).y


def trajectory_times(traj: Trajectory) -> np.ndarray:
    return np.array(traj.times)


def heat_total_series(traj: Trajectory) -> np.ndarray:
    """The heat equation's conserved quantity (sum(y)) at every
    recorded step -- see seit_lang.evolution.rhs_library.heat_total."""
    return np.array([heat_total(s) for s in traj.states])


def wave_energy_series(traj: Trajectory, L: np.ndarray) -> np.ndarray:
    """The wave equation's conserved energy at every recorded step --
    see seit_lang.evolution.rhs_library.wave_energy."""
    return np.array([wave_energy(L, s) for s in traj.states])


def wave_trajectory_final_u(traj: Trajectory) -> np.ndarray:
    n = traj.metadata["n"]
    return traj.final().y[:n]


def wave_trajectory_final_v(traj: Trajectory) -> np.ndarray:
    n = traj.metadata["n"]
    return traj.final().y[n:]


def conservation_holds(series: np.ndarray, tol: float) -> bool:
    """True iff every recorded value in `series` stays within relative
    tolerance `tol` of the first (initial) value -- a Scalar-valued
    (boolean) check usable directly inside a `.seit` `verify` statement,
    matching the pattern Phase 5's symmetric()/positive_semidefinite()
    already established (a boolean fact reported as a Call result, not
    expressed via a comparison operator `.seit`'s grammar does not
    have)."""
    series = np.asarray(series, dtype=float)
    reference = max(abs(float(series[0])), 1.0)
    return bool(np.all(np.abs(series - series[0]) <= float(tol) * reference))


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("evolve_heat_equation", ["Matrix", "Vector", "Scalar", "Scalar", "Scalar", "Scalar"],
                      "Trajectory", evolve_heat_equation,
                      "seit_lang.evolution_branch.evolve_heat_equation (Step 1 kernel: "
                      "seit_lang.evolution.rhs_library.heat_equation_rhs + integrators.evolve)"),
    PrimitiveBinding("evolve_wave_equation",
                      ["Matrix", "Vector", "Vector", "Scalar", "Scalar", "Scalar", "Scalar"],
                      "Trajectory", evolve_wave_equation,
                      "seit_lang.evolution_branch.evolve_wave_equation (Step 1 kernel: "
                      "seit_lang.evolution.rhs_library.wave_equation_rhs + integrators.evolve)"),
    PrimitiveBinding("trajectory_initial_state", ["Trajectory"], "Vector",
                      trajectory_initial_state, "seit_lang.evolution_branch.trajectory_initial_state"),
    PrimitiveBinding("trajectory_final_state", ["Trajectory"], "Vector",
                      trajectory_final_state, "seit_lang.evolution_branch.trajectory_final_state"),
    PrimitiveBinding("trajectory_state_at", ["Trajectory", "Scalar"], "Vector",
                      trajectory_state_at, "seit_lang.evolution_branch.trajectory_state_at"),
    PrimitiveBinding("trajectory_times", ["Trajectory"], "Vector",
                      trajectory_times, "seit_lang.evolution_branch.trajectory_times"),
    PrimitiveBinding("heat_total_series", ["Trajectory"], "Vector",
                      heat_total_series, "seit_lang.evolution_branch.heat_total_series"),
    PrimitiveBinding("wave_energy_series", ["Trajectory", "Matrix"], "Vector",
                      wave_energy_series, "seit_lang.evolution_branch.wave_energy_series"),
    PrimitiveBinding("wave_trajectory_final_u", ["Trajectory"], "Vector",
                      wave_trajectory_final_u, "seit_lang.evolution_branch.wave_trajectory_final_u"),
    PrimitiveBinding("wave_trajectory_final_v", ["Trajectory"], "Vector",
                      wave_trajectory_final_v, "seit_lang.evolution_branch.wave_trajectory_final_v"),
    PrimitiveBinding("conservation_holds", ["Vector", "Scalar"], "Scalar",
                      conservation_holds, "seit_lang.evolution_branch.conservation_holds"),
]

EVOLUTION_BRANCH_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
EVOLUTION_BRANCH_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
