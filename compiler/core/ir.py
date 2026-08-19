"""Canonical Intermediate Representation (spec section 8).

Three node kinds: Object, Transformation, Equation. All three carry
dependencies, provenance, and status so the dependency engine and
provenance engine can operate uniformly over them.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional

from compiler.core.status import Status


def _status_value(s: Status | str) -> str:
    return s.value if isinstance(s, Status) else Status(s).value


@dataclass
class Provenance:
    source: str
    source_version: str = ""
    object_id: str = ""
    equation_id: str = ""
    dependency_ids: list[str] = field(default_factory=list)
    transformation_id: str = ""
    calculation_id: str = ""
    execution_timestamp: str = ""
    git_commit: str = ""
    code_version: str = ""
    numerical_environment: dict[str, str] = field(default_factory=dict)
    status: str = Status.OPEN.value
    verification: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class IRNode:
    """Common fields shared by Object, Transformation, and Equation."""
    id: str
    status: Status = Status.OPEN
    dependencies: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    provenance: Optional[Provenance] = None
    # Declared role for the target-independence firewall (spec section 26):
    # "upstream_construction" (default) forbids downstream/observed terms;
    # "validation" | "comparison" | "falsification" | "observational_output"
    # permits them.
    role: str = "upstream_construction"

    def set_status(self, new_status: Status, *, force: bool = False) -> None:
        from compiler.core.status import can_transition
        if not force and not can_transition(self.status, new_status):
            raise ValueError(
                f"{self.id}: illegal status transition "
                f"{self.status.value} -> {new_status.value}"
            )
        self.status = new_status


@dataclass
class Object(IRNode):
    type: str = ""
    carrier: Any = None
    operations: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["status"] = _status_value(self.status)
        d["carrier"] = _safe_carrier(self.carrier)
        if self.provenance is not None:
            d["provenance"] = self.provenance.to_dict()
        return d


@dataclass
class Transformation(IRNode):
    domain: str = ""
    codomain: str = ""
    action: str = ""
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    proof: str = ""

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["status"] = _status_value(self.status)
        if self.provenance is not None:
            d["provenance"] = self.provenance.to_dict()
        return d


@dataclass
class Equation(IRNode):
    lhs: str = ""
    rhs: str = ""
    domain: str = ""
    derivation: str = ""
    verification: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["status"] = _status_value(self.status)
        if self.provenance is not None:
            d["provenance"] = self.provenance.to_dict()
        return d


def _safe_carrier(carrier: Any) -> Any:
    """Render a carrier JSON-safe; large numeric carriers are summarized."""
    if carrier is None or isinstance(carrier, (str, int, float, bool)):
        return carrier
    if isinstance(carrier, (list, tuple)):
        if len(carrier) > 32:
            return f"<carrier: {type(carrier).__name__} len={len(carrier)}>"
        return list(carrier)
    return f"<carrier: {type(carrier).__name__}>"
