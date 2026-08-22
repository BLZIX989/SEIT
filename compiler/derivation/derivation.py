"""Derivation trace model (Phase 3 of DERIVATION_ENGINE_SPEC.md section 2/6).

A Derivation never records a bare "therefore X follows" -- it stores the
actual sequence of DerivationSteps, each naming the established-mathematics
rule invoked and the numeric/symbolic evidence produced. DerivationStatus is
additive: it governs Derivation records only and does not replace
compiler.core.status.Status, which continues to govern canonical Objects/
Transformations/Equations exactly as before this package existed (see
DERIVATION_ENGINE_SPEC.md section 6 for the one-directional mapping used only
at the moment a Derivation is registered into the canonical registries).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from compiler.derivation.obligations import ProofObligation


class DerivationStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    FORMALIZED = "FORMALIZED"
    DERIVABLE = "DERIVABLE"
    DERIVED = "DERIVED"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"
    CANONICAL = "CANONICAL"
    DERIVATION_FAILED = "DERIVATION_FAILED"
    FALSIFIED = "FALSIFIED"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    UNRESOLVED = "UNRESOLVED"


TERMINAL_DERIVATION_STATUSES = {DerivationStatus.FALSIFIED, DerivationStatus.RETIRED}


@dataclass
class DerivationStep:
    step_id: str
    rule_id: str
    input_ids: list
    output_id: str
    symbolic_form: str | None = None
    numeric_evidence: dict | None = None
    symbolic_evidence: dict | None = None

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id, "rule_id": self.rule_id,
            "input_ids": list(self.input_ids), "output_id": self.output_id,
            "symbolic_form": self.symbolic_form,
            "numeric_evidence": self.numeric_evidence,
            "symbolic_evidence": self.symbolic_evidence,
        }


@dataclass
class Derivation:
    derivation_id: str
    target_id: str
    inputs: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    definitions: list = field(default_factory=list)
    steps: list = field(default_factory=list)              # list[DerivationStep]
    proof_obligations: list = field(default_factory=list)  # list[ProofObligation]
    dependencies: list = field(default_factory=list)        # other derivation_ids
    provenance: dict = field(default_factory=dict)
    status: DerivationStatus = DerivationStatus.DOCUMENTED
    note: str = ""
    superseded_by: str | None = None   # set on an OLDER derivation once a
                                          # newer one is preferred; never deleted
    recovers: str | None = None         # set on a NEW derivation that was
                                          # produced by RecoveryEngine in
                                          # response to `recovers` falsifying/
                                          # blocking

    def to_dict(self) -> dict:
        return {
            "derivation_id": self.derivation_id,
            "target_id": self.target_id,
            "inputs": list(self.inputs),
            "assumptions": list(self.assumptions),
            "definitions": list(self.definitions),
            "steps": [s.to_dict() for s in self.steps],
            "proof_obligations": [o.to_dict() for o in self.proof_obligations],
            "dependencies": list(self.dependencies),
            "provenance": self.provenance,
            "status": self.status.value,
            "note": self.note,
            "superseded_by": self.superseded_by,
            "recovers": self.recovers,
        }


class DerivationRegistry:
    """Same id -> record, duplicate-guarded, to_list()/dump_json() shape as
    every other registry in this repository (compiler/ir/registry.py,
    compiler/protocol/registry.py) -- deliberately consistent, not a new
    convention."""

    def __init__(self):
        self._items: dict[str, Derivation] = {}

    def add(self, d: Derivation) -> Derivation:
        if d.derivation_id in self._items:
            raise ValueError(f"derivation registry: duplicate id '{d.derivation_id}'")
        self._items[d.derivation_id] = d
        return d

    def get(self, derivation_id: str) -> Derivation:
        return self._items[derivation_id]

    def __contains__(self, derivation_id: str) -> bool:
        return derivation_id in self._items

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def ids(self):
        return self._items.keys()

    def to_list(self) -> list:
        return [d.to_dict() for d in self._items.values()]

    def dump_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_list(), indent=2))
