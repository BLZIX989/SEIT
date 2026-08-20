"""The one write path in the whole console (architecture doc section 6).

`execute_full_rebuild_run()` does exactly three things: snapshot
canonical state, call the real `compiler.run_compiler.build_and_run()`
(dependency-injectable so tests never have to run the real compiler),
and snapshot canonical state again -- then computes a `RunDiff` from
the two snapshots' *actual content*, never from what the run "intended"
to do. There is no code path here that sets a node's status directly;
every status change in the diff is one the compiler itself already
wrote to disk via `Status.can_transition()`.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from console.api.canonical import adapter
from console.api.execution import ledger_store, runs_store

BuildFn = Callable[[], dict[str, Any]]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_event_id() -> str:
    return str(uuid.uuid4())


def _content_hash(action: str, inputs: dict, outputs: dict) -> str:
    payload = json.dumps({"action": action, "inputs": inputs, "outputs": outputs}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _registry_hash() -> str:
    """sha256 over every registry file's actual current bytes, in a
    fixed order -- a single number that changes iff anything on disk
    changed, independent of the structured diff below."""
    reg = adapter.load_all()
    payload = json.dumps(reg, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _snapshot_for_diff() -> dict[str, Any]:
    """Best-effort read of the pieces the diff needs. Returns an empty
    snapshot (not an error) if no registries exist yet -- the very
    first run in a fresh checkout has no "before" state to compare
    against, which is itself a true fact, not a failure."""
    try:
        nodes = adapter.get_all_nodes_merged()
        falsifications = adapter.get_falsifications()
        calculations = adapter.get_calculations()
        audits = adapter.get_self_audit()
    except adapter.RegistryNotFoundError:
        return {"nodes": {}, "falsification_ids": set(), "calculation_ids": set(), "audit_status": {}}
    return {
        "nodes": {nid: n.get("status") for nid, n in nodes.items()},
        "falsification_ids": {f["id"] for f in falsifications},
        "calculation_ids": {c["id"] for c in calculations},
        "audit_status": {a["name"]: a["passed"] for a in audits},
    }


def _diff(pre: dict[str, Any], post: dict[str, Any]) -> dict[str, Any]:
    pre_nodes, post_nodes = pre["nodes"], post["nodes"]

    nodes_added = sorted(set(post_nodes) - set(pre_nodes))
    nodes_status_changed = []
    nodes_unchanged = 0
    for nid, new_status in post_nodes.items():
        old_status = pre_nodes.get(nid)
        if old_status is None:
            continue  # already counted in nodes_added
        if old_status != new_status:
            nodes_status_changed.append({"id": nid, "old_status": old_status, "new_status": new_status})
        else:
            nodes_unchanged += 1

    new_falsifications = sorted(post["falsification_ids"] - pre["falsification_ids"])
    new_calculations = sorted(post["calculation_ids"] - pre["calculation_ids"])

    audit_deltas = sorted(
        name for name, passed in post["audit_status"].items()
        if pre["audit_status"].get(name) != passed
    )

    return {
        "nodes_added": nodes_added,
        "nodes_status_changed": sorted(nodes_status_changed, key=lambda c: c["id"]),
        "nodes_unchanged": nodes_unchanged,
        "new_falsifications": new_falsifications,
        "new_calculations": new_calculations,
        "audit_deltas": audit_deltas,
    }


def execute_full_rebuild_run(build_fn: BuildFn | None = None) -> dict[str, Any]:
    """Runs a full compiler rebuild and records exactly what changed.

    `build_fn` defaults to the real `compiler.run_compiler.build_and_run`
    -- imported lazily inside this function so importing this module
    never imports the (heavy) compiler package until a run is actually
    triggered, and so tests can substitute a stub.
    """
    if build_fn is None:
        from compiler.run_compiler import build_and_run
        build_fn = build_and_run

    run_id = runs_store.next_run_id()
    started_at = _now_iso()

    ledger_store.append({
        "event_id": _new_event_id(), "timestamp": started_at, "run_id": run_id,
        "actor": "system", "node_id": None, "action": "RUN_STARTED",
        "inputs": {"trigger": "full_rebuild"}, "outputs": {}, "status": "running",
        "provenance": {"source": "console/api/execution/executor.py"},
        "content_hash": _content_hash("RUN_STARTED", {"trigger": "full_rebuild"}, {}),
    })

    pre_diff_snapshot = _snapshot_for_diff()
    try:
        pre_state_hash = _registry_hash()
    except Exception:
        pre_state_hash = hashlib.sha256(b"").hexdigest()  # no prior registries at all yet

    snapshot: dict[str, Any] = {
        "run_id": run_id, "started_at": started_at, "completed_at": None,
        "trigger": "full_rebuild", "scope": "full_rebuild", "target_node_ids": [],
        "pre_state_hash": pre_state_hash, "post_state_hash": None,
        "diff": None, "test_suite_result": None, "self_audit_result": None,
        "terminal_status": None, "stopped_reason": None, "error": None,
    }

    try:
        result = build_fn()
    except Exception as exc:  # noqa: BLE001 -- must record the failure, not raise past the API boundary
        completed_at = _now_iso()
        snapshot["completed_at"] = completed_at
        snapshot["stopped_reason"] = "error"
        snapshot["error"] = f"{type(exc).__name__}: {exc}"
        runs_store.save(snapshot)
        ledger_store.append({
            "event_id": _new_event_id(), "timestamp": completed_at, "run_id": run_id,
            "actor": "system", "node_id": None, "action": "RUN_COMPLETED",
            "inputs": {}, "outputs": {"stopped_reason": "error", "error": snapshot["error"]},
            "status": "error", "provenance": {"source": "console/api/execution/executor.py"},
            "content_hash": _content_hash("RUN_COMPLETED", {}, {"stopped_reason": "error"}),
        })
        return snapshot

    completed_at = _now_iso()
    post_diff_snapshot = _snapshot_for_diff()
    post_state_hash = _registry_hash()
    diff = _diff(pre_diff_snapshot, post_diff_snapshot)

    terminal_status = result.get("terminal_status")
    terminal_status_value = terminal_status.value if hasattr(terminal_status, "value") else terminal_status
    audit_results = result.get("audit_results") or []
    self_audit_result = [
        {"name": a.name, "passed": a.passed, "issues": a.issues, "details": getattr(a, "details", {})}
        for a in audit_results
    ] if audit_results else None

    snapshot.update({
        "completed_at": completed_at,
        "post_state_hash": post_state_hash,
        "diff": diff,
        "self_audit_result": self_audit_result,
        "terminal_status": terminal_status_value,
        "stopped_reason": "completed",
    })
    runs_store.save(snapshot)

    ledger_store.append({
        "event_id": _new_event_id(), "timestamp": completed_at, "run_id": run_id,
        "actor": "system", "node_id": None, "action": "RUN_COMPLETED",
        "inputs": {},
        "outputs": {
            "terminal_status": terminal_status_value,
            "nodes_status_changed": len(diff["nodes_status_changed"]),
            "new_falsifications": len(diff["new_falsifications"]),
            "new_calculations": len(diff["new_calculations"]),
        },
        "status": "completed", "provenance": {"source": "console/api/execution/executor.py"},
        "content_hash": _content_hash("RUN_COMPLETED", {}, {"terminal_status": terminal_status_value}),
    })

    return snapshot
