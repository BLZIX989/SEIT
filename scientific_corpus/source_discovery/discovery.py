"""Discovery orchestration (brief section V/VII). Runs the query
registry against a fetch function (real network by default, injectable
for offline tests), parses results, and deduplicates by bare arXiv id
(brief section VII: prefer arXiv ID over title-similarity merging).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from scientific_corpus.source_discovery.arxiv_client import (
    ArxivEntry, fetch_raw, parse_atom_feed,
)
from scientific_corpus.source_discovery.queries import query_priorities
from scientific_corpus.source_discovery.schema import DiscoveredSource, DiscoveryQuery, stable_source_id

FetchFn = Callable[..., bytes]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_discovered_source(entry: ArxivEntry, query: DiscoveryQuery, priority: int) -> DiscoveredSource:
    return DiscoveredSource(
        source_id=stable_source_id("arxiv", entry.arxiv_id),
        title=entry.title,
        authors=entry.authors,
        publication_year=(entry.published or "")[:4] or None,
        doi=entry.doi,
        arxiv_id=entry.arxiv_id,
        repository_id=None,
        journal=None,
        publisher="arXiv",
        abstract=entry.summary,
        subject_categories=entry.categories,
        domain=query.domain,
        subdomain=query.subdomain,
        source_type="preprint",
        discovery_method="arxiv_api",
        discovery_query_id=query.query_id,
        discovery_timestamp=_now_iso(),
        source_url=entry.abs_url,
        fulltext_url=entry.pdf_url,
        source_package_url=None,  # robots.txt disallows /e-print -- see __init__.py
        access_status="OPEN_ACCESS_ARXIV",
        license_status="UNKNOWN_PER_PAPER",  # arXiv license varies per submission; not
                                              # determinable from search metadata alone
        version=entry.version,
        acquisition_priority=priority,
        acquisition_status="DISCOVERED",
    )


def run_discovery(
    queries: list[DiscoveryQuery], *, fetch_fn: FetchFn = fetch_raw, max_results_per_query: int = 8,
) -> tuple[list[DiscoveredSource], list[DiscoveryQuery], dict]:
    """Returns (unique sources, queries with results filled in, stats).
    `queries` is mutated in place (date_executed/result_count/
    retrieval_status) so the caller can persist the executed query log."""
    priorities = query_priorities()
    seen: dict[str, DiscoveredSource] = {}
    raw_hit_count = 0

    for q in queries:
        try:
            raw = fetch_fn(q.query_text, max_results=max_results_per_query)
            entries = parse_atom_feed(raw)
            q.date_executed = _now_iso()
            q.result_count = len(entries)
            q.retrieval_status = "OK"
        except Exception as exc:  # noqa: BLE001 -- a real query failure must be recorded, not raised past discovery
            q.date_executed = _now_iso()
            q.result_count = 0
            q.retrieval_status = f"FAILED: {type(exc).__name__}: {exc}"
            continue

        raw_hit_count += len(entries)
        for entry in entries:
            if entry.arxiv_id in seen:
                continue  # cross-query duplicate -- brief section VII: dedup by arXiv id
            seen[entry.arxiv_id] = _to_discovered_source(entry, q, priorities.get(q.query_id, 5))

    sources = sorted(seen.values(), key=lambda s: (s.acquisition_priority, s.arxiv_id))
    stats = {
        "queries_executed": sum(1 for q in queries if q.retrieval_status == "OK"),
        "queries_failed": sum(1 for q in queries if q.retrieval_status.startswith("FAILED")),
        "raw_hits_across_all_queries": raw_hit_count,
        "unique_sources_after_dedup": len(sources),
        "duplicate_hits_removed": raw_hit_count - len(sources),
    }
    return sources, queries, stats
