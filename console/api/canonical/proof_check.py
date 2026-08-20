"""Proof Workspace support (brief section: Proof Workspace / Phase 8).

Two pieces, both computed live from the real registries -- nothing here
is a second, hand-maintained copy of compiler logic:

1. Circular-dependency detection: "Conclusion(T) in Premises(T)" --
   does a node's own id appear in its transitive dependency closure?
   The compiler's own dependency-graph guard
   (compiler/dependencies/graph.py::DependencyGraph._creates_cycle) and
   self_audit's dependency_audit already make this structurally
   impossible for a healthy build, so this should always report clean
   -- but the Proof Workspace re-checks it independently, per node, on
   demand, rather than trusting a single whole-corpus audit result: "the
   application must never manufacture closure merely because a UI
   element says complete."

2. A reference list of the compiler's real falsification protocols,
   pulled via `inspect` directly from compiler.falsification.protocols
   so it can never drift out of sync with a hand-typed duplicate.
"""
from __future__ import annotations

import inspect
from typing import Any


def check_circular_dependency(node_id: str, nodes: dict[str, dict]) -> dict[str, Any]:
    """DFS from node_id through its declared `dependencies`, looking for
    node_id itself. Returns the actual cycle path when found, not just a
    boolean, so a reviewer can see exactly which chain closes the loop."""
    start = nodes.get(node_id)
    if start is None:
        return {"is_circular": False, "cycle_path": None}

    stack: list[tuple[str, list[str]]] = [(d, [node_id, d]) for d in start.get("dependencies", [])]
    seen: set[str] = set()
    while stack:
        current, path = stack.pop()
        if current == node_id:
            return {"is_circular": True, "cycle_path": path}
        if current in seen:
            continue
        seen.add(current)
        for dep in nodes.get(current, {}).get("dependencies", []):
            stack.append((dep, path + [dep]))
    return {"is_circular": False, "cycle_path": None}


def falsification_protocol_reference() -> list[dict[str, str]]:
    from compiler.falsification import protocols

    names = [
        "structural_elimination_protocol",
        "representation_invariance_test",
        "mathematical_invariance_test",
        "observer_independent_structural_reduction",
    ]
    out = []
    for name in names:
        fn = getattr(protocols, name)
        doc = inspect.getdoc(fn) or ""
        summary = doc.strip().split("\n")[0] if doc.strip() else ""
        out.append({"name": name, "summary": summary})
    return out
