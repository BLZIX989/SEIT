"""API-level tests against the real, live repository state.

These deliberately do NOT use synthetic fixtures for the endpoint tests
(brief section XXXII: no mock data for canonical state) -- they assert
the live API output against a fresh direct parse of the real registry
files, so a passing suite is evidence the API is not drifting from the
compiler's actual current state.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from console.api.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
client = TestClient(app)


def _read(name: str):
    return json.loads((REPO_ROOT / name).read_text())


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_state_matches_live_registries():
    r = client.get("/api/state")
    assert r.status_code == 200
    body = r.json()
    sm = _read("status_matrix.json")
    assert body["total_nodes"] == len(sm)
    by_status = {}
    for row in sm:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
    assert body["by_status"] == by_status
    audits = _read("self_audit_report.json")
    assert body["all_audits_passed"] == all(a["passed"] for a in audits)


def test_mdcl_is_verbatim():
    r = client.get("/api/mdcl")
    assert r.status_code == 200
    assert r.json() == _read("master_mdcl.json")


def test_nodes_list_count_matches_status_matrix():
    r = client.get("/api/nodes")
    assert r.status_code == 200
    assert len(r.json()) == len(_read("status_matrix.json"))


def test_node_detail_for_real_node():
    nodes = client.get("/api/nodes").json()
    assert nodes, "expected at least one real node"
    sample_id = nodes[0]["id"]
    r = client.get(f"/api/nodes/{sample_id}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == sample_id
    assert detail["superseding_nodes"] == []
    assert "NOT_IMPLEMENTED" in detail["superseding_nodes_note"]


def test_node_detail_404_for_unknown_node():
    r = client.get("/api/nodes/THIS-NODE-DOES-NOT-EXIST-XYZ")
    assert r.status_code == 404


def test_frontier_only_contains_non_admissible_nodes():
    r = client.get("/api/frontier")
    assert r.status_code == 200
    frontier = r.json()
    admissible = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}
    for entry in frontier:
        assert entry["status"] not in admissible, (
            f"{entry['id']} has admissible status {entry['status']} but appeared in frontier"
        )


def test_frontier_every_dependency_actually_resolved():
    """For every frontier entry, every listed resolved_dependencies id
    must itself have an admissible status in the live registries --
    otherwise the frontier computation would be lying about what is
    actually ready to investigate next."""
    nodes_raw = client.get("/api/nodes").json()
    status_by_id = {n["id"]: n["status"] for n in nodes_raw}
    admissible = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}

    frontier = client.get("/api/frontier").json()
    for entry in frontier:
        for dep in entry["resolved_dependencies"]:
            assert status_by_id.get(dep) in admissible, (
                f"{entry['id']} claims resolved dependency {dep} but its "
                f"actual status is {status_by_id.get(dep)}"
            )


def test_audits_endpoint_matches_file():
    r = client.get("/api/audits")
    assert r.status_code == 200
    assert r.json() == _read("self_audit_report.json")


def test_chainlink_arrows_reference_real_registered_nodes():
    r = client.get("/api/chainlink")
    assert r.status_code == 200
    body = r.json()
    assert len(body["arrows"]) > 0
    node_ids = {n["id"] for n in client.get("/api/nodes").json()}
    for arrow in body["arrows"]:
        assert arrow["from_id"] in node_ids, f"{arrow['from_id']} not a real registered node"
        assert arrow["to_id"] in node_ids, f"{arrow['to_id']} not a real registered node"
        assert arrow["execution_status"] in ("EXECUTED", "NOT_IMPLEMENTED")


def test_fc005_endpoint_is_verbatim_and_never_implies_closure():
    r = client.get("/api/fc005")
    assert r.status_code == 200
    body = r.json()
    assert body == _read("fc005_result.json")
    assert body["terminal_status"] != "CLOSED", (
        "FC-005 must never report CLOSED while the compiler itself does not"
    )


def test_no_mutating_routes_exist_in_phase_2():
    """Brief section XVII: no 'mark as verified' button. At the route
    level, this means: every registered API route must be GET-only."""
    methods_seen = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        if methods:
            methods_seen |= methods
    disallowed = methods_seen - {"GET", "HEAD", "OPTIONS"}
    assert not disallowed, f"Phase 2 must be read-only; found mutating methods: {disallowed}"
