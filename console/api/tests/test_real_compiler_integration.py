"""Phase 11 audit item 8: a full `POST /api/runs` against the *real*,
non-stubbed compiler (compiler.run_compiler.build_and_run), with the
resulting RunSnapshot.diff checked against a diff computed independently
in this test -- by directly parsing the registry files before and after,
never by calling the same adapter/executor code the API itself uses.

This intentionally runs against the real repository's canonical state,
same as `compiler/tests` already does: the standard, accepted side effect
is timestamp/git_commit drift in the registry files, which the phase's
verification pass reverts with `git checkout --` once tests pass (see
UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 8 / the Phase 6-10 commit
history for this established pattern). console_runs/ and
console_research/ (ledger) are both gitignored, so the run record and
ledger entries this test creates are backed up and restored around the
test rather than left to accumulate.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from console.api.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = REPO_ROOT / "console_runs"
LEDGER_PATH = REPO_ROOT / "console_research" / "ledger.jsonl"

client = TestClient(app)


def _read(name: str):
    return json.loads((REPO_ROOT / name).read_text())


def _independent_pre_post_snapshot():
    """A direct parse of the exact same registry files the API reads,
    but performed here with zero shared code -- no adapter, no executor
    -- so this is a genuine independent cross-check of the API's diff,
    not a restatement of the same computation."""
    status_matrix = _read("status_matrix.json")
    node_status = {row["id"]: row["status"] for row in status_matrix}
    falsification_ids = {f["id"] for f in _read("falsification_registry.json")}
    calculation_ids = {c["id"] for c in _read("calculation_registry.json")}
    audit_status = {a["name"]: a["passed"] for a in _read("self_audit_report.json")}
    return node_status, falsification_ids, calculation_ids, audit_status


def test_post_runs_against_real_compiler_diff_matches_independent_computation(tmp_path):
    runs_backup = None
    if RUNS_DIR.exists():
        runs_backup = tmp_path / "console_runs_backup"
        shutil.copytree(RUNS_DIR, runs_backup)
    ledger_backup_text = LEDGER_PATH.read_text() if LEDGER_PATH.exists() else None

    try:
        pre_nodes, pre_fals, pre_calcs, pre_audits = _independent_pre_post_snapshot()

        resp = client.post("/api/runs")
        assert resp.status_code == 201
        body = resp.json()

        post_nodes, post_fals, post_calcs, post_audits = _independent_pre_post_snapshot()

        # Independently-derived diff, computed with none of executor._diff's code.
        expected_nodes_added = sorted(set(post_nodes) - set(pre_nodes))
        expected_status_changed = sorted(
            (
                {"id": nid, "old_status": pre_nodes[nid], "new_status": new_status}
                for nid, new_status in post_nodes.items()
                if nid in pre_nodes and pre_nodes[nid] != new_status
            ),
            key=lambda c: c["id"],
        )
        expected_unchanged = sum(
            1 for nid, new_status in post_nodes.items()
            if nid in pre_nodes and pre_nodes[nid] == new_status
        )
        expected_new_fals = sorted(post_fals - pre_fals)
        expected_new_calcs = sorted(post_calcs - pre_calcs)
        expected_audit_deltas = sorted(
            name for name, passed in post_audits.items() if pre_audits.get(name) != passed
        )

        diff = body["diff"]
        assert diff["nodes_added"] == expected_nodes_added
        assert diff["nodes_status_changed"] == expected_status_changed
        assert diff["nodes_unchanged"] == expected_unchanged
        assert diff["new_falsifications"] == expected_new_fals
        assert diff["new_calculations"] == expected_new_calcs
        assert diff["audit_deltas"] == expected_audit_deltas

        # This ran the real compiler end to end -- the terminal status it
        # reports must be one the compiler itself actually produces, and
        # the run must be durably retrievable exactly as returned.
        assert body["terminal_status"] in (
            "CONDITIONALLY_CLOSED", "CLOSED", "OPEN", "FAILED", "FALSIFIED",
        )
        assert body["stopped_reason"] == "completed"
        assert body["error"] is None

        get_resp = client.get(f"/api/runs/{body['run_id']}")
        assert get_resp.status_code == 200
        assert get_resp.json() == body

        ledger_events = client.get("/api/ledger").json()
        matching = [e for e in ledger_events if e.get("run_id") == body["run_id"]]
        assert [e["action"] for e in matching] == ["RUN_STARTED", "RUN_COMPLETED"]
    finally:
        if runs_backup is not None:
            shutil.rmtree(RUNS_DIR, ignore_errors=True)
            shutil.copytree(runs_backup, RUNS_DIR)
        elif RUNS_DIR.exists():
            shutil.rmtree(RUNS_DIR)

        if ledger_backup_text is not None:
            LEDGER_PATH.write_text(ledger_backup_text)
        elif LEDGER_PATH.exists():
            LEDGER_PATH.unlink()
