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


def test_frontier_never_contains_falsified_nodes():
    """Brief testing item 17 (architecture doc section 8): a falsified
    candidate must never appear in the frontier as if it were an open
    target for new investigation. Checked against the real registries
    -- confirms the Phase 11 fix against the actual FALSIFIED nodes
    that exist in this repository, not just a synthetic fixture."""
    nodes_raw = client.get("/api/nodes").json()
    falsified_ids = {n["id"] for n in nodes_raw if n["status"] == "FALSIFIED"}
    assert falsified_ids, "expected at least one real FALSIFIED node in this repository to test against"

    frontier_ids = {e["id"] for e in client.get("/api/frontier").json()}
    assert not (falsified_ids & frontier_ids), (
        f"FALSIFIED node(s) leaked into the frontier: {falsified_ids & frontier_ids}"
    )


def test_falsified_and_failed_nodes_remain_queryable_but_never_deleted():
    """Brief testing item 17: excluded from the frontier is not the same
    as excluded from the system. A falsified/failed node must remain
    fully queryable via GET /api/nodes/:id forever."""
    nodes_raw = client.get("/api/nodes").json()
    terminal_ids = [n["id"] for n in nodes_raw if n["status"] in ("FAIL", "FALSIFIED")]
    assert terminal_ids, "expected at least one real FAIL/FALSIFIED node in this repository to test against"
    for nid in terminal_ids:
        r = client.get(f"/api/nodes/{nid}")
        assert r.status_code == 200
        assert r.json()["status"] in ("FAIL", "FALSIFIED")


def test_retriable_fail_nodes_remain_frontier_eligible():
    """The Phase 11 fix excludes only FALSIFIED (compiler's own
    ALLOWED_TRANSITIONS shows it has zero outgoing transitions) --
    FAIL is explicitly retriable and must NOT be swept out along with
    it. Confirmed against real FAIL nodes with fully-resolved
    dependencies in this repository."""
    nodes_raw = client.get("/api/nodes").json()
    status_by_id = {n["id"]: n["status"] for n in nodes_raw}
    admissible = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}
    fail_ids_with_resolved_deps = {
        n["id"] for n in nodes_raw
        if n["status"] == "FAIL" and all(status_by_id.get(d) in admissible for d in n["dependencies"])
    }
    assert fail_ids_with_resolved_deps, "expected at least one real FAIL node with resolved dependencies"

    frontier_ids = {e["id"] for e in client.get("/api/frontier").json()}
    assert fail_ids_with_resolved_deps <= frontier_ids, (
        f"retriable FAIL node(s) incorrectly excluded from frontier: {fail_ids_with_resolved_deps - frontier_ids}"
    )


def test_failed_dependency_propagation_blocks_downstream_frontier_eligibility():
    """Brief testing item 16's real console-side equivalent: this
    compiler has no scoped single-node execution endpoint to return a
    409 from (architecture doc section 6, point 2 -- every run is a
    full rebuild), so the observable form of "a FAIL/FALSIFIED upstream
    dependency blocks downstream execution" here is frontier exclusion,
    which mirrors the same admissibility check
    compiler/dependencies/graph.py::ExecutionGuard uses. Verified
    against a real chain in this repository: DESI-HEAT-TRACE depends on
    DESI-SPECTRUM, whose own status is FAIL -- so DESI-HEAT-TRACE must
    never appear in the frontier, and the blocking dependency's real
    (non-admissible) status must be visible, not hidden."""
    nodes_raw = client.get("/api/nodes").json()
    status_by_id = {n["id"]: n["status"] for n in nodes_raw}
    assert status_by_id.get("DESI-SPECTRUM") == "FAIL"

    downstream = next(n for n in nodes_raw if n["id"] == "DESI-HEAT-TRACE")
    assert "DESI-SPECTRUM" in downstream["dependencies"]

    frontier_ids = {e["id"] for e in client.get("/api/frontier").json()}
    assert "DESI-HEAT-TRACE" not in frontier_ids, (
        "DESI-HEAT-TRACE depends on FAIL node DESI-SPECTRUM but appeared in the frontier anyway"
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


def test_chainlink_arrows_expose_open_obligations_and_honest_gaps():
    """Phase 5: every arrow must carry open_obligations (real dependency
    gap, computed against the same admissible-status set as /api/frontier)
    plus an honest NOT_IMPLEMENTED marker for der_id (this compiler has
    no DER-id concept) and real literature crosswalk matches only where
    literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv actually names
    the node (Phase 9) -- never a fabricated link either way."""
    r = client.get("/api/chainlink")
    assert r.status_code == 200
    nodes = {n["id"]: n for n in client.get("/api/nodes").json()}
    admissible = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}
    crosswalk = client.get("/api/literature/crosswalk").json()
    crosswalk_node_ids = {row["mdcl_node_id"] for row in crosswalk}
    for arrow in r.json()["arrows"]:
        assert "open_obligations" in arrow
        assert "failures" in arrow
        to_node = nodes.get(arrow["to_id"])
        if to_node is not None:
            expected = [d for d in arrow["dependencies"] if nodes.get(d, {}).get("status") not in admissible]
            assert set(arrow["open_obligations"]) == set(expected), (
                f"open_obligations for {arrow['to_id']} disagree with a direct recomputation "
                f"against the real node statuses"
            )
        assert arrow["der_id"] is None
        assert arrow["der_id_note"]
        expected_has_literature = arrow["to_id"] in crosswalk_node_ids
        assert bool(arrow["literature"]) == expected_has_literature, (
            f"literature presence for {arrow['to_id']} disagrees with a direct recomputation "
            f"against the real crosswalk"
        )
        assert arrow["literature_note"]


def test_fc005_endpoint_is_verbatim_and_never_implies_closure():
    r = client.get("/api/fc005")
    assert r.status_code == 200
    body = r.json()
    assert body == _read("fc005_result.json")
    assert body["terminal_status"] != "CLOSED", (
        "FC-005 must never report CLOSED while the compiler itself does not"
    )


def test_only_the_known_mutating_routes_exist():
    """Brief section XVII: no 'mark as verified' button, no
    PATCH /api/nodes/:id/status -- and critically, no route anywhere
    that can set a node's status directly. Phase 6 added POST /api/runs
    (invokes the real compiler, nothing else). Phase 7 adds two more,
    both scoped to the Hypothesis Engine's own file
    (console_research/hypotheses.jsonl) and neither able to touch a
    registry: POST /api/hypotheses and POST /api/hypotheses/:id/transition.
    Every other route must stay GET-only forever."""
    mutating = {}
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        non_safe = methods - {"GET", "HEAD", "OPTIONS"}
        if non_safe:
            mutating[route.path] = non_safe
    expected = {
        "/api/runs": {"POST"},
        "/api/hypotheses": {"POST"},
        "/api/hypotheses/{hypothesis_id}/transition": {"POST"},
    }
    assert mutating == expected, f"expected exactly {expected}, found: {mutating}"
