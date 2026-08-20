"""Adapter-level tests: every read must match direct file parsing exactly."""
from __future__ import annotations

import json
from pathlib import Path

from console.api.canonical import adapter, frontier

REPO_ROOT = Path(__file__).resolve().parents[3]


def _read(name: str):
    return json.loads((REPO_ROOT / name).read_text())


def test_get_status_matrix_matches_file_exactly():
    assert adapter.get_status_matrix() == _read("status_matrix.json")


def test_get_master_mdcl_matches_file_exactly():
    assert adapter.get_master_mdcl() == _read("master_mdcl.json")


def test_get_self_audit_matches_file_exactly():
    assert adapter.get_self_audit() == _read("self_audit_report.json")


def test_all_nodes_merged_count_matches_status_matrix():
    nodes = adapter.get_all_nodes_merged()
    sm = _read("status_matrix.json")
    assert len(nodes) == len(sm)
    assert set(nodes.keys()) == {row["id"] for row in sm}


def test_all_nodes_merged_kind_matches_status_matrix():
    nodes = adapter.get_all_nodes_merged()
    sm = {row["id"]: row["kind"] for row in _read("status_matrix.json")}
    for nid, node in nodes.items():
        assert node["kind"] == sm[nid], f"{nid}: kind mismatch"


def test_reverse_dependency_index_is_consistent():
    nodes = adapter.get_all_nodes_merged()
    reverse = adapter.build_reverse_dependency_index(nodes)
    # every forward edge nid -> dep must appear as dep -> nid in reverse
    for nid, node in nodes.items():
        for dep in node.get("dependencies", []):
            assert nid in reverse.get(dep, []), f"{nid} missing from reverse[{dep}]"


def test_registry_not_found_raises_explicit_error(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    try:
        adapter.get_status_matrix()
        assert False, "expected RegistryNotFoundError"
    except adapter.RegistryNotFoundError as exc:
        assert "status_matrix.json" in str(exc)


def test_frontier_admissible_statuses_match_compiler_exactly():
    """The console's frontier admissibility set must be textually
    identical to the compiler's own EXECUTABLE_UPSTREAM_STATUSES --
    imported directly from compiler.dependencies.graph so a future edit
    to the compiler cannot silently desync the two."""
    from compiler.core.status import Status
    from compiler.dependencies.graph import EXECUTABLE_UPSTREAM_STATUSES

    compiler_set = {s.value for s in EXECUTABLE_UPSTREAM_STATUSES}
    assert frontier.ADMISSIBLE_STATUSES == compiler_set


def test_frontier_hand_computed_fixture():
    """A -> nothing (VERIFIED); B depends on A (OPEN); C depends on B (OPEN);
    D depends on A and Z where Z is missing/never-registered (treated as
    unresolved). Frontier should be exactly {B}."""
    nodes = {
        "A": {"kind": "Object", "status": "VERIFIED", "dependencies": []},
        "B": {"kind": "Object", "status": "OPEN", "dependencies": ["A"]},
        "C": {"kind": "Object", "status": "OPEN", "dependencies": ["B"]},
        "D": {"kind": "Object", "status": "OPEN", "dependencies": ["A", "Z"]},
    }
    reverse = adapter.build_reverse_dependency_index(nodes)
    result = frontier.compute_frontier(nodes, reverse)
    ids = [e["id"] for e in result]
    assert ids == ["B"], f"expected only B in frontier, got {ids}"


def test_frontier_excludes_already_admissible_nodes():
    nodes = {
        "A": {"kind": "Object", "status": "VERIFIED", "dependencies": []},
        "B": {"kind": "Object", "status": "CALCULATED", "dependencies": ["A"]},
    }
    reverse = adapter.build_reverse_dependency_index(nodes)
    result = frontier.compute_frontier(nodes, reverse)
    assert result == [], "VERIFIED/CALCULATED nodes must never appear in the frontier"


def test_frontier_excludes_falsified_but_retains_retriable_fail(monkeypatch):
    """Phase 11 audit finding: FALSIFIED has zero allowed outgoing
    transitions (compiler/core/status.py), so it can never become
    admissible again and must never appear as a frontier candidate.
    FAIL, by contrast, is explicitly retriable
    (ALLOWED_TRANSITIONS[Status.FAIL] == {OPEN, PROPOSED}) and must
    stay in the frontier once its dependencies resolve."""
    from compiler.core.status import ALLOWED_TRANSITIONS, Status

    # Assert the real compiler semantics this fix relies on, rather than
    # just asserting our own constant -- if the compiler ever changes
    # FALSIFIED's transitions, this test should fail loudly.
    assert ALLOWED_TRANSITIONS[Status.FALSIFIED] == set()
    assert Status.OPEN in ALLOWED_TRANSITIONS[Status.FAIL] or Status.PROPOSED in ALLOWED_TRANSITIONS[Status.FAIL]

    nodes = {
        "A": {"kind": "Object", "status": "VERIFIED", "dependencies": []},
        "RETRIABLE": {"kind": "Object", "status": "FAIL", "dependencies": ["A"]},
        "DEAD-END": {"kind": "Object", "status": "FALSIFIED", "dependencies": ["A"]},
    }
    reverse = adapter.build_reverse_dependency_index(nodes)
    result = frontier.compute_frontier(nodes, reverse)
    ids = [e["id"] for e in result]
    assert ids == ["RETRIABLE"], f"expected only the retriable FAIL node, got {ids}"


def test_falsification_matching_confidence_levels():
    fals = [
        {"id": "F1", "target": "NODE-X"},
        {"id": "F2", "target": "NODE-X-variant"},
        {"id": "F3", "target": "something containing NODE-X inside"},
        {"id": "F4", "target": "unrelated"},
    ]
    matches = adapter.find_falsifications_for_node("NODE-X", fals)
    confidences = {m["record"]["id"]: m["match_confidence"] for m in matches}
    assert confidences["F1"] == "exact_id"
    assert confidences["F2"] == "prefix_match"
    assert confidences["F3"] == "substring_match"
    assert "F4" not in confidences
