"""Tests for seit_lang.cli (Phase 13)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.cli import (
    TARGET_PRESETS,
    _json_safe,
    cmd_audit,
    cmd_build,
    cmd_check,
    cmd_graph,
    cmd_parse,
    cmd_report,
    cmd_run,
    cmd_status,
    cmd_verify,
    main,
)
from seit_lang.state import SeitState

FIXTURES = Path(__file__).parent / "fixtures"
GEOMETRY = str(FIXTURES / "geometry_pipeline.seit")
MILESTONE = str(FIXTURES / "spectral_test_complete.seit")
AUDITED = str(FIXTURES / "audited_pipeline.seit")


CANONICAL_FILES = [
    "equation_registry.json", "object_registry.json", "transformation_registry.json",
    "master_mdcl.json", "chainlink_registry.json", "protocol_registry.json",
]


# --- _json_safe -------------------------------------------------------

def test_json_safe_real_ndarray_becomes_list():
    assert _json_safe(np.array([[1.0, 2.0], [3.0, 4.0]])) == [[1.0, 2.0], [3.0, 4.0]]


def test_json_safe_complex_ndarray_becomes_structured_dict():
    arr = np.array([[1 + 2j, 0j], [0j, 3 - 1j]])
    result = _json_safe(arr)
    assert result["__complex_ndarray__"] is True
    assert result["real"] == [[1.0, 0.0], [0.0, 3.0]]
    assert result["imag"] == [[2.0, 0.0], [0.0, -1.0]]


def test_json_safe_numpy_scalar_becomes_python_scalar():
    assert _json_safe(np.float64(3.5)) == 3.5
    assert isinstance(_json_safe(np.float64(3.5)), float)
    assert _json_safe(np.int64(4)) == 4
    assert _json_safe(np.bool_(True)) is True


def test_json_safe_seit_state_becomes_its_value():
    assert _json_safe(SeitState.CALCULATED) == "CALCULATED"


def test_json_safe_dataclass_becomes_dict():
    from compiler.backends.graph_laplacian import build_graph
    g = build_graph("cycle", 5)
    result = _json_safe(g)
    assert result["topology"] == "cycle"
    assert result["n"] == 5


def test_json_safe_is_fully_serializable_with_stdlib_json():
    payload = {"a": np.array([1.0, 2.0]), "b": SeitState.OPEN, "c": np.float64(1.5)}
    json.dumps(_json_safe(payload))  # must not raise


# --- parse ---------------------------------------------------------------

def test_cmd_parse_ok_reports_module_name_and_statement_count():
    result = cmd_parse(GEOMETRY)
    assert result["ok"] is True
    assert result["module_name"] == "geometry_pipeline"
    assert result["n_statements"] > 0
    assert "provenance" in result


def test_cmd_parse_syntax_error(tmp_path):
    bad = tmp_path / "bad.seit"
    bad.write_text("module m")  # missing semicolon
    result = cmd_parse(str(bad))
    assert result["ok"] is False
    assert result["stage"] == "parse"


# --- check -----------------------------------------------------------------

def test_cmd_check_default_target_resolves_all_calls():
    result = cmd_check(GEOMETRY)
    assert result["ok"] is True
    assert result["unresolved_calls"] == []
    assert result["symbols"]["L"] == "Laplacian"


def test_cmd_check_fc005_target_leaves_incidence_clifford_calls_unresolved(tmp_path):
    src = tmp_path / "prog.seit"
    src.write_text('derive B = ring_incidence_matrix(6, 3);\n')
    result = cmd_check(str(src), target="FC005")
    assert result["ok"] is True
    assert any(c["callee"] == "ring_incidence_matrix" for c in result["unresolved_calls"])
    assert "not yet exposed" in result["target_note"]


def test_cmd_check_semantic_error(tmp_path):
    src = tmp_path / "prog.seit"
    src.write_text("variable X: NotARealType;\n")
    result = cmd_check(str(src))
    assert result["ok"] is False
    assert result["stage"] == "check"


# --- build ------------------------------------------------------------------

def test_cmd_build_geometry_pipeline_fully_calculated():
    result = cmd_build(GEOMETRY)
    assert result["ok"] is True
    for name in ("G", "A", "L", "S"):
        assert result["states"][name] == "CALCULATED"
    assert result["blocked"] == {}
    assert len(result["edges"]) > 0


def test_cmd_build_milestone_fixture_reports_L_blocked():
    result = cmd_build(MILESTONE)
    assert result["ok"] is True
    assert result["states"]["L"] == "BLOCKED"
    assert "L" in result["blocked"]


# --- run ---------------------------------------------------------------------

def test_cmd_run_geometry_pipeline_computes_real_values():
    result = cmd_run(GEOMETRY)
    assert result["ok"] is True
    L = result["environment"]["L"]
    assert isinstance(L, list)
    L_arr = np.array(L)
    assert np.allclose(L_arr, L_arr.T)  # a real graph Laplacian is symmetric


def test_cmd_run_milestone_fixture_fails_honestly_on_unset_B():
    result = cmd_run(MILESTONE)
    assert result["ok"] is False
    assert result["stage"] == "run"
    assert "B" in result["error"]


# --- verify --------------------------------------------------------------

def test_cmd_verify_geometry_pipeline_all_pass():
    result = cmd_verify(GEOMETRY)
    assert result["ok"] is True
    assert len(result["verify_results"]) == 2
    assert all(r["passed"] is True for r in result["verify_results"])


def test_cmd_verify_reports_a_genuine_failure(tmp_path):
    src = tmp_path / "prog.seit"
    src.write_text("derive mu = construct_intersection_matrix(6, 6, 7);\nverify symmetric(mu);\n")
    result = cmd_verify(str(src))
    assert result["ok"] is False
    assert result["verify_results"][0]["passed"] is False  # KO=6 is antisymmetric, genuinely fails


# --- audit / status --------------------------------------------------------

def test_cmd_audit_reports_target_state_and_obligations():
    result = cmd_audit(AUDITED)
    assert result["ok"] is True
    assert len(result["audits"]) == 1
    entry = result["audits"][0]
    assert entry["target"] == "y"
    assert entry["state"] == "CALCULATED"
    assert any("y == y" in ob for ob in entry["proof_obligations"])


def test_cmd_status_reports_dag_state_separate_from_declared_status_statement():
    result = cmd_status(AUDITED)
    assert result["ok"] is True
    # the real DAG state (computed) and the source's own `status`
    # statement (descriptive metadata) are reported separately and
    # need not agree -- exactly Phase 8's documented distinction.
    assert result["dag_states"]["y"] == "CALCULATED"
    assert result["declared_status_statements"]["y"] == "VERIFIED"


# --- graph -----------------------------------------------------------------

def test_cmd_graph_reports_topological_order_and_edges():
    result = cmd_graph(GEOMETRY)
    assert result["ok"] is True
    order = result["topological_order"]
    assert order.index("G") < order.index("A") < order.index("L") < order.index("S")
    assert len(result["edges"]) >= 3


# --- report ------------------------------------------------------------------

def test_cmd_report_geometry_pipeline_summarizes_success():
    result = cmd_report(GEOMETRY)
    assert result["ok"] is True
    assert result["module_name"] == "geometry_pipeline"
    assert result["blocked"] == {}
    assert len(result["verify_results"]) == 2


def test_cmd_report_milestone_fixture_summarizes_the_run_failure():
    result = cmd_report(MILESTONE)
    assert result["ok"] is False
    assert result["run_error"] is not None
    assert result["states"]["L"] == "BLOCKED"


# --- main() / argument parsing -----------------------------------------------

def test_main_returns_0_on_success(capsys):
    code = main(["run", GEOMETRY])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True


def test_main_returns_1_on_failure(capsys):
    code = main(["run", MILESTONE])
    assert code == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False


def test_main_respects_target_flag(capsys):
    main(["check", GEOMETRY, "--target", "NCG"])
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True  # NCG preset still includes Phase 5's base graph primitives


# --- real subprocess invocation + canonical-registry isolation -------------

def test_real_subprocess_invocation_produces_valid_json():
    proc = subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "run", GEOMETRY],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=60)
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True


def test_cli_subprocess_never_touches_canonical_registries():
    before = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "run", GEOMETRY],
        cwd=ROOT, check=True, capture_output=True, timeout=60)
    after = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    assert before == after, "seit CLI modified a canonical registry file"
