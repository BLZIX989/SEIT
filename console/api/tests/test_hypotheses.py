"""Tests for the Phase 7 Hypothesis Engine. Like test_execution.py,
these run against an isolated fixture repo root and an isolated
hypotheses.jsonl -- never the real canonical state or the real
console_research/ directory.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from console.api.canonical import adapter
from console.api.main import app
from console.api.research import hypothesis_status, hypothesis_store

FIXTURE_REGISTRIES = {
    "type_registry.json": [],
    "object_registry.json": [
        {"id": "NODE-A", "status": "OPEN", "kind": "Object", "dependencies": [],
         "role": "upstream_construction", "type": "x"},
        {"id": "NODE-B", "status": "OPEN", "kind": "Object", "dependencies": [],
         "role": "upstream_construction", "type": "x"},
    ],
    "transformation_registry.json": [],
    "equation_registry.json": [],
    "status_matrix.json": [],
    "master_mdcl.json": {"types": [], "objects": [], "transformations": [], "equations": [], "status_matrix": []},
    "self_audit_report.json": [],
    "target_independence.json": {"findings": [], "n_flagged": 0},
    "proof_registry.json": [],
    "calculation_registry.json": [],
    "falsification_registry.json": [],
    "provenance_registry.json": {},
    "fc005_result.json": {"terminal_status": None},
}


@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    for name, content in FIXTURE_REGISTRIES.items():
        (tmp_path / name).write_text(json.dumps(content))
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(hypothesis_store, "HYPOTHESES_PATH", tmp_path / "console_research" / "hypotheses.jsonl")
    return tmp_path


@pytest.fixture
def client(isolated_repo):
    return TestClient(app)


def test_create_hypothesis_rejects_unknown_node(client):
    r = client.post("/api/hypotheses", json={"statement": "x depends on y", "target_node_id": "NOT-A-REAL-NODE"})
    assert r.status_code == 400


def test_create_hypothesis_for_real_node(client):
    r = client.post("/api/hypotheses", json={
        "statement": "NODE-A can be derived from a diffusion-distance construction",
        "target_node_id": "NODE-A",
        "assumptions": ["graph is connected"],
    })
    assert r.status_code == 201
    body = r.json()
    assert body["hypothesis"]["id"] == "HYP-0001"
    assert body["hypothesis"]["status"] == "PROPOSED"
    assert body["hypothesis"]["target_node_id"] == "NODE-A"
    assert body["possible_duplicates"] == []


def test_create_hypothesis_surfaces_possible_duplicates(client):
    stmt = "NODE-A can be derived from a diffusion-distance construction over the graph Laplacian"
    r1 = client.post("/api/hypotheses", json={"statement": stmt, "target_node_id": "NODE-A"})
    assert r1.status_code == 201

    # Same statement, same node -- must surface as an exact duplicate.
    r2 = client.post("/api/hypotheses", json={"statement": stmt, "target_node_id": "NODE-A"})
    assert r2.status_code == 201
    dupes = r2.json()["possible_duplicates"]
    assert len(dupes) == 1
    assert dupes[0]["id"] == "HYP-0001"
    assert dupes[0]["match_confidence"] == "exact_normalized_match"

    # Same statement targeting a DIFFERENT node must not be flagged.
    r3 = client.post("/api/hypotheses", json={"statement": stmt, "target_node_id": "NODE-B"})
    assert r3.json()["possible_duplicates"] == []


def test_valid_transition_succeeds_and_history_accumulates(client):
    hyp_id = client.post("/api/hypotheses", json={"statement": "s", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]

    r = client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "TESTING", "reason": "starting a numerical test"})
    assert r.status_code == 200
    assert r.json()["status"] == "TESTING"

    detail = client.get(f"/api/hypotheses/{hyp_id}").json()
    assert detail["current"]["status"] == "TESTING"
    assert [h["status"] for h in detail["history"]] == ["PROPOSED", "TESTING"]


def test_invalid_transition_is_rejected(client):
    hyp_id = client.post("/api/hypotheses", json={"statement": "s", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]
    # PROPOSED -> VERIFIED skips TESTING/SUPPORTED/DERIVED entirely.
    r = client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "VERIFIED", "reason": "nope"})
    assert r.status_code == 409


def test_terminal_status_cannot_transition_further(client):
    hyp_id = client.post("/api/hypotheses", json={"statement": "s", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]
    client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "REJECTED", "reason": "dead end"})
    r = client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "TESTING", "reason": "try again"})
    assert r.status_code == 409


def test_transition_unknown_hypothesis_404s(client):
    r = client.post("/api/hypotheses/HYP-9999/transition", json={"new_status": "TESTING", "reason": "x"})
    assert r.status_code == 404


def test_get_unknown_hypothesis_404s(client):
    assert client.get("/api/hypotheses/HYP-9999").status_code == 404


def test_list_hypotheses_filters_by_node_and_status(client):
    client.post("/api/hypotheses", json={"statement": "a1", "target_node_id": "NODE-A"})
    hb = client.post("/api/hypotheses", json={"statement": "b1", "target_node_id": "NODE-B"}).json()["hypothesis"]["id"]
    client.post(f"/api/hypotheses/{hb}/transition", json={"new_status": "TESTING", "reason": "go"})

    by_node = client.get("/api/hypotheses?target_node_id=NODE-A").json()
    assert [h["target_node_id"] for h in by_node] == ["NODE-A"]

    by_status = client.get("/api/hypotheses?status=TESTING").json()
    assert [h["id"] for h in by_status] == [hb]


def test_reason_is_never_lost_across_transitions(client):
    """Every transition's reason survives permanently in that line's
    provenance, even after later transitions overwrite the *current*
    line's provenance -- because the full jsonl history is retained."""
    hyp_id = client.post("/api/hypotheses", json={"statement": "s", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]
    client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "TESTING", "reason": "reason one"})
    client.post(f"/api/hypotheses/{hyp_id}/transition", json={"new_status": "FALSIFIED", "reason": "reason two"})

    history = client.get(f"/api/hypotheses/{hyp_id}").json()["history"]
    reasons = [h["provenance"].get("last_transition_reason") for h in history]
    assert reasons == [None, "reason one", "reason two"]


