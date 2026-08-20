"""Legitimate acquisition (brief section VIII/IX/XI). Only fetches
"/pdf" URLs -- arxiv.org's own robots.txt explicitly Allows "/pdf" and
"/abs" while Disallowing "/e-print" and "/src" for automated agents, so
LaTeX source packages are never fetched here (see
scientific_corpus/source_discovery/__init__.py). The declared
Crawl-delay: 15 for arxiv.org is enforced in code between PDF fetches,
separately from the arXiv API's own 3-second guidance (a different host,
different limit).
"""
from __future__ import annotations

import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from scientific_corpus.source_discovery.arxiv_client import RateLimiter
from scientific_corpus.source_discovery.schema import (
    AcquisitionManifest, DiscoveredSource, sha256_bytes,
)

_PDF_RATE_LIMITER = RateLimiter(min_interval_seconds=15.0)  # arxiv.org robots.txt Crawl-delay: 15

FetchPdfFn = Callable[[str], bytes]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_pdf_bytes(url: str, *, timeout: float = 30.0, max_retries: int = 2) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": "UOC-SEIT-research-corpus/0.1 (Phase 13 Phase C/D; "
                      "non-commercial academic research corpus construction)"
    })
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        _PDF_RATE_LIMITER.wait()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise
            last_exc = e
        except (urllib.error.URLError, TimeoutError) as e:
            last_exc = e
    assert last_exc is not None
    raise last_exc


def acquire_sources(
    sources: list[DiscoveredSource], out_dir: Path, *,
    max_acquisitions: int = 10, fetch_fn: FetchPdfFn = fetch_pdf_bytes,
) -> tuple[list[AcquisitionManifest], list[dict]]:
    """Acquires up to `max_acquisitions` sources (highest acquisition_priority
    first, i.e. lowest integer value), mutating each source's
    `acquisition_status` in place. Returns (manifests, failure_records) --
    failures are never silently dropped (brief section XL)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    # Skip sources already HASHED (idempotent re-run / cache reuse, brief
    # section XII) and sources linked to an existing project source or
    # already known to be inaccessible -- never re-fetch those.
    skip_statuses = {"HASHED", "ACCESS_RESTRICTED", "NOT_FOUND", "LICENSE_RESTRICTED",
                      "DISCOVERED_ONLY"}
    candidates = sorted(
        (s for s in sources if s.fulltext_url and s.acquisition_status not in skip_statuses),
        key=lambda s: (s.acquisition_priority, s.arxiv_id),
    )[:max_acquisitions]

    manifests: list[AcquisitionManifest] = []
    failures: list[dict] = []

    for source in candidates:
        source.acquisition_status = "ACQUISITION_PENDING"
        try:
            data = fetch_fn(source.fulltext_url)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                source.acquisition_status = "ACCESS_RESTRICTED"
                source.access_status = "ACCESS_RESTRICTED"
            elif e.code == 404:
                source.acquisition_status = "NOT_FOUND"
            else:
                source.acquisition_status = "ACQUISITION_FAILED"
            failures.append({
                "source_id": source.source_id, "arxiv_id": source.arxiv_id,
                "url": source.fulltext_url, "failure_type": type(e).__name__,
                "error": str(e), "timestamp": _now_iso(),
            })
            continue
        except Exception as e:  # noqa: BLE001 -- a real acquisition failure must be preserved, not raised
            source.acquisition_status = "ACQUISITION_FAILED"
            failures.append({
                "source_id": source.source_id, "arxiv_id": source.arxiv_id,
                "url": source.fulltext_url, "failure_type": type(e).__name__,
                "error": str(e), "timestamp": _now_iso(),
            })
            continue

        digest = sha256_bytes(data)
        filename = f"{source.source_id}.pdf"
        (out_dir / filename).write_bytes(data)
        source.acquisition_status = "HASHED"

        manifests.append(AcquisitionManifest(
            source_id=source.source_id, source_version=source.version,
            source_hash=f"sha256:{digest}", filename=filename, media_type="application/pdf",
            source_url=source.fulltext_url, retrieval_timestamp=_now_iso(),
            retrieval_method="HTTP_GET_PDF", license=source.license_status,
            access_status=source.access_status, file_size=len(data),
            parser_candidate="PDF_TEXT",
            provenance=f"acquired from arXiv PDF endpoint (robots.txt Allow: /pdf), "
                       f"arxiv_id={source.arxiv_id}{source.version or ''}",
        ))

    # Every source not selected for acquisition this run keeps its prior
    # acquisition_status (DISCOVERED) untouched -- never silently marked
    # as acquired.
    return manifests, failures
