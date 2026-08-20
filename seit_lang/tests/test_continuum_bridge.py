"""Tests for seit_lang.continuum_bridge (Phase 8)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import kc003_vr001

from seit_lang.continuum_bridge import (
    CONTINUUM_BRIDGE_BINDINGS,
    _seit_status_label,
    generate_continuum_bridge_declarations,
    kc003_subclaim_report,
    vr001_nonuniform_result,
    vr001_uniform_result,
)
from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.parser import parse
from seit_lang.semantic import check_program
from seit_lang.state import SeitState


# --- status labels read from real ground truth ------------------------

def test_kc003a_is_open_matching_real_not_computable_status():
    entry = kc003_subclaim_report("a")
    assert entry["status"].startswith("NOT COMPUTABLE")
    assert _seit_status_label(entry["status"]) == "OPEN"


def test_kc003d_is_open_matching_real_not_computable_status():
    entry = kc003_subclaim_report("d")
    assert entry["status"].startswith("NOT COMPUTABLE")
    assert _seit_status_label(entry["status"]) == "OPEN"


def test_kc003b_is_resolved_matching_real_partially_addressed_status():
    entry = kc003_subclaim_report("b")
    assert entry["status"].startswith("PARTIALLY ADDRESSED")
    assert _seit_status_label(entry["status"]) == "RESOLVED"


def test_kc003c_is_calculated_matching_real_computed_status():
    entry = kc003_subclaim_report("c")
    assert entry["status"].startswith("COMPUTED")
    assert _seit_status_label(entry["status"]) == "CALCULATED"


def test_status_label_defaults_to_open_for_unrecognized_text():
    assert _seit_status_label("some future unrecognized phrasing") == "OPEN"


# --- kc003_subclaim_report matches the real module --------------------

def test_kc003_subclaim_report_matches_real_decomposition():
    real = kc003_vr001.kc003_decomposition()
    assert kc003_subclaim_report("a") == real["KC-003a_measure_convergence"]
    assert kc003_subclaim_report("d") == real["KC-003d_geometric_convergence"]


def test_vr001_uniform_result_matches_real_module():
    n = 200
    real = kc003_vr001.vr001_known_manifold_control(n_values=(n,))
    assert vr001_uniform_result(n) == real["results"]["uniform"][n]


def test_vr001_nonuniform_result_matches_real_module():
    n = 200
    real = kc003_vr001.vr001_known_manifold_control(n_values=(n,))
    assert vr001_nonuniform_result(n) == real["results"]["nonuniform"][n]


def test_bindings_registered_for_all_three_accessors():
    assert set(CONTINUUM_BRIDGE_BINDINGS) == {
        "kc003_subclaim_report", "vr001_uniform_result", "vr001_nonuniform_result",
    }


# --- the generated .seit source is honest -------------------------------

def test_generated_source_parses_and_checks_cleanly():
    src = generate_continuum_bridge_declarations()
    program = parse(src)
    result = check_program(program)
    assert result.symbols["KC_003a_measure_convergence"] == "Dataset"
    assert result.symbols["KC_003d_geometric_convergence"] == "Dataset"
    assert result.symbols["VR001"] == "Dataset"
    assert result.unresolved_calls == []


def test_generated_source_kc003a_and_d_never_leave_declared_in_the_dag():
    """The core Phase 8 guarantee: no matter what the `status` statement
    TEXT says, the DAG's own tracked SeitState for KC-003a/d must stay
    DECLARED, because nothing in the generated source ever
    derives/calculates them. The status label is descriptive metadata,
    never a shortcut to a fabricated execution state."""
    program = parse(generate_continuum_bridge_declarations())
    dag = compile_dag(program)
    assert dag.states["KC_003a_measure_convergence"] == SeitState.DECLARED
    assert dag.states["KC_003d_geometric_convergence"] == SeitState.DECLARED
    assert dag.blocked == {}  # nothing attempted, so nothing to block either


def test_generated_source_evaluates_to_an_empty_environment():
    # No producing statements exist for any of these nodes -- evaluating
    # the program must not compute anything, honestly reflecting that
    # nothing was asked to be computed.
    program = parse(generate_continuum_bridge_declarations())
    dag = compile_dag(program)
    env = evaluate_program(dag, program, inputs={}, bindings={})
    assert env == {}


def test_generated_source_includes_kc003b_and_c_with_real_status_labels():
    src = generate_continuum_bridge_declarations()
    assert "status KC_003b_operator_convergence = RESOLVED;" in src
    assert "status KC_003c_spectral_convergence = CALCULATED;" in src
    assert "status KC_003a_measure_convergence = OPEN;" in src
    assert "status KC_003d_geometric_convergence = OPEN;" in src


def test_vr001_provenance_carries_the_methodology_caveat():
    src = generate_continuum_bridge_declarations()
    assert "NOT a claim about real DESI data" in src


# --- the trap this module's design deliberately avoids ---------------------

def test_the_fabrication_trap_this_module_avoids_is_real():
    """Demonstrates exactly the failure mode the module docstring warns
    about: naively `derive`-ing a subclaim's report INTO a node named
    after the claim itself drives that node to CALCULATED at the DAG
    level, even though the report's own content says OPEN. This is why
    generate_continuum_bridge_declarations() uses `variable` + `status`
    instead of `derive` for KC-003a/d -- this test is not asserting the
    trap is fixed, it is proving the trap exists so the safer pattern's
    necessity is not just asserted, but demonstrated."""
    src = 'derive KC003a = kc003_subclaim_report("a");'
    from seit_lang.continuum_bridge import CONTINUUM_BRIDGE_TRANSFORMATIONS
    program = parse(src)
    check_result = check_program(program, extra_transformations=CONTINUUM_BRIDGE_TRANSFORMATIONS)
    dag = compile_dag(program, check_result)
    assert dag.states["KC003a"] == SeitState.CALCULATED  # the trap: CALCULATED despite OPEN content
