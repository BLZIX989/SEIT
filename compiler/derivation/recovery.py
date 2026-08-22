"""Recovery engine (Phase 10 of the implementation plan). Never mutates or
deletes a falsified/blocked Derivation -- it only ever adds a NEW Derivation
record, cross-referenced via `recovers`, and marks the old one SUPERSEDED
(never deleted; still readable in derivation_registry.json for audit) only
once the new one actually reaches VERIFIED/CANONICAL. If no admissible
alternative exists, `recover()` honestly returns a DERIVATION_FAILED record
and leaves the original BLOCKED -- "no currently admissible construction
exists" is a valid terminal answer (task section 9/23), never forced closed.
"""
from __future__ import annotations

from compiler.derivation.derivation import Derivation, DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.types import MathType


class RecoveryEngine:
    def __init__(self, engine: DerivationEngine):
        self.engine = engine

    def recover(
        self, blocked_derivation_id: str, target_type: MathType, bound: dict,
        *, exclude_theorem_ids: frozenset = frozenset(),
    ) -> Derivation:
        blocked = self.engine.derivations.get(blocked_derivation_id)
        new_id = f"{blocked_derivation_id}-recovery"
        d = self.engine.derive(
            new_id, target_type, bound,
            exclude_theorem_ids=exclude_theorem_ids,
            dependencies=list(blocked.dependencies),
        )
        d.recovers = blocked_derivation_id
        if d.status == DerivationStatus.VERIFIED:
            d.status = DerivationStatus.CANONICAL
            blocked.superseded_by = new_id
            if blocked.status == DerivationStatus.BLOCKED:
                blocked.status = DerivationStatus.SUPERSEDED
        # else: d.status is already an honest DERIVATION_FAILED/FALSIFIED/
        # CONDITIONAL from DerivationEngine.derive -- left as-is, and
        # `blocked` is left BLOCKED (not forced to SUPERSEDED) since no
        # admissible replacement was actually certified.
        return d
