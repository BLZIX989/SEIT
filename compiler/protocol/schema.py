"""Chainlink and Protocol record shapes (master brief section V, XVII).

Both are pure data + a `to_dict()` -- same shape convention as
`compiler/core/ir.py`'s IRNode subclasses -- but neither is an IRNode and
neither goes through `Status.can_transition()`. A Chainlink's status
fields are always COMPUTED from the real Transformation/Object/
FalsificationRecord it wraps (see
`compiler/protocol/derivation_chainlinks.py`), never asserted by hand.
That is the whole point of this module: it is impossible, by construction,
for a chainlink to claim a stronger result than the compiler itself
already produced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chainlink:
    chainlink_id: str
    source_node: str
    target_node: str
    transformation: str              # human-readable map, e.g. "L = D - A"
    mathematical_statement: str
    dependencies: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    # All four of these are computed from real registry data by the code
    # in derivation_chainlinks.py -- see that module for exactly which
    # field on which real record each one is read from.
    status: str = "OPEN"
    proof_status: str = "OPEN"
    calculation_status: str = "OPEN"
    falsification_status: str = "NOT_TESTED"

    executable_backend: str | None = None      # real module path, or None if not executed
    reproducibility: str = "N/A_NOT_EXECUTED"
    literature_support: list[dict] = field(default_factory=list)
    open_obligations: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)
    provenance_source: str = ""
    # "N/A" -- this chainlink makes no claim about a historical document;
    # "MISSING_SOURCE" -- a historical document is referenced but not
    #   present in this repository (never fabricated from memory);
    # "RECOVERED" -- reserved for when real source text is actually present.
    source_document_status: str = "N/A"

    def to_dict(self) -> dict[str, Any]:
        return {
            "chainlink_id": self.chainlink_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "transformation": self.transformation,
            "mathematical_statement": self.mathematical_statement,
            "dependencies": list(self.dependencies),
            "assumptions": list(self.assumptions),
            "status": self.status,
            "proof_status": self.proof_status,
            "calculation_status": self.calculation_status,
            "falsification_status": self.falsification_status,
            "executable_backend": self.executable_backend,
            "reproducibility": self.reproducibility,
            "literature_support": list(self.literature_support),
            "open_obligations": list(self.open_obligations),
            "failure_conditions": list(self.failure_conditions),
            "provenance_source": self.provenance_source,
            "source_document_status": self.source_document_status,
        }


@dataclass
class Protocol:
    protocol_id: str
    version: str
    name: str
    purpose: str
    inputs: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    primitives: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    algorithm: str = ""
    outputs: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    proof_obligations: list[str] = field(default_factory=list)
    falsification_criteria: list[str] = field(default_factory=list)
    literature: list[dict] = field(default_factory=list)
    execution_backend: str | None = None
    status_policy: str = (
        "Every status field this protocol exposes is read from the compiler's "
        "own Status machine (compiler/core/status.py) or from a Chainlink "
        "projection over it -- this protocol layer never assigns status."
    )
    reproducibility_policy: str = "Reported per-chainlink; see each chainlink's `reproducibility` field."
    chainlinks: list[str] = field(default_factory=list)     # chainlink_ids
    admissibility_conditions: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    registry_bindings: list[str] = field(default_factory=list)  # real registries/modules this protocol reads
    # See Chainlink.source_document_status for the meaning of these values.
    source_document_status: str = "MISSING_SOURCE"
    provenance_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "version": self.version,
            "name": self.name,
            "purpose": self.purpose,
            "inputs": list(self.inputs),
            "assumptions": list(self.assumptions),
            "primitives": list(self.primitives),
            "operators": list(self.operators),
            "algorithm": self.algorithm,
            "outputs": list(self.outputs),
            "invariants": list(self.invariants),
            "proof_obligations": list(self.proof_obligations),
            "falsification_criteria": list(self.falsification_criteria),
            "literature": list(self.literature),
            "execution_backend": self.execution_backend,
            "status_policy": self.status_policy,
            "reproducibility_policy": self.reproducibility_policy,
            "chainlinks": list(self.chainlinks),
            "admissibility_conditions": list(self.admissibility_conditions),
            "failure_modes": list(self.failure_modes),
            "registry_bindings": list(self.registry_bindings),
            "source_document_status": self.source_document_status,
            "provenance_note": self.provenance_note,
        }
