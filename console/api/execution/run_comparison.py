"""Run-vs-run comparison (Phase 10, brief section XXVI). Merges the
real, already-stored per-run diffs across a range of runs -- no new
storage format, no reconstruction of historical state beyond what the
existing RunSnapshot records genuinely support.

A node that changed status more than once within the range nets out to
its earliest old_status and latest new_status; a node that ends up
back where it started (A -> B -> A across the range) is correctly
reported as unchanged, not as a spurious flip. Falsification/
calculation ids are permanent once created, so unioning each run's
own new_* lists across the range is exact, not approximate. Audit
deltas are computed directly from each run's stored self_audit_result
(a full snapshot already), not accumulated -- so that comparison is
always exact regardless of how many runs sit in between.
"""
from __future__ import annotations

from typing import Any

from console.api.execution import runs_store


class RunComparisonError(ValueError):
    """Raised for a nonexistent run id or an out-of-order range."""


def compare_runs(from_run_id: str, to_run_id: str) -> dict[str, Any]:
    all_runs = runs_store.load_all()
    ids = [r["run_id"] for r in all_runs]

    if from_run_id not in ids:
        raise RunComparisonError(f"no run with id '{from_run_id}'")
    if to_run_id not in ids:
        raise RunComparisonError(f"no run with id '{to_run_id}'")

    from_idx = ids.index(from_run_id)
    to_idx = ids.index(to_run_id)
    if to_idx <= from_idx:
        raise RunComparisonError(
            f"'{to_run_id}' must come after '{from_run_id}' (runs are compared in the order "
            f"they actually happened)"
        )

    runs_in_range = all_runs[from_idx + 1: to_idx + 1]

    nodes_added: set[str] = set()
    first_old: dict[str, str | None] = {}
    last_new: dict[str, str] = {}
    new_falsifications: set[str] = set()
    new_calculations: set[str] = set()

    for run in runs_in_range:
        diff = run.get("diff")
        if not diff:
            continue
        nodes_added.update(diff.get("nodes_added", []))
        for change in diff.get("nodes_status_changed", []):
            nid = change["id"]
            if nid not in first_old:
                first_old[nid] = change["old_status"]
            last_new[nid] = change["new_status"]
        new_falsifications.update(diff.get("new_falsifications", []))
        new_calculations.update(diff.get("new_calculations", []))

    nodes_status_changed = [
        {"id": nid, "old_status": first_old[nid], "new_status": last_new[nid]}
        for nid in sorted(last_new)
        if first_old[nid] != last_new[nid]  # nets to no-op (e.g. A -> B -> A) -- correctly excluded
    ]

    from_run = all_runs[from_idx]
    to_run = all_runs[to_idx]
    from_audits = {a["name"]: a["passed"] for a in (from_run.get("self_audit_result") or [])}
    to_audits = {a["name"]: a["passed"] for a in (to_run.get("self_audit_result") or [])}
    audit_deltas = sorted(name for name in to_audits if from_audits.get(name) != to_audits[name])

    return {
        "from_run_id": from_run_id,
        "to_run_id": to_run_id,
        "runs_in_range": [r["run_id"] for r in runs_in_range],
        "nodes_added": sorted(nodes_added),
        "nodes_status_changed": nodes_status_changed,
        "new_falsifications": sorted(new_falsifications),
        "new_calculations": sorted(new_calculations),
        "audit_deltas": audit_deltas,
        "from_terminal_status": from_run.get("terminal_status"),
        "to_terminal_status": to_run.get("terminal_status"),
    }
