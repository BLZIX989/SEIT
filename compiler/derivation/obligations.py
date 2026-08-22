"""Proof obligations (Phase 5 of DERIVATION_ENGINE_SPEC.md section 4). Every
obligation is discharged by actually running its `check` callable -- a missing
check is honestly recorded as NOT_TESTED, never silently upgraded to
SATISFIED.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ObligationResult(str, Enum):
    SATISFIED = "SATISFIED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    NOT_TESTED = "NOT_TESTED"


@dataclass
class ProofObligation:
    obligation_id: str
    description: str
    check: Callable[[], bool] | None = None
    result: ObligationResult = ObligationResult.NOT_TESTED
    evidence: str = ""

    def discharge(self) -> "ProofObligation":
        """Runs `check` (if present) and sets result/evidence from its actual
        return value. Never upgrades a result without calling `check`."""
        if self.check is None:
            self.result = ObligationResult.NOT_TESTED
            self.evidence = "no check registered for this obligation"
            return self
        try:
            ok = bool(self.check())
        except Exception as exc:  # a raising check is a failed obligation, not a crash
            self.result = ObligationResult.FAILED
            self.evidence = f"check raised {type(exc).__name__}: {exc}"
            return self
        self.result = ObligationResult.SATISFIED if ok else ObligationResult.FAILED
        self.evidence = "check() returned True" if ok else "check() returned False"
        return self

    def to_dict(self) -> dict:
        return {
            "obligation_id": self.obligation_id,
            "description": self.description,
            "result": self.result.value,
            "evidence": self.evidence,
        }
