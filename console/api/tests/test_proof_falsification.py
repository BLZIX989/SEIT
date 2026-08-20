"""Tests for the Phase 8 Proof / Falsification Workspaces. The real
repository's registered dependency graph is guaranteed acyclic by the
compiler's own construction-time guard, so a genuine positive
circular-dependency case can only be exercised against a synthetic
fixture -- these tests build one deliberately.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from console.api.canonical import adapter, proof_check
from console.api.main import app

# A -> B -> C -> A is a real cycle; D is clean and depends on an OPEN node.
FIXTURE_REGISTRIES = {
    "type_registry.json": [],
    "object_registry.json": [
        {"id": "A", "status": "OPEN", "kind": "Object", "dependencies": ["B"], "role": "upstream_construction", "type": "x"},
        {"id": "B", "status": "OPEN", "kind": "Object", "dependencies": ["C"], "role": "upstream_construction", "type": "x"},
        {"id": "C", "status": "OPEN", "kind": "Object", "dependencies": ["A"], "role": "upstream_construction", "type": "x"},
        {"id": "D", "status": "OPEN", "kind": "Object", "dependencies": ["E"], "role": "upstream_construction", "type": "x"},
        {"id": "E", "status": "VERIFIED", "kind": "Object", "dependencies": [], "role": "upstream_construction", "type": "x"},
    ],
    "transformation_registry.json": [
        {"id": "T-D", "status": "PROPOSED", "kind": "Transformation", "dependencies": ["E"],
         "role": "upstream_construction", "domain": "x", "codomain": "y", "action": "derive D",
         "preconditions": ["E must be admissible"], "postconditions": ["D holds"],
         "assumptions": ["graph is finite"], "proof": "by construction"},
    ],
    "equation_registry.json": [],
    "status_matrix.json": [],
    "master_mdcl.json": {"types": [], "objects": [], "transformations": [], "equations": [], "status_matrix": []},
    "self_audit_report.json": [],
    "target_independence.json": {"findings": [], "n_flagged": 0},
    "proof_registry.json": [
        {"id": "PROOF-T-D", "transformation_id": "T-D", "statement": "derive D", "method": "by construction", "status": "PROPOSED"},
    ],
    "calculation_registry.json": [],
    "falsification_registry.json": [
        {"id": "FALS-1", "protocol": "structural_elimination", "target": "D", "passed": False, "detail": "eliminated", "evidence": {}},
        {"id": "FALS-2", "protocol": "representation_invariance", "target": "E", "passed": True, "detail": "invariant held", "evidence": {}},
    ],
    "provenance_registry.json": {},
    "fc005_result.json": {"terminal_status": None},
}


@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    for name, content in FIXTURE_REGISTRIES.items():
        (tmp_path / name).write_text(json.dumps(content))
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    return tmp_path


@pytest.fixture
def client(isolated_repo):
    return TestClient(app)


# ---- unit tests: proof_check.py directly ----

def test_check_circular_dependency_detects_a_real_cycle():
    nodes = {
        "A": {"dependencies": ["B"]},
        "B": {"dependencies": ["C"]},
        "C": {"dependencies": ["A"]},
    }
    result = proof_check.check_circular_dependency("A", nodes)
    assert result["is_circular"] is True
    assert result["cycle_path"][0] == "A"
    assert result["cycle_path"][-1] == "A"


def test_check_circular_dependency_clean_graph_reports_false():
    nodes = {"D": {"dependencies": ["E"]}, "E": {"dependencies": []}}
    result = proof_check.check_circular_dependency("D", nodes)
    assert result == {"is_circular": False, "cycle_path": None}


def test_check_circular_dependency_unknown_node_reports_false():
    assert proof_check.check_circular_dependency("NOPE", {}) == {"is_circular": False, "cycle_path": None}


def test_falsification_protocol_reference_matches_real_module():
    from compiler.falsification import protocols
    refs = proof_check.falsification_protocol_reference()
    names = {r["name"] for r in refs}
    assert names == {
        "structural_elimination_protocol", "representation_invariance_test",
        "mathematical_invariance_test", "observer_independent_structural_reduction",
    }
    for r in refs:
        assert r["summary"]  # every real protocol has a non-empty docstring summary
        assert hasattr(protocols, r["name"])  # never a name the module doesn't actually define


# ---- API tests ----

def test_node_detail_flags_a_real_cycle(client):
    r = client.get("/api/nodes/A")
    assert r.status_code == 200
    cd = r.json()["circular_dependency"]
    assert cd["is_circular"] is True
    assert "A" in cd["cycle_path"]


def test_node_detail_clean_node_reports_no_cycle(client):
    r = client.get("/api/nodes/D")
    assert r.status_code == 200
    assert r.json()["circular_dependency"] == {"is_circular": False, "cycle_path": None}


def test_list_proofs_enriched_with_obligations_and_circularity(client):
    r = client.get("/api/proofs")
    assert r.status_code == 200
    proofs = r.json()
    assert len(proofs) == 1
    p = proofs[0]
    assert p["transformation_id"] == "T-D"
    assert p["preconditions"] == ["E must be admissible"]
    assert p["circular_dependency"]["is_circular"] is False
    # E is VERIFIED (admissible), so nothing is an open obligation.
    assert p["open_obligations"] == []


def test_get_proof_by_node_id(client):
    r = client.get("/api/proofs/T-D")
    assert r.status_code == 200
    assert r.json()["id"] == "PROOF-T-D"


def test_get_proof_404_for_node_without_one(client):
    assert client.get("/api/proofs/E").status_code == 404


def test_list_falsifications_includes_failed_records_and_protocol_reference(client):
    r = client.get("/api/falsifications")
    assert r.status_code == 200
    body = r.json()
    # A failed record is present, not filtered out -- "failed tests remain
    # permanently attached".
    assert any(rec["id"] == "FALS-1" and rec["passed"] is False for rec in body["records"])
    assert len(body["protocols"]) == 4
    assert all(p["summary"] for p in body["protocols"])
