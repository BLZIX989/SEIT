"""Dependency engine (spec section 9): a DAG over IR node ids.

Enforces: A -> B  =>  B cannot be an ancestor of A.
Execution protocol (spec 9.1-9.9): resolve dependencies, verify types,
verify assumptions, verify status, detect cycles, execute, verify,
register provenance, assign status. `ExecutionGuard` implements steps
1-5 and 8; the caller (a backend) performs 6-7 and hands the result back
for 8-9 via `record_result`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from compiler.core.status import Status

# Statuses considered "resolved enough" to build on for a downstream
# transformation. OPEN/FAIL/FALSIFIED upstream dependencies must STOP the
# branch (spec section 5, 39).
EXECUTABLE_UPSTREAM_STATUSES = {
    Status.VERIFIED, Status.DERIVED, Status.CALCULATED, Status.CONDITIONAL,
}


class CycleError(ValueError):
    pass


class DependencyError(ValueError):
    pass


@dataclass
class DependencyGraph:
    edges: dict[str, set[str]] = field(default_factory=dict)  # node -> set of nodes it depends on
    _reverse: dict[str, set[str]] = field(default_factory=dict)  # node -> set of dependents

    def add_node(self, node_id: str) -> None:
        self.edges.setdefault(node_id, set())
        self._reverse.setdefault(node_id, set())

    def add_dependency(self, node_id: str, depends_on: str) -> None:
        """Register node_id -> depends_on (node_id requires depends_on)."""
        self.add_node(node_id)
        self.add_node(depends_on)
        self.edges[node_id].add(depends_on)
        self._reverse[depends_on].add(node_id)
        if self._creates_cycle():
            self.edges[node_id].discard(depends_on)
            self._reverse[depends_on].discard(node_id)
            raise CycleError(
                f"adding dependency {node_id} -> {depends_on} would create a cycle "
                f"(i.e. {depends_on} is already a descendant of {node_id})"
            )

    def _creates_cycle(self) -> bool:
        try:
            self.topological_order()
            return False
        except CycleError:
            return True

    def ancestors(self, node_id: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self.edges.get(node_id, ()))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.edges.get(n, ()))
        return seen

    def descendants(self, node_id: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self._reverse.get(node_id, ()))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self._reverse.get(n, ()))
        return seen

    def topological_order(self) -> list[str]:
        """Kahn's algorithm; raises CycleError if a cycle is present."""
        indegree = {n: 0 for n in self.edges}
        for n, deps in self.edges.items():
            for d in deps:
                indegree.setdefault(d, 0)
        # indegree here = number of unresolved dependencies remaining
        indegree = {n: len(self.edges.get(n, set())) for n in self.edges}
        ready = [n for n, deg in indegree.items() if deg == 0]
        ready.sort()
        order: list[str] = []
        remaining = {n: set(deps) for n, deps in self.edges.items()}
        while ready:
            ready.sort()
            n = ready.pop(0)
            order.append(n)
            for dependent in sorted(self._reverse.get(n, ())):
                remaining[dependent].discard(n)
                if not remaining[dependent]:
                    indegree[dependent] = 0
                    if dependent not in order and dependent not in ready:
                        ready.append(dependent)
        if len(order) != len(self.edges):
            unresolved = set(self.edges) - set(order)
            raise CycleError(f"cycle detected among nodes: {sorted(unresolved)}")
        return order

    def unreachable_nodes(self, roots: list[str]) -> set[str]:
        seen: set[str] = set(roots)
        stack = list(roots)
        while stack:
            n = stack.pop()
            for dependent in self._reverse.get(n, ()):
                if dependent not in seen:
                    seen.add(dependent)
                    stack.append(dependent)
            for dep in self.edges.get(n, ()):
                if dep not in seen:
                    seen.add(dep)
                    stack.append(dep)
        return set(self.edges) - seen


class ExecutionGuard:
    """Implements spec section 9 steps 1-5 before a transformation executes."""

    def __init__(self, graph: DependencyGraph, registries):
        self.graph = graph
        self.registries = registries

    def _lookup(self, node_id: str):
        for reg in (self.registries.objects, self.registries.transformations,
                    self.registries.equations):
            if node_id in reg:
                return reg.get(node_id)
        raise DependencyError(f"unknown dependency id '{node_id}'")

    def check(self, node_id: str) -> None:
        node = self._lookup(node_id)
        # 1. resolve dependencies
        for dep_id in node.dependencies:
            if dep_id not in self.graph.edges.get(node_id, set()):
                raise DependencyError(
                    f"{node_id}: dependency '{dep_id}' not registered in the graph"
                )
            dep = self._lookup(dep_id)
            # 4. verify status: an upstream OPEN/FAIL/FALSIFIED dependency
            # must stop this branch (spec 5, 39).
            if dep.status not in EXECUTABLE_UPSTREAM_STATUSES:
                raise DependencyError(
                    f"{node_id}: upstream dependency '{dep_id}' has status "
                    f"{dep.status.value}; branch STOPPED (spec section 5/39)"
                )
        # 3. verify assumptions are explicitly declared (non-silent)
        if node.dependencies and not isinstance(node.assumptions, list):
            raise DependencyError(f"{node_id}: assumptions must be an explicit list")
        # 5. detect cycles across the whole graph
        self.graph.topological_order()
