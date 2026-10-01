"""Invalidation engine (Phase 9 of the implementation plan). Turns the
existing leakage_control_audit's passive DETECTION (compiler/verification/
self_audit.py) into an active consequence at the Derivation-trace layer:
falsifying a node now visibly blocks its dependents, rather than merely
failing an audit if a human lets a falsified ancestor stay in the active DAG.

Reuses compiler.dependencies.graph.DependencyGraph unchanged -- its
.descendants() method already existed before this package (confirmed during
the Phase-1 audit) and did not need to be added.
"""
from __future__ import annotations

from compiler.dependencies.graph import DependencyGraph
from compiler.derivation.derivation import DerivationRegistry, DerivationStatus

TERMINAL_NO_OVERWRITE = {
    DerivationStatus.FALSIFIED, DerivationStatus.RETIRED, DerivationStatus.SUPERSEDED,
}


class InvalidationEngine:
    def __init__(self, derivations: DerivationRegistry):
        self.derivations = derivations

    def build_graph(self) -> DependencyGraph:
        g = DependencyGraph()
        for d in self.derivations:
            g.add_node(d.derivation_id)
        for d in self.derivations:
            for dep in d.dependencies:
                g.add_node(dep)
                g.add_dependency(d.derivation_id, dep)
        return g

    def on_falsified(self, node_id: str) -> list:
        """Walks graph.descendants(node_id) and marks every non-terminal
        descendant's Derivation BLOCKED. Never overwrites an already-terminal
        status (FALSIFIED/RETIRED/SUPERSEDED). Returns the list of
        derivation_ids newly blocked by this call."""
        graph = self.build_graph()
        blocked_ids = []
        for desc_id in graph.descendants(node_id):
            if desc_id not in self.derivations:
                continue
            d = self.derivations.get(desc_id)
            if d.status in TERMINAL_NO_OVERWRITE:
                continue
            d.status = DerivationStatus.BLOCKED
            prefix = f"{d.note} " if d.note else ""
            d.note = f"{prefix}BLOCKED: transitively depends on falsified '{node_id}'"
            blocked_ids.append(desc_id)
        return blocked_ids
