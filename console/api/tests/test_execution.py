"""Tests for the Phase 6 execution package (the only write path in the
whole console). These never invoke the real compiler -- `build_fn` is
always a stub -- and always run against an isolated fixture repo root,
never the real registries, so running this suite has zero side effects
on real canonical state (unlike compiler/tests, which legitimately does
touch real files because that IS the thing under test there).
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from console.api.canonical import adapter
from console.api.execution import executor, ledger_store, runs_store
from console.api.main import app

EMPTY_REGISTRIES = {
    "type_registry.json": [],
    "object_registry.json": [],
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
    """Points adapter/runs_store/ledger_store at a throwaway directory
    seeded with minimal-but-valid empty registries, so tests never read
    or write the real repository's canonical state."""
    for name, content in EMPTY_REGISTRIES.items():
        (tmp_path / name).write_text(json.dumps(content))
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runs_store, "RUNS_DIR", tmp_path / "console_runs")
    monkeypatch.setattr(ledger_store, "LEDGER_PATH", tmp_path / "console_research" / "ledger.jsonl")
    return tmp_path


class _StubAudit:
    def __init__(self, name, passed, issues=None):
        self.name = name
        self.passed = passed
        self.issues = issues or []
        self.details = {}


def _stub_build_ok(repo_root: "object" = None):
    """A build_fn stand-in that mimics build_and_run()'s real return
    shape but writes a deterministic, known change to the fixture
    registries instead of running the real compiler."""
    def _make(repo_root):
        (repo_root / "object_registry.json").write_text(json.dumps([
            {"id": "NEW-OBJ", "status": "VERIFIED", "kind": "Object", "dependencies": [],
             "role": "upstream_construction", "type": "x"},
        ]))
        (repo_root / "falsification_registry.json").write_text(json.dumps([
            {"id": "FALS-NEW", "protocol": "x", "target": "NEW-OBJ", "passed": True, "detail": "", "evidence": {}},
        ]))
        (repo_root / "calculation_registry.json").write_text(json.dumps([
            {"id": "CALC-NEW", "kind": "x", "inputs": {}, "results": {}, "verification": {}, "status": "VERIFIED"},
        ]))
        (repo_root / "self_audit_report.json").write_text(json.dumps([
            {"name": "dependency_audit", "passed": True, "issues": [], "details": {}},
        ]))
        return {
            "terminal_status": SimpleNamespace(value="CONDITIONALLY_CLOSED"),
            "audit_results": [_StubAudit("dependency_audit", True)],
            "all_audits_passed": True,
        }
    return _make


def test_runs_store_id_sequencing_and_immutability(isolated_repo):
    assert runs_store.next_run_id() == "RUN-0001"
    runs_store.save({"run_id": "RUN-0001", "started_at": "t"})
    assert runs_store.next_run_id() == "RUN-0002"
    with pytest.raises(runs_store.RunAlreadyExistsError):
        runs_store.save({"run_id": "RUN-0001", "started_at": "t2"})
    assert runs_store.load("RUN-0001")["started_at"] == "t"
    assert runs_store.load("RUN-9999") is None
    assert [s["run_id"] for s in runs_store.load_all()] == ["RUN-0001"]


def test_ledger_append_only_and_tail(isolated_repo):
    assert ledger_store.tail() == []
    for i in range(5):
        ledger_store.append({"event_id": str(i), "timestamp": "t", "action": "RUN_STARTED"})
    assert len(ledger_store.all_events()) == 5
    assert [e["event_id"] for e in ledger_store.tail(2)] == ["3", "4"]


def test_diff_reports_added_changed_unchanged_nodes():
    pre = {"nodes": {"A": "OPEN", "B": "VERIFIED"},
           "falsification_ids": set(), "calculation_ids": set(), "audit_status": {"x": True}}
    post = {"nodes": {"A": "VERIFIED", "B": "VERIFIED", "C": "OPEN"},
            "falsification_ids": {"FALS-1"}, "calculation_ids": {"CALC-1"}, "audit_status": {"x": False}}
    diff = executor._diff(pre, post)
    assert diff["nodes_added"] == ["C"]
    assert diff["nodes_status_changed"] == [{"id": "A", "old_status": "OPEN", "new_status": "VERIFIED"}]
    assert diff["nodes_unchanged"] == 1  # B
    assert diff["new_falsifications"] == ["FALS-1"]
    assert diff["new_calculations"] == ["CALC-1"]
    assert diff["audit_deltas"] == ["x"]


def test_execute_full_rebuild_run_success(isolated_repo):
    stub = _stub_build_ok()
    snapshot = executor.execute_full_rebuild_run(build_fn=lambda: stub(isolated_repo))

    assert snapshot["run_id"] == "RUN-0001"
    assert snapshot["scope"] == "full_rebuild"
    assert snapshot["stopped_reason"] == "completed"
    assert snapshot["terminal_status"] == "CONDITIONALLY_CLOSED"
    assert snapshot["diff"]["nodes_added"] == ["NEW-OBJ"]
    assert snapshot["diff"]["new_falsifications"] == ["FALS-NEW"]
    assert snapshot["diff"]["new_calculations"] == ["CALC-NEW"]
    assert snapshot["pre_state_hash"] != snapshot["post_state_hash"]

    # persisted immutably
    assert runs_store.load("RUN-0001")["run_id"] == "RUN-0001"

    events = ledger_store.all_events()
    assert [e["action"] for e in events] == ["RUN_STARTED", "RUN_COMPLETED"]
    assert events[0]["run_id"] == "RUN-0001"
    assert events[1]["outputs"]["terminal_status"] == "CONDITIONALLY_CLOSED"


def test_execute_full_rebuild_run_records_error_without_raising(isolated_repo):
    def _boom():
        raise RuntimeError("simulated compiler crash")

    snapshot = executor.execute_full_rebuild_run(build_fn=_boom)

    assert snapshot["stopped_reason"] == "error"
    assert "simulated compiler crash" in snapshot["error"]
    assert snapshot["diff"] is None
    persisted = runs_store.load(snapshot["run_id"])
    assert persisted["stopped_reason"] == "error"
    events = ledger_store.all_events()
    assert events[-1]["action"] == "RUN_COMPLETED"
    assert events[-1]["status"] == "error"


def test_api_post_runs_end_to_end(isolated_repo, monkeypatch):
    """Full request/response cycle through the FastAPI route, with the
    real compiler substituted for a stub via monkeypatching
    compiler.run_compiler.build_and_run (the exact function
    executor.execute_full_rebuild_run lazily imports by default)."""
    import compiler.run_compiler as run_compiler_module

    stub = _stub_build_ok()
    monkeypatch.setattr(run_compiler_module, "build_and_run", lambda: stub(isolated_repo))

    client = TestClient(app)
    resp = client.post("/api/runs")
    assert resp.status_code == 201
    body = resp.json()
    assert body["run_id"] == "RUN-0001"
    assert body["scope"] == "full_rebuild"
    assert body["diff"]["nodes_added"] == ["NEW-OBJ"]

    list_resp = client.get("/api/runs")
    assert [r["run_id"] for r in list_resp.json()] == ["RUN-0001"]

    get_resp = client.get(f"/api/runs/{body['run_id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["run_id"] == "RUN-0001"

    missing_resp = client.get("/api/runs/RUN-9999")
    assert missing_resp.status_code == 404

    ledger_resp = client.get("/api/ledger")
    assert [e["action"] for e in ledger_resp.json()] == ["RUN_STARTED", "RUN_COMPLETED"]
