"""Tests for seit_lang.spectral_action (Phase 12)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.incidence_clifford import (
    INCIDENCE_CLIFFORD_BINDINGS,
    INCIDENCE_CLIFFORD_TRANSFORMATIONS,
    block_dirac,
    grading_operator,
    ring_incidence_matrix,
)
from seit_lang.parser import parse
from seit_lang.semantic import check_program
from seit_lang.spectral_action import (
    SPECTRAL_ACTION_BINDINGS,
    SPECTRAL_ACTION_TRANSFORMATIONS,
    finite_moment_report,
    finite_spectral_moment,
    spectral_action_trace,
    spectral_triple_prerequisites_report,
)


# --- prerequisites report: the gate -------------------------------------

def test_self_adjoint_real_symmetric_matrix_reports_true():
    D = np.diag([0.0, 1.0, 2.0, 3.0])
    report = spectral_triple_prerequisites_report(D)
    assert report["D_is_self_adjoint"] is True
    assert report["all_prerequisites_satisfied"] is False  # never True in this corpus


def test_non_self_adjoint_matrix_reports_false():
    D = np.array([[0.0, 1.0], [0.0, 0.0]])
    report = spectral_triple_prerequisites_report(D)
    assert report["D_is_self_adjoint"] is False


def test_no_grading_supplied_reports_none_not_false():
    report = spectral_triple_prerequisites_report(np.eye(2))
    assert report["grading_supplied"] is False
    assert report["D_anticommutes_with_grading"] is None


def test_real_structure_and_first_order_condition_never_checked():
    report = spectral_triple_prerequisites_report(np.eye(3))
    assert report["real_structure_J_checked"] is False
    assert report["first_order_condition_checked"] is False


# --- cross-phase: Phase 6's D_B correctly gated despite passing what CAN --
# --- be checked -------------------------------------------------------------

def test_block_dirac_from_phase6_passes_checkable_prerequisites_but_gate_still_closed():
    """D_B is self-adjoint and anticommutes with gamma (both already
    verified in Phase 6) -- this must be reflected honestly here -- but
    all_prerequisites_satisfied must STILL be False, since J and the
    first-order condition remain unconstructed anywhere in this corpus.
    This is the literal "only after spectral-triple prerequisites
    satisfied" gate, exercised on this project's own real object."""
    B = ring_incidence_matrix(10, 3)
    D = block_dirac(B)
    gamma = grading_operator(B)
    report = spectral_triple_prerequisites_report(D, gamma)
    assert report["D_is_self_adjoint"] is True
    assert report["D_anticommutes_with_grading"] is True
    assert report["all_prerequisites_satisfied"] is False


# --- Tr f(D/Lambda) -----------------------------------------------------

def test_spectral_action_trace_step_cutoff_exact_count():
    D = np.diag([0.0, 1.0, 2.0, 3.0])
    # eigenvalues/1.5 = [0, 0.667, 1.333, 2] -> |x|<=1 for the first two
    result = spectral_action_trace(D, 1.5, cutoff="step")
    assert result == pytest.approx(2.0)


def test_spectral_action_trace_gaussian_cutoff_matches_direct_computation():
    D = np.diag([0.0, 1.0, 2.0])
    Lambda = 2.0
    result = spectral_action_trace(D, Lambda, cutoff="gaussian")
    expected = float(np.sum(np.exp(-(np.array([0.0, 1.0, 2.0]) / Lambda) ** 2)))
    assert result == pytest.approx(expected)


def test_spectral_action_trace_unknown_cutoff_raises():
    with pytest.raises(ValueError):
        spectral_action_trace(np.eye(2), 1.0, cutoff="not_a_real_cutoff")


def test_spectral_action_trace_default_is_step():
    D = np.diag([0.0, 1.0, 2.0, 3.0])
    assert spectral_action_trace(D, 1.5) == spectral_action_trace(D, 1.5, cutoff="step")


# --- finite spectral moments, explicitly NOT Seeley-DeWitt coefficients ----

def test_moment_0_is_the_dimension():
    D = np.diag([5.0, -3.0, 2.0])
    assert finite_spectral_moment(D, 0) == pytest.approx(3.0)


def test_moment_2_matches_direct_trace_of_D_squared():
    D = np.array([[1.0, 2.0], [2.0, -1.0]])
    assert finite_spectral_moment(D, 2) == pytest.approx(float(np.trace(D @ D)))


def test_moment_report_tracks_assumptions_per_coefficient():
    D = np.diag([1.0, 2.0, 3.0])
    report = finite_moment_report(D, max_k=4)
    assert set(report["moments"]) == {"moment_0", "moment_2", "moment_4"}
    for entry in report["moments"].values():
        assert len(entry["assumptions_used"]) == 3
        assert "value" in entry


def test_moment_report_states_no_physical_interpretation():
    D = np.diag([1.0, 2.0, 3.0])
    report = finite_moment_report(D)
    assert report["physical_interpretation"] is None
    assert "NONE" in report["physical_interpretation_note"]


def test_moment_report_includes_prerequisites():
    D = np.diag([1.0, 2.0])
    report = finite_moment_report(D)
    assert "spectral_triple_prerequisites" in report
    assert report["spectral_triple_prerequisites"]["all_prerequisites_satisfied"] is False


# --- .seit integration across Phase 6 + Phase 12 ----------------------------

def test_full_spectral_action_pipeline_on_phase6_block_dirac():
    src = (
        "derive B = ring_incidence_matrix(10, 3); "
        "derive D = block_dirac(B); "
        "derive gamma = grading_operator(B); "
        "derive prereq = spectral_triple_prerequisites_report(D); "
        "derive moments = finite_moment_report(D, 4);"
    )
    program = parse(src)
    extra = {**INCIDENCE_CLIFFORD_TRANSFORMATIONS, **SPECTRAL_ACTION_TRANSFORMATIONS}
    bindings = {**INCIDENCE_CLIFFORD_BINDINGS, **SPECTRAL_ACTION_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}

    env = evaluate_program(dag, program, inputs={}, bindings=bindings)
    assert env["prereq"]["D_is_self_adjoint"] is True
    assert env["prereq"]["all_prerequisites_satisfied"] is False
    assert env["moments"]["physical_interpretation"] is None
    assert env["moments"]["moments"]["moment_0"]["value"] == pytest.approx(env["D"].shape[0])
