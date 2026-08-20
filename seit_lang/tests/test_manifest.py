"""Tests for seit_lang.manifest (Phase 14)."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.cli import main
from seit_lang.manifest import build_manifest, write_manifest

FIXTURES = Path(__file__).parent / "fixtures"
GEOMETRY = str(FIXTURES / "geometry_pipeline.seit")
MILESTONE = str(FIXTURES / "spectral_test_complete.seit")

CANONICAL_FILES = [
    "equation_registry.json", "object_registry.json", "transformation_registry.json",
    "master_mdcl.json", "chainlink_registry.json", "protocol_registry.json",
]


def _without_timestamp(manifest: dict) -> dict:
    m = copy.deepcopy(manifest)
    m["provenance"].pop("timestamp_utc", None)
    return m


# --- structure: all the pieces the brief asks for ---------------------

def test_manifest_has_all_required_sections():
    manifest = build_manifest(GEOMETRY)
    for key in ("execution_manifest", "dependency_dag", "equation_registry",
                "variable_registry", "operator_registry", "status_registry",
                "provenance", "numerical_outputs", "audit_results", "verify_results"):
        assert key in manifest


def test_execution_manifest_reports_success_for_geometry_pipeline():
    manifest = build_manifest(GEOMETRY)
    assert manifest["execution_manifest"]["run_succeeded"] is True
    assert manifest["execution_manifest"]["module_name"] == "geometry_pipeline"


def test_dependency_dag_matches_real_compile_dag():
    from seit_lang.dag import compile_dag
    from seit_lang.parser import parse
    program = parse(Path(GEOMETRY).read_text())
    dag = compile_dag(program)
    manifest = build_manifest(GEOMETRY)
    assert manifest["dependency_dag"]["topological_order"] == dag.topological_order()


def test_variable_registry_includes_computed_nodes():
    manifest = build_manifest(GEOMETRY)
    assert manifest["variable_registry"]["L"]["type"] == "Laplacian"
    assert manifest["variable_registry"]["L"]["kind"] == "derived"


def test_operator_registry_only_includes_actually_called_transformations():
    manifest = build_manifest(GEOMETRY)
    assert "build_graph" in manifest["operator_registry"]
    assert "symmetric" in manifest["operator_registry"]
    # a transformation that exists in the target registry but is never
    # called in this program must NOT appear
    assert "construct_intersection_matrix" not in manifest["operator_registry"]


def test_operator_registry_records_real_source_provenance():
    manifest = build_manifest(GEOMETRY)
    source = manifest["operator_registry"]["build_graph"]["source"]
    assert "compiler.backends.graph_laplacian.build_graph" in source


def test_status_registry_combines_dag_state_and_declared_status():
    src = (
        'constant x: Scalar = 2.0; definition y = x * x; '
        'status y = VERIFIED; equation heat_eq: y == y;'
    )
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "prog.seit"
        f.write_text(src)
        manifest = build_manifest(str(f))
        assert manifest["status_registry"]["y"]["dag_state"] == "CALCULATED"
        assert manifest["status_registry"]["y"]["declared_status_statement"] == "VERIFIED"
        assert "heat_eq" in manifest["equation_registry"]
        assert manifest["equation_registry"]["heat_eq"]["type"] == "Equation"


def test_numerical_outputs_are_json_serializable():
    manifest = build_manifest(GEOMETRY)
    json.dumps(manifest["numerical_outputs"])  # must not raise


def test_verify_and_audit_results_present():
    manifest = build_manifest(GEOMETRY)
    assert len(manifest["verify_results"]) == 2
    assert all(r["passed"] is True for r in manifest["verify_results"])


# --- honest failure handling -------------------------------------------

def test_manifest_on_unresolved_input_reports_failure_not_a_crash():
    manifest = build_manifest(MILESTONE)
    assert manifest["execution_manifest"]["run_succeeded"] is False
    assert "B" in manifest["execution_manifest"]["run_error"]["error"]
    assert manifest["numerical_outputs"] == {}


def test_manifest_on_parse_error_still_returns_a_structured_result(tmp_path):
    bad = tmp_path / "bad.seit"
    bad.write_text("module m")  # missing semicolon
    manifest = build_manifest(str(bad))
    assert manifest["execution_manifest"]["run_succeeded"] is False
    assert manifest["dependency_dag"] is None


# --- reproducibility: pure function of (source, target, inputs) -----------

def test_manifest_is_reproducible_across_repeated_calls():
    m1 = build_manifest(GEOMETRY)
    m2 = build_manifest(GEOMETRY)
    assert _without_timestamp(m1) == _without_timestamp(m2)


def test_manifest_reflects_declared_inputs_not_hidden_state():
    B1 = np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    B2 = np.array([[2.0, 0.0], [0.0, 3.0]])
    m1 = build_manifest(MILESTONE, inputs={"B": B1})
    m2 = build_manifest(MILESTONE, inputs={"B": B2})
    assert m1["numerical_outputs"]["L"] != m2["numerical_outputs"]["L"]
    L1_expected = (B1 @ B1.T).tolist()
    assert m1["numerical_outputs"]["L"] == L1_expected


def test_manifest_declared_inputs_list_recorded():
    B = np.array([[1.0, 0.0], [0.0, 1.0]])
    manifest = build_manifest(MILESTONE, inputs={"B": B})
    assert manifest["execution_manifest"]["declared_inputs"] == ["B"]


# --- write_manifest / CLI "manifest" subcommand -----------------------------

def test_write_manifest_creates_file_with_expected_name(tmp_path):
    out_path = write_manifest(GEOMETRY, str(tmp_path))
    assert out_path.name == "geometry_pipeline.manifest.json"
    assert out_path.exists()
    on_disk = json.loads(out_path.read_text())
    assert on_disk["execution_manifest"]["run_succeeded"] is True


def test_cli_manifest_subcommand(tmp_path):
    code = main(["manifest", GEOMETRY, "--output-dir", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "geometry_pipeline.manifest.json").exists()


def test_manifest_subcommand_via_real_subprocess(tmp_path):
    proc = subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "manifest", GEOMETRY, "--output-dir", str(tmp_path)],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=60)
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert Path(payload["manifest_path"]).exists()


def test_manifest_subprocess_never_touches_canonical_registries(tmp_path):
    before = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "manifest", GEOMETRY, "--output-dir", str(tmp_path)],
        cwd=ROOT, check=True, capture_output=True, timeout=60)
    after = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    assert before == after, "seit manifest command modified a canonical registry file"
