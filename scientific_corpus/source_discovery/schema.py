"""Record shapes for source discovery/acquisition (brief sections V, VI,
IX, XIV). Extends scientific_corpus.schema (Phase A/B) rather than
duplicating it -- DiscoveredSource is a superset used only inside this
subpackage; once a source is acquired it can be represented as a
scientific_corpus.schema.Source for the rest of the corpus.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

# Brief section XIV -- acquisition states. Never VERIFIED: verification
# belongs to the (not-yet-built) mathematical extraction/validation phase.
SOURCE_STATUS = (
    "DISCOVERED", "METADATA_ACQUIRED", "SOURCE_LOCATED", "ACQUISITION_PENDING",
    "ACQUIRED", "HASHED", "VERSIONED", "READY_FOR_EXTRACTION",
    "ACCESS_RESTRICTED", "LICENSE_RESTRICTED", "NOT_FOUND",
    "ACQUISITION_FAILED", "PARSE_UNSUPPORTED", "DISCOVERED_ONLY",
)


def stable_source_id(channel: str, external_id: str) -> str:
    """Deterministic, collision-resistant id -- never a raw URL string
    (brief section V: "Do not use URL strings as primary identity")."""
    h = hashlib.sha256(f"{channel}::{external_id}".encode("utf-8")).hexdigest()[:12]
    return f"SRC-{channel.upper()}-{h}"


@dataclass
class DiscoveryQuery:
    query_id: str
    domain: str
    subdomain: str
    structure_target: str
    query_text: str
    database: str
    date_executed: str | None = None
    result_count: int | None = None
    retrieval_status: str = "NOT_EXECUTED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id, "domain": self.domain, "subdomain": self.subdomain,
            "structure_target": self.structure_target, "query_text": self.query_text,
            "database": self.database, "date_executed": self.date_executed,
            "result_count": self.result_count, "retrieval_status": self.retrieval_status,
        }


@dataclass
class DiscoveredSource:
    source_id: str
    title: str
    authors: list[str]
    publication_year: str | None
    doi: str | None
    arxiv_id: str | None
    repository_id: str | None
    journal: str | None
    publisher: str | None
    abstract: str | None
    subject_categories: list[str]
    domain: str
    subdomain: str
    source_type: str               # "preprint" | "journal_version" | ...
    discovery_method: str          # "arxiv_api"
    discovery_query_id: str
    discovery_timestamp: str
    source_url: str | None
    fulltext_url: str | None       # PDF, when Allow'd by robots.txt
    source_package_url: str | None  # LaTeX e-print -- left None this slice (robots.txt disallow)
    access_status: str = "UNKNOWN"
    license_status: str = "UNKNOWN"
    version: str | None = None
    parent_source_id: str | None = None
    duplicate_group: str | None = None
    discovery_confidence: str = "EXACT_API_MATCH"
    acquisition_priority: int = 5   # 1 = highest, per brief section XV ordering
    acquisition_status: str = "DISCOVERED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id, "title": self.title, "authors": list(self.authors),
            "publication_year": self.publication_year, "doi": self.doi,
            "arxiv_id": self.arxiv_id, "repository_id": self.repository_id,
            "journal": self.journal, "publisher": self.publisher, "abstract": self.abstract,
            "subject_categories": list(self.subject_categories), "domain": self.domain,
            "subdomain": self.subdomain, "source_type": self.source_type,
            "discovery_method": self.discovery_method,
            "discovery_query_id": self.discovery_query_id,
            "discovery_timestamp": self.discovery_timestamp, "source_url": self.source_url,
            "fulltext_url": self.fulltext_url, "source_package_url": self.source_package_url,
            "access_status": self.access_status, "license_status": self.license_status,
            "version": self.version, "parent_source_id": self.parent_source_id,
            "duplicate_group": self.duplicate_group,
            "discovery_confidence": self.discovery_confidence,
            "acquisition_priority": self.acquisition_priority,
            "acquisition_status": self.acquisition_status,
        }


@dataclass
class AcquisitionManifest:
    source_id: str
    source_version: str | None
    source_hash: str            # sha256 of the actual acquired BYTES
    filename: str
    media_type: str
    source_url: str
    retrieval_timestamp: str
    retrieval_method: str       # "HTTP_GET_PDF"
    license: str
    access_status: str
    file_size: int
    parser_candidate: str       # "PDF_TEXT" | "NOT_YET_DETERMINED"
    parent_source_id: str | None = None
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id, "source_version": self.source_version,
            "source_hash": self.source_hash, "filename": self.filename,
            "media_type": self.media_type, "source_url": self.source_url,
            "retrieval_timestamp": self.retrieval_timestamp,
            "retrieval_method": self.retrieval_method, "license": self.license,
            "access_status": self.access_status, "file_size": self.file_size,
            "parser_candidate": self.parser_candidate,
            "parent_source_id": self.parent_source_id, "provenance": self.provenance,
        }


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
