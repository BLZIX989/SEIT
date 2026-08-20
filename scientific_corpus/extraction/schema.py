"""Record shapes for the Phase 14 mathematical extraction layer (brief
sections IV, IX, XI, XII, XIII, XXV). Every field is one this phase's
real extraction methods (literature-registry decomposition, PDF text
extraction) can honestly populate; fields the brief lists that nothing
here can responsibly fill (units, MathML, dimensional info beyond a
best-effort pass) are simply omitted rather than filled with a fabricated
or empty-but-implied value -- see scientific_corpus/extraction/__init__.py.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


def stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{h}"


@dataclass
class EquationRecord:
    equation_id: str
    source_id: str
    source_version: str | None
    document_id: str
    location: str                 # e.g. "p.9, eq.(1.1)" or "compiler:<path>"
    page: str | None
    section: str | None
    equation_label: str | None    # the source's own numbering, e.g. "(1.1)"
    extraction_method: str        # LATEX_SOURCE | PDF_TEXT_MATH | REGISTRY_INGESTION
    extraction_quality: str       # EXACT_LATEX | PDF_TEXT_MATH | OCR | ...
    source_status: str            # SOURCE_EXTRACTED | COMPILER_DERIVED | UNRESOLVED
    exact_representation: str     # the equation exactly as it occurs in the source
    surrounding_text: str
    variable_ids: list[str] = field(default_factory=list)
    operator_ids: list[str] = field(default_factory=list)
    structure_ids: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    dimensional_information: str = "NOT_EXTRACTED"
    provenance: str = ""
    equation_hash: str = ""

    def __post_init__(self):
        if not self.equation_hash:
            self.equation_hash = stable_id("H", self.source_id, self.location,
                                            self.exact_representation)[2:]

    def to_dict(self) -> dict[str, Any]:
        return {k: (list(v) if isinstance(v, list) else v) for k, v in self.__dict__.items()}


@dataclass
class SymbolOccurrence:
    """Brief section X: a symbol OCCURRENCE, never a globally-merged
    variable identity. Two occurrences of "G" in different equations are
    two separate records unless later, explicit semantic evidence links
    them -- which this phase does not attempt."""
    variable_id: str
    equation_id: str
    literal_symbol: str
    local_definition: str          # from the source's own text, "UNKNOWN" if not stated
    role: str                      # OPERATOR_TOKEN | VARIABLE_TOKEN (regex-category only)
    mathematical_type: str         # "UNRESOLVED" unless the source text explicitly names it
    source_id: str
    source_location: str
    extraction_method: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class OperatorOccurrence:
    operator_id: str
    equation_id: str
    symbol: str
    source_id: str
    source_location: str
    definition: str                # "UNKNOWN" unless stated
    extraction_method: str
    confidence: str
    algebraic_properties: str = "NOT_EXTRACTED"

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class RelationRecord:
    relation_id: str
    relation_type: str   # COMMUTATOR | ANTICOMMUTATOR | POISSON_BRACKET | ALGEBRAIC_IDENTITY | UNRESOLVED
    lhs: str
    rhs: str
    source_id: str
    equation_id: str
    assumptions: list[str] = field(default_factory=list)
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        d["assumptions"] = list(self.assumptions)
        return d


@dataclass
class StructureRecord:
    structure_id: str
    structure_type: str   # from the brief section XVIII vocabulary
    source_id: str
    source_location: str
    equation_ids: list[str]
    definition: str
    evidence: str          # the literal source text this was detected from
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        d["equation_ids"] = list(self.equation_ids)
        return d


@dataclass
class ReviewItem:
    review_id: str
    equation_id: str | None
    issue: str
    source_location: str
    machine_proposal: str
    unresolved_question: str
    status: str = "UNRESOLVED"

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class ChainCrosswalkRow:
    chain_position: str
    canonical_object: str
    source_id: str
    source_equation_id: str | None
    source_structure_id: str | None
    relationship: str
    evidence: str
    status: str    # SOURCE_SUPPORT | MULTI_SOURCE_SUPPORT | COMPILER_ONLY | OPEN | UNRESOLVED
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)