def test_historical_failure_rate_computed_from_terminal_hypotheses(isolated_repo, client):
    h1 = client.post("/api/hypotheses", json={"statement": "a1", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]
    h2 = client.post("/api/hypotheses", json={"statement": "a2", "target_node_id": "NODE-A"}).json()["hypothesis"]["id"]
    client.post(f"/api/hypotheses/{h1}/transition", json={"new_status": "REJECTED", "reason": "x"})
    client.post(f"/api/hypotheses/{h2}/transition", json={"new_status": "TESTING", "reason": "still going"})
    client.post(f"/api/hypotheses/{h2}/transition", json={"new_status": "SUPPORTED", "reason": "x"})
    client.post(f"/api/hypotheses/{h2}/transition", json={"new_status": "DERIVED", "reason": "x"})
    client.post(f"/api/hypotheses/{h2}/transition", json={"new_status": "VERIFIED", "reason": "x"})

    rates = hypothesis_store.historical_failure_rates()
    # Only h1 (REJECTED) is terminal at NODE-A; VERIFIED is not terminal
    # (a hypothesis can still be superseded later), so the rate is
    # computed over 1 terminal hypothesis, 1 of which failed.
    assert rates["NODE-A"] == 1.0
    assert "NODE-B" not in rates  # no terminal hypothesis for NODE-B at all


def test_status_machine_allows_documented_paths():
    assert hypothesis_status.can_transition("PROPOSED", "TESTING")
    assert hypothesis_status.can_transition("TESTING", "SUPPORTED")
    assert hypothesis_status.can_transition("SUPPORTED", "DERIVED")
    assert hypothesis_status.can_transition("DERIVED", "VERIFIED")
    assert hypothesis_status.can_transition("VERIFIED", "SUPERSEDED")
    assert not hypothesis_status.can_transition("PROPOSED", "DERIVED")
    assert not hypothesis_status.can_transition("REJECTED", "PROPOSED")
