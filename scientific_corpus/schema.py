"""Record shapes for the scientific corpus (Phase 13, master brief
sections VI, IX, XXXI). Deliberately smaller than the brief's full field
lists: every field below is one this slice can populate HONESTLY from
data that already exists in this repository. Fields the brief asks for
that this slice cannot populate (units, dimensions, equivalence classes,
UOC translation, ...) are simply not present here yet -- adding an empty
or fabricated value for them would violate the brief's own section LVI
("do not fabricate completeness"). See scientific_corpus/__init__.py.

status_category values (brief section XXXI, the subset this slice
actually assigns -- never SOURCE_CLAIM promoted to MATHEMATICAL_THEOREM):
  COMPILER_DERIVED   -- produced by this repo's own compiler, traceable
                        to a real Status value in equation_registry.json
                        (never re-labeled upward).
  SOURCE_CLAIM       -- extracted from a literature source; the source's
                        own "textbook-established" language is preserved
                        verbatim in provenance_note, never converted into
                        this corpus's own truth claim.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def stable_hash(*parts: str) -> str:
    h = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


@dataclass
class Source:
    source_id: str
    title: str
    document_type: str          # "compiler_source_code" | "textbook_lecture_notes" | ...
    repository: str             # where it physically lives
    file_path: str | None = None
    file_hash: str | None = None
    authors: list[str] | None = None
    year: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    domain: str = "UNRESOLVED"
    version: str | None = None
    access_status: str = "UNKNOWN"
    acquisition_method: str = "PRIORITY_0_EXISTING_PROJECT_CORPUS"
    ingestion_status: str = "PARTIAL"   # never claim FULL unless independently verified
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id, "title": self.title,
            "document_type": self.document_type, "repository": self.repository,
            "file_path": self.file_path, "file_hash": self.file_hash,
            "authors": self.authors, "year": self.year, "doi": self.doi,
            "arxiv_id": self.arxiv_id, "domain": self.domain, "version": self.version,
            "access_status": self.access_status, "acquisition_method": self.acquisition_method,
            "ingestion_status": self.ingestion_status, "notes": self.notes,
        }


@dataclass
class CorpusEquation:
    equation_id: str            # SCIEQ-<hash>, this corpus's own id
    source_id: str
    source_equation_id: str     # the ORIGINAL id in its own registry -- never lost
    source_location: str        # page/section/equation_number if known, else "N/A"
    equation_latex_original: str
    equation_text: str
    domain: str
    subdomain: str | None
    status_category: str        # see module docstring -- COMPILER_DERIVED | SOURCE_CLAIM
    source_status_verbatim: str # the ORIGINAL status/claim, unmodified (e.g. compiler's
                                 # real Status.value, or the literature source's own
                                 # "textbook-established" language)
    extraction_method: str      # "REGISTRY_INGESTION" for this slice (Priority 0)
    extraction_confidence: str  # "EXACT" for direct JSON field copy
    semantic_confidence: str    # "NOT_ASSESSED" -- no semantic analysis performed this slice
    normalization_status: str = "RAW_ONLY"   # no normalization pipeline run yet (Phase G, not done)
    assumptions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    equation_hash: str = ""
    provenance_note: str = ""

    def __post_init__(self):
        if not self.equation_hash:
            self.equation_hash = stable_hash(self.source_id, self.source_equation_id,
                                              self.equation_latex_original)

    def to_dict(self) -> dict[str, Any]:
        return {
            "equation_id": self.equation_id, "source_id": self.source_id,
            "source_equation_id": self.source_equation_id, "source_location": self.source_location,
            "equation_latex_original": self.equation_latex_original,
            "equation_text": self.equation_text, "equation_hash": self.equation_hash,
            "domain": self.domain, "subdomain": self.subdomain,
            "status_category": self.status_category,
            "source_status_verbatim": self.source_status_verbatim,
            "extraction_method": self.extraction_method,
            "extraction_confidence": self.extraction_confidence,
            "semantic_confidence": self.semantic_confidence,
            "normalization_status": self.normalization_status,
            "assumptions": list(self.assumptions), "dependencies": list(self.dependencies),
            "provenance_note": self.provenance_note,
        }


@dataclass
class CorpusOperator:
    operator_id: str
    source_id: str
    source_transformation_id: str
    domain: str
    codomain: str
    action: str
    status_category: str
    source_status_verbatim: str
    extraction_method: str = "REGISTRY_INGESTION"
    provenance_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "operator_id": self.operator_id, "source_id": self.source_id,
            "source_transformation_id": self.source_transformation_id,
            "domain": self.domain, "codomain": self.codomain, "action": self.action,
            "status_category": self.status_category,
            "source_status_verbatim": self.source_status_verbatim,
            "extraction_method": self.extraction_method, "provenance_note": self.provenance_note,
        }


def write_jsonl(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r.to_dict() if hasattr(r, "to_dict") else r, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
