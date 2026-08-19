#!/usr/bin/env python3
"""Part IX: node-level MDCL dependency-closure audit. For every node in
the live registries, determines: leaf vs intermediate, its own status
category, and whether it is transitively blocked by an unresolved
(non-VERIFIED/DERIVED/CALCULATED) dependency. Every value is computed
directly from object_registry.json / transformation_registry.json --
nothing is asserted.

Category mapping (this Status enum has no literal CLOSED value --
compiler/core/status.py defines VERIFIED/DERIVED/CALCULATED/
CONDITIONAL/PROPOSED/OPEN/FAIL/FALSIFIED only; TerminalStatus, a
SEPARATE enum, has CLOSED/PARTIALLY_CLOSED/CONDITIONALLY_CLOSED/
FALSIFIED but applies only to the overall build, never an individual
node). For this audit, "closed" is defined as the strongest node-level
states this schema actually has: VERIFIED, DERIVED, CALCULATED.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CLOSED_LIKE = {"VERIFIED", "DERIVED", "CALCULATED"}
FIELDS = ["id", "kind", "status", "is_leaf", "is_intermediate", "n_dependencies",
          "n_dependents", "category", "blocked", "blocking_dependencies"]


def load(name):
    return json.loads((ROOT / name).read_text())


def main():
    objs = load("object_registry.json")
    trans = load("transformation_registry.json")
    all_nodes = [dict(n, kind="Object") for n in objs] + [dict(n, kind="Transformation") for n in trans]

    status_by_id = {n["id"]: n["status"] for n in all_nodes}
    # NOTE: the registry's actual field is "dependencies" -- "dependency_ids" only
    # exists nested inside provenance and is unrelated. Found and fixed during this
    # campaign's own audit: an earlier draft of this script read the wrong key and
    # silently produced an empty dependency graph (0 closed_intermediate, 0 blocked).
    deps_by_id = {n["id"]: (n.get("dependencies") or []) for n in all_nodes}

    # dependents: who points AT this node
    dependents = {n["id"]: [] for n in all_nodes}
    for n in all_nodes:
        for dep in deps_by_id[n["id"]]:
            if dep in dependents:
                dependents[dep].append(n["id"])

    def ancestors(node_id, seen=None):
        seen = seen or set()
        for dep in deps_by_id.get(node_id, []):
            if dep not in seen:
                seen.add(dep)
                ancestors(dep, seen)
        return seen

    rows = []
    counts = {"closed_leaf": 0, "closed_intermediate": 0, "open": 0, "conditional": 0,
              "failed_retriable": 0, "falsified": 0, "proposed": 0, "blocked": 0,
              "superseded": 0}

    for n in all_nodes:
        node_id = n["id"]
        status = n["status"]
        n_deps = len(deps_by_id[node_id])
        n_dependents = len(dependents[node_id])
        is_leaf = n_dependents == 0
        is_intermediate = not is_leaf

        anc = ancestors(node_id)
        blocking = sorted(a for a in anc if status_by_id.get(a) not in CLOSED_LIKE)
        blocked = bool(blocking) and status in CLOSED_LIKE
        # A CLOSED_LIKE node is "improperly" closed if it has an unresolved ancestor --
        # this is exactly what leakage_control_audit already guards against for
        # FAIL/FALSIFIED ancestors specifically; here we report ANY non-closed ancestor
        # (including OPEN/PROPOSED/CONDITIONAL) for full transparency.

        if status == "FALSIFIED":
            category = "falsified"
            counts["falsified"] += 1
        elif status == "FAIL":
            category = "failed_retriable"
            counts["failed_retriable"] += 1
        elif status == "CONDITIONAL":
            category = "conditional"
            counts["conditional"] += 1
        elif status == "PROPOSED":
            category = "proposed"
            counts["proposed"] += 1
        elif status == "OPEN":
            category = "open"
            counts["open"] += 1
        elif status in CLOSED_LIKE:
            category = "closed_leaf" if is_leaf else "closed_intermediate"
            counts[category] += 1
        else:
            category = f"UNKNOWN_STATUS({status})"

        if blocked:
            counts["blocked"] += 1

        rows.append({
            "id": node_id, "kind": n["kind"], "status": status, "is_leaf": is_leaf,
            "is_intermediate": is_intermediate, "n_dependencies": n_deps,
            "n_dependents": n_dependents, "category": category, "blocked": blocked,
            "blocking_dependencies": ";".join(blocking) if blocking else "",
        })

    csv_path = ROOT / "DEPENDENCY_CLOSURE_AUDIT.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {csv_path} ({len(rows)} rows)")
    print()
    print("Category counts:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print()
    print(f"SUPERSEDED status: not present in compiler/core/status.py's Status enum at all "
          f"-- 0 nodes can carry it. This is reported explicitly (see report) rather than "
          f"silently omitted.")

    return rows, counts


if __name__ == "__main__":
    main()
