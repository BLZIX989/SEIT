"""Established-mathematics library (Phase 4 of DERIVATION_ENGINE_SPEC.md
section 3). A Theorem with `implemented=False` is registered honestly --
statement, hypotheses, conclusion, domain, and provenance are real and
citable -- but `check_applicable`/`apply` refuse to run it, raising
TheoremNotImplemented rather than silently treating it as usable. This is the
literal fix for the audit's item 25 finding (DOCUMENTATION ONLY: citations
exist as prose but nothing is queryable).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from compiler.derivation.obligations import ProofObligation
from compiler.derivation.types import MathObject, MathType


class TheoremNotImplemented(RuntimeError):
    pass


@dataclass
class Theorem:
    theorem_id: str
    statement: str
    hypotheses: list
    conclusion: str
    conclusion_type: MathType
    domain: str
    provenance: str
    implemented: bool = False
    applicability_check: Callable | None = None   # (bound: dict[str, MathObject]) -> bool
    transformation: Callable | None = None        # (bound) -> tuple[MathObject, list[ProofObligation]]

    def check_applicable(self, bound: dict) -> bool:
        if not self.implemented or self.applicability_check is None:
            raise TheoremNotImplemented(
                f"{self.theorem_id} is registered (statement + provenance only) but not implemented"
            )
        return bool(self.applicability_check(bound))

    def apply(self, bound: dict):
        if not self.implemented or self.transformation is None:
            raise TheoremNotImplemented(
                f"{self.theorem_id} is registered (statement + provenance only) but not implemented"
            )
        return self.transformation(bound)


class TheoremRegistry:
    def __init__(self):
        self._items: dict[str, Theorem] = {}

    def register(self, t: Theorem) -> Theorem:
        if t.theorem_id in self._items:
            raise ValueError(f"theorem registry: duplicate id '{t.theorem_id}'")
        self._items[t.theorem_id] = t
        return t

    def get(self, theorem_id: str) -> Theorem:
        return self._items[theorem_id]

    def __contains__(self, theorem_id: str) -> bool:
        return theorem_id in self._items

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def candidates_for(self, conclusion_type: MathType) -> list:
        """Preserves registration order -- the order theorems were added is
        the order the engine tries them in, per DERIVATION_ENGINE_SPEC.md
        section 5 step 3."""
        return [t for t in self._items.values() if t.conclusion_type == conclusion_type]
