"""Tests for seit_lang.evolution_branch (Step 2): the typed
evolve/trajectory `.seit` abstraction, and its compatibility with the
existing acyclic-DAG semantics."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian

from seit_lang.cli import _json_safe, cmd_run
from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.evolution.rhs_library import heat_total, wave_energy
from seit_lang.evolution_branch import (
    EVOLUTION_BRANCH_BINDINGS,
    EVOLUTION_BRANCH_TRANSFORMATIONS,
    conservation_holds,
    evolve_heat_equation,
    evolve_wave_equation,
    heat_total_series,
    trajectory_final_state,
    trajectory_initial_state,
    trajectory_state_at,
    trajectory_times,
    wave_energy_series,
    wave_trajectory_final_u,
    wave_trajectory_final_v,
)
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program
from seit_lang.types import is_subtype


def _real_laplacian(topology="cycle", n=8, seed=0):
    A = graph_laplacian.build_graph(topology, n, seed=seed).adjacency()
    return graph_laplacian.laplacian(A)


# --- Python-level API: real, calibrated numerical checks -----------------

def test_evolve_heat_equation_returns_a_real_trajectory():
    L = _real_laplacian(n=6)
    y0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    traj = evolve_heat_equation(L, y0, 0.0, 1.0, 0.01, "rk4")
    assert traj.rhs_name == "heat_equation"
    assert traj.times[-1] == pytest.approx(1.0)


def test_trajectory_accessors_match_direct_state_access():
    L = _real_laplacian(n=6)
    y0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    traj = evolve_heat_equation(L, y0, 0.0, 1.0, 0.01, "rk4")
    assert np.array_equal(trajectory_initial_state(traj), traj.states[0])
    assert np.array_equal(trajectory_final_state(traj), traj.states[-1])
    assert np.array_equal(trajectory_times(traj), np.array(traj.times))
    nearest = trajectory_state_at(traj, 0.5)
    assert np.array_equal(nearest, traj.nearest(0.5).y)


def test_heat_total_series_matches_direct_computation():
    L = _real_laplacian(topology="erdos_renyi", n=8, seed=1)
    y0 = np.random.default_rng(2).standard_normal(8)
    traj = evolve_heat_equation(L, y0, 0.0, 1.0, 0.02, "rk4")
    series = heat_total_series(traj)
    expected = np.array([heat_total(s) for s in traj.states])
    assert np.array_equal(series, expected)
    # conserved to within RK4 numerical error
    assert series[-1] == pytest.approx(series[0], abs=1e-6)


def test_evolve_wave_equation_and_energy_series_match_direct_computation():
    L = _real_laplacian(topology="path", n=6)
    rng = np.random.default_rng(3)
    u0, v0 = rng.standard_normal(6), rng.standard_normal(6)
    traj = evolve_wave_equation(L, u0, v0, 0.0, 1.0, 0.01, "rk4")
    assert traj.metadata["n"] == 6

    energy_series = wave_energy_series(traj, L)
    expected = np.array([wave_energy(L, s) for s in traj.states])
    assert np.array_equal(energy_series, expected)

    final_u = wave_trajectory_final_u(traj)
    final_v = wave_trajectory_final_v(traj)
    assert np.array_equal(final_u, traj.final().y[:6])
    assert np.array_equal(final_v, traj.final().y[6:])


def test_conservation_holds_true_for_a_genuinely_conserved_series():
    series = np.array([5.0, 5.0000001, 4.9999998, 5.0])
    assert conservation_holds(series, 1e-4) is True


def test_conservation_holds_false_for_a_genuinely_drifting_series():
    """Negative control: proves conservation_holds can detect a real
    violation, not just always return True."""
    series = np.array([5.0, 5.5, 6.2, 8.0])
    assert conservation_holds(series, 1e-4) is False


def test_conservation_holds_on_real_heat_trajectory():
    L = _real_laplacian(n=10)
    y0 = np.random.default_rng(4).standard_normal(10)
    traj = evolve_heat_equation(L, y0, 0.0, 2.0, 0.005, "rk4")
    assert conservation_holds(heat_total_series(traj), 1e-5) is True


# --- type system integration ------------------------------------------------

def test_trajectory_type_is_a_dataset_specialization_end_to_end():
    assert is_subtype(EVOLUTION_BRANCH_TRANSFORMATIONS["evolve_heat_equation"].return_type, "Dataset")


def test_accessor_return_types_are_vector_not_trajectory():
    for name in ("trajectory_initial_state", "trajectory_final_state", "trajectory_times",
                 "heat_total_series", "wave_trajectory_final_u", "wave_trajectory_final_v"):
        assert EVOLUTION_BRANCH_TRANSFORMATIONS[name].return_type == "Vector"


def test_conservation_holds_returns_scalar_for_verify_compatibility():
    assert EVOLUTION_BRANCH_TRANSFORMATIONS["conservation_holds"].return_type == "Scalar"


# --- the core DAG-compatibility claim: one node per simulation, not per step -

def test_dag_has_one_node_per_named_value_not_one_per_timestep():
    """The core compatibility claim: however many internal timesteps a
    simulation takes (here, 1.0/0.001 = 1000 RK4 steps), the DAG must
    have exactly as many nodes as the program has named values -- never
    one node per step. This is what "remaining compatible with the
    existing DAG semantics" concretely means."""
    src = (
        'derive G = build_graph("cycle", 8); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "variable y0: Vector; "
        'derive traj = evolve_heat_equation(L, y0, 0.0, 1.0, 0.001, "rk4"); '
        "derive series = heat_total_series(traj); "
        "derive result = conservation_holds(series, 0.0001);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **EVOLUTION_BRANCH_TRANSFORMATIONS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result, supplied_inputs={"y0"})
    named_values = ["G", "A", "L", "y0", "traj", "series", "result"]
    assert set(dag.states) == set(named_values)
    assert len(dag.topological_order()) == len(named_values)  # NOT ~1000
    assert dag.blocked == {}


def test_realistic_program_runs_a_1000_step_simulation_as_one_dag_node():
    """The full, realistic version: a real graph, a real vector input
    (supplied externally, matching Phase 16's own --inputs pattern for
    a `variable` with no producing statement), a 1000-step RK4
    integration, and a genuine `verify` of a conserved quantity -- all
    while the DAG itself stays exactly 6 nodes."""
    src = (
        'derive G = build_graph("cycle", 8); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "variable y0: Vector; "
        'derive traj = evolve_heat_equation(L, y0, 0.0, 1.0, 0.001, "rk4"); '
        "derive series = heat_total_series(traj); "
        "verify conservation_holds(series, 0.0001);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **EVOLUTION_BRANCH_TRANSFORMATIONS}
    bindings = {**PHYSICS_KERNEL_BINDINGS, **EVOLUTION_BRANCH_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []

    y0 = np.random.default_rng(7).standard_normal(8)
    dag = compile_dag(program, check_result, supplied_inputs={"y0": y0})
    assert dag.blocked == {}
    assert len(dag.topological_order()) == 6  # G, A, L, y0, traj, series -- NOT ~1000

    env = evaluate_program(dag, program, inputs={"y0": y0}, bindings=bindings)
    assert env["traj"].n_recorded == 1001  # 1000 steps + initial state
    assert conservation_holds(env["series"], 1e-4) is True


# --- integration with the existing CLI (Phase 13/14) infrastructure --------

def test_trajectory_json_serializes_via_existing_json_safe_with_no_changes():
    """Trajectory is a plain dataclass, so cli._json_safe's existing
    generic is_dataclass() branch (built in Phase 13, before Trajectory
    existed) already handles it correctly -- no changes to cli.py's
    serializer were needed, a genuine compatibility win worth confirming
    directly rather than assuming."""
    import json
    L = _real_laplacian(n=6)
    y0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    traj = evolve_heat_equation(L, y0, 0.0, 0.5, 0.05, "rk4")
    safe = _json_safe(traj)
    json.dumps(safe)  # must not raise
    assert safe["method"] == "rk4"
    assert isinstance(safe["states"], list)
    assert isinstance(safe["states"][0], list)  # ndarray -> list, recursively


def test_cli_cmd_run_executes_a_real_simulation_end_to_end(tmp_path):
    src = (
        'derive G = build_graph("path", 6); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "variable y0: Vector; "
        'derive traj = evolve_heat_equation(L, y0, 0.0, 0.5, 0.01, "rk4"); '
        "derive final_state = trajectory_final_state(traj); "
        "derive series = heat_total_series(traj); "
        "verify conservation_holds(series, 0.0001);"
    )
    seit_file = tmp_path / "sim.seit"
    seit_file.write_text(src)
    inputs_file = tmp_path / "inputs.json"
    inputs_file.write_text('{"y0": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]}')

    result = cmd_run(str(seit_file), inputs_path=str(inputs_file))
    assert result["ok"] is True
    assert result["states"]["traj"] == "CALCULATED"
    assert len(result["environment"]["final_state"]) == 6
