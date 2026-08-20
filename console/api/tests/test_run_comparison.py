"""Tests for the Phase 10 run-vs-run comparison. Builds a small,
synthetic sequence of RunSnapshot records directly (via runs_store.save)
rather than running the real compiler -- the comparison logic only
needs to consume the stored diff/self_audit_result shape, so these
tests exercise it in isolation and fast.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from console.api.execution import run_comparison, runs_store
from console.api.main import app


def _snapshot(run_id, diff=None, self_audit_result=None, terminal_status="CONDITIONALLY_CLOSED"):
    return {
        "run_id": run_id, "started_at": "t", "completed_at": "t",
        "trigger": "full_rebuild", "scope": "full_rebuild", "target_node_ids": [],
        "pre_state_hash": "x", "post_state_hash": "y",
        "diff": diff, "test_suite_result": None,
        "self_audit_result": self_audit_result,
        "terminal_status": terminal_status, "stopped_reason": "completed", "error": None,
    }


@pytest.fixture
def isolated_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(runs_store, "RUNS_DIR", tmp_path / "console_runs")
    return tmp_path


@pytest.fixture
def client(isolated_runs):
    return TestClient(app)


def test_compare_merges_sequential_status_changes(isolated_runs):
    runs_store.save(_snapshot("RUN-0001", diff={
        "nodes_added": [], "nodes_status_changed": [], "nodes_unchanged": 0,
        "new_falsifications": [], "new_calculations": [], "audit_deltas": [],
    }))
    runs_store.save(_snapshot("RUN-0002", diff={
        "nodes_added": ["NEW-A"], "nodes_status_changed": [{"id": "A", "old_status": "OPEN", "new_status": "VERIFIED"}],
        "nodes_unchanged": 5, "new_falsifications": ["FALS-1"], "new_calculations": [], "audit_deltas": [],
    }))
    runs_store.save(_snapshot("RUN-0003", diff={
        "nodes_added": [], "nodes_status_changed": [{"id": "A", "old_status": "VERIFIED", "new_status": "DERIVED"}],
        "nodes_unchanged": 5, "new_falsifications": [], "new_calculations": ["CALC-1"], "audit_deltas": [],
    }))

    result = run_comparison.compare_runs("RUN-0001", "RUN-0003")
    assert result["runs_in_range"] == ["RUN-0002", "RUN-0003"]
    assert result["nodes_added"] == ["NEW-A"]
    assert result["nodes_status_changed"] == [{"id": "A", "old_status": "OPEN", "new_status": "DERIVED"}]
    assert result["new_falsifications"] == ["FALS-1"]
    assert result["new_calculations"] == ["CALC-1"]


def test_compare_excludes_net_no_op_changes(isolated_runs):
    runs_store.save(_snapshot("RUN-0001"))
    runs_store.save(_snapshot("RUN-0002", diff={
        "nodes_added": [], "nodes_status_changed": [{"id": "B", "old_status": "X", "new_status": "Y"}],
        "nodes_unchanged": 0, "new_falsifications": [], "new_calculations": [], "audit_deltas": [],
    }))
    runs_store.save(_snapshot("RUN-0003", diff={
        "nodes_added": [], "nodes_status_changed": [{"id": "B", "old_status": "Y", "new_status": "X"}],
        "nodes_unchanged": 0, "new_falsifications": [], "new_calculations": [], "audit_deltas": [],
    }))

    result = run_comparison.compare_runs("RUN-0001", "RUN-0003")
    assert result["nodes_status_changed"] == []  # B ended up back where it started


def test_compare_audit_deltas_computed_directly_not_accumulated(isolated_runs):
    runs_store.save(_snapshot("RUN-0001", self_audit_result=[
        {"name": "dependency_audit", "passed": True, "issues": [], "details": {}},
    ]))
    runs_store.save(_snapshot("RUN-0002"))  # audit flips to failing...
    runs_store.save(_snapshot("RUN-0003", self_audit_result=[
        {"name": "dependency_audit", "passed": False, "issues": ["x"], "details": {}},
    ]))

    result = run_comparison.compare_runs("RUN-0001", "RUN-0003")
    assert result["audit_deltas"] == ["dependency_audit"]
    assert result["from_terminal_status"] == "CONDITIONALLY_CLOSED"
    assert result["to_terminal_status"] == "CONDITIONALLY_CLOSED"


def test_compare_rejects_unknown_run_id(isolated_runs):
    runs_store.save(_snapshot("RUN-0001"))
    with pytest.raises(run_comparison.RunComparisonError):
        run_comparison.compare_runs("RUN-0001", "RUN-9999")
    with pytest.raises(run_comparison.RunComparisonError):
        run_comparison.compare_runs("RUN-9999", "RUN-0001")


def test_compare_rejects_out_of_order_range(isolated_runs):
    runs_store.save(_snapshot("RUN-0001"))
    runs_store.save(_snapshot("RUN-0002"))
    with pytest.raises(run_comparison.RunComparisonError):
        run_comparison.compare_runs("RUN-0002", "RUN-0001")
    with pytest.raises(run_comparison.RunComparisonError):
        run_comparison.compare_runs("RUN-0001", "RUN-0001")


def test_api_compare_endpoint(client):
    runs_store.save(_snapshot("RUN-0001"))
    runs_store.save(_snapshot("RUN-0002", diff={
        "nodes_added": ["X"], "nodes_status_changed": [], "nodes_unchanged": 0,
        "new_falsifications": [], "new_calculations": [], "audit_deltas": [],
    }))

    r = client.get("/api/runs/compare", params={"from_run_id": "RUN-0001", "to_run_id": "RUN-0002"})
    assert r.status_code == 200
    body = r.json()
    assert body["nodes_added"] == ["X"]
    assert body["runs_in_range"] == ["RUN-0002"]


def test_api_compare_endpoint_400_on_bad_range(client):
    runs_store.save(_snapshot("RUN-0001"))
    r = client.get("/api/runs/compare", params={"from_run_id": "RUN-0001", "to_run_id": "RUN-9999"})
    assert r.status_code == 400


def test_api_compare_route_does_not_collide_with_run_id_route(client):
    """'/api/runs/compare' must never be swallowed by GET /api/runs/{run_id}
    matching the literal string 'compare' as a run_id."""
    runs_store.save(_snapshot("RUN-0001"))
    runs_store.save(_snapshot("RUN-0002"))
    r = client.get("/api/runs/compare", params={"from_run_id": "RUN-0001", "to_run_id": "RUN-0002"})
    assert r.status_code == 200
    assert "from_run_id" in r.json()  # a RunComparison, not a 404 "no run with id 'compare'"
