"""Frontier computation (brief section VII):

    F_t = { x not in C_t : Pred(x) subset C_t }

C_t is the set of nodes whose status is "resolved enough" to build on.
This is NOT a new definition invented for the console -- it is the
exact same set compiler/dependencies/graph.py::EXECUTABLE_UPSTREAM_STATUSES
already uses to gate execution (`ExecutionGuard.check`). Reusing the
literal value here (rather than re-deriving a similar-looking set)
guarantees the console's frontier can never disagree with what the
compiler itself would actually allow to execute next.
"""
from __future__ import annotations

# Mirrors compiler/dependencies/graph.py::EXECUTABLE_UPSTREAM_STATUSES exactly.
ADMISSIBLE_STATUSES = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}

# FALSIFIED is the one status with zero allowed outgoing transitions
# (compiler/core/status.py::ALLOWED_TRANSITIONS[Status.FALSIFIED] == set()):
# a falsified node can never become admissible again, so it must never
# appear in the frontier as if it were a fresh "next thing to
# investigate" (Phase 11 audit finding -- confirmed live against the
# real MDCL, where a FALSIFIED node was leaking into /api/frontier).
# FAIL is deliberately NOT excluded here: the compiler's own transition
# table explicitly allows FAIL -> OPEN/PROPOSED ("may be retried
# upstream"), so a FAIL node with resolved dependencies is a genuine
# retry candidate -- it belongs in the frontier, with its real status
# visible in the `status` field rather than disguised as untried.
EXCLUDED_FROM_FRONTIER_STATUSES = {"FALSIFIED"}


def compute_closed_set(nodes: dict[str, dict]) -> set[str]:
    return {nid for nid, n in nodes.items() if n.get("status") in ADMISSIBLE_STATUSES}


def compute_frontier(nodes: dict[str, dict], reverse_deps: dict[str, list[str]]) -> list[dict]:
    """Returns frontier entries sorted by id for deterministic output.

    A node is in the frontier iff:
      - it is NOT already in the closed set, AND
      - every one of its declared dependencies IS in the closed set
        (an isolated node with zero dependencies also qualifies).

    `downstream_unlock_count` is a transparent count of nodes that
    directly or transitively depend on this one -- it is reported as an
    input to ranking (brief section XV), never as a synthesized
    "scientific significance" score.
    """
    closed = compute_closed_set(nodes)
    frontier = []
    for nid, node in nodes.items():
        if nid in closed or node.get("status") in EXCLUDED_FROM_FRONTIER_STATUSES:
            continue
        deps = node.get("dependencies", [])
        unresolved = [d for d in deps if d not in closed]
        if unresolved:
            continue
        frontier.append({
            "id": nid,
            "kind": node.get("kind", ""),
            "status": node.get("status", ""),
            "unresolved_dependency_count": 0,
            "resolved_dependencies": list(deps),
            "downstream_unlock_count": _count_descendants(nid, reverse_deps),
        })
    frontier.sort(key=lambda e: e["id"])
    return frontier


def _count_descendants(node_id: str, reverse_deps: dict[str, list[str]]) -> int:
    seen: set[str] = set()
    stack = list(reverse_deps.get(node_id, []))
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(reverse_deps.get(n, []))
    return len(seen)
