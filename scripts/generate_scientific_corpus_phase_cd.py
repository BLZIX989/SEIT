"""Phase 13, Phases C+D (master brief): scientific literature discovery
+ legitimate acquisition. Extends the Phase A/B corpus
(scripts/generate_scientific_corpus_phase_ab.py) -- does not duplicate
or overwrite it.

Two modes:
  --live (default): real network calls against the arXiv API and PDF
    endpoint, rate-limited per scientific_corpus/source_discovery/
    __init__.py's documented discipline.
  --offline-fixture: no network at all -- discovery reads a bundled
    Atom XML fixture, acquisition writes synthetic byte content. Used
    by the test suite (scientific_corpus/tests/test_source_discovery.py)
    to prove, deterministically and without network dependency, that
    running this script never touches a canonical compiler registry.

This script does NOT extract equations, normalize anything, or run
equivalence analysis (brief section XIX: "Do NOT proceed yet"). It only
produces source-layer evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.schema import read_jsonl, write_jsonl, Source
from scientific_corpus.source_discovery.acquisition import acquire_sources, fetch_pdf_bytes
from scientific_corpus.source_discovery.arxiv_client import fetch_raw
from scientific_corpus.source_discovery.crosswalk import link_existing_sources
from scientific_corpus.source_discovery.discovery import run_discovery
from scientific_corpus.source_discovery.queries import build_query_registry
from scientific_corpus.source_discovery.schema import DiscoveredSource

# Phase A/B's existing corpus (sources.jsonl) is always read from the
# real repository -- it is read-only input, never mutated by this
# script, so isolating it in tests is unnecessary. Everything this
# script WRITES goes under `output_root` (default: the real repo;
# overridden to a tmp_path by tests so no test run ever touches real
# repository data -- see scientific_corpus/tests/test_source_discovery.py).
AB_CORPUS_DIR = ROOT / "data" / "scientific_corpus"
FIXTURE_XML = ROOT / "scientific_corpus" / "tests" / "fixtures" / "arxiv_atom_sample.xml"

SOFTWARE_VERSION = "phase13-source-discovery-0.1.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _offline_fetch_raw(query_text: str, max_results: int = 8) -> bytes:
    return FIXTURE_XML.read_bytes()


def _offline_fetch_pdf(url: str) -> bytes:
    return f"OFFLINE_FIXTURE_PDF_STUB for {url}".encode("utf-8")


def _write_xlsx(path: Path, sheet_name: str, fieldnames: list[str], rows: list[dict]) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(fieldnames)
    for row in rows:
        ws.append([row.get(k, "") for k in fieldnames])
    wb.save(path)


def _hash_records(records: list[dict]) -> str:
    payload = json.dumps(records, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(*, offline: bool, max_results_per_query: int, max_acquisitions: int,
         output_root: Path = ROOT) -> dict:
    fetch_raw_fn = _offline_fetch_raw if offline else fetch_raw
    fetch_pdf_fn = _offline_fetch_pdf if offline else fetch_pdf_bytes

    corpus_dir = output_root / "data" / "scientific_corpus"
    discovery_dir = corpus_dir / "sources" / "discovery"
    raw_dir = corpus_dir / "sources" / "raw"
    manifest_dir = corpus_dir / "sources" / "manifests"
    failures_dir = corpus_dir / "sources" / "failures"

    existing_sources = [Source(**row) for row in read_jsonl(AB_CORPUS_DIR / "sources" / "sources.jsonl")]

    queries = build_query_registry()
    discovered, executed_queries, discovery_stats = run_discovery(
        queries, fetch_fn=fetch_raw_fn, max_results_per_query=max_results_per_query,
    )
    discovered, links = link_existing_sources(discovered, existing_sources)

    manifests, failures = acquire_sources(
        discovered, raw_dir, max_acquisitions=max_acquisitions, fetch_fn=fetch_pdf_fn,
    )

    discovery_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    failures_dir.mkdir(parents=True, exist_ok=True)
    (corpus_dir / "coverage").mkdir(parents=True, exist_ok=True)

    write_jsonl(discovered, discovery_dir / "SCIENTIFIC_SOURCE_DISCOVERY_REGISTRY.jsonl")
    write_jsonl(executed_queries, discovery_dir / "query_registry.jsonl")
    write_jsonl(manifests, manifest_dir / "acquisition_manifests.jsonl")
    (failures_dir / "acquisition_failures.jsonl").write_text(
        "\n".join(json.dumps(f, sort_keys=True) for f in failures) + ("\n" if failures else "")
    )
    (discovery_dir / "existing_source_links.json").write_text(json.dumps(links, indent=2))

    # Coverage matrix (brief section XVI)
    by_domain: dict[str, dict] = {}
    for s in discovered:
        key = (s.domain, s.subdomain)
        row = by_domain.setdefault(key, {
            "domain": s.domain, "subdomain": s.subdomain, "structure_target": s.subdomain,
            "sources_discovered": 0, "sources_metadata_acquired": 0,
            "sources_fulltext_acquired": 0, "machine_readable_sources": 0,
            "latex_sources": 0, "xml_sources": 0, "mathml_sources": 0, "pdf_sources": 0,
            "inaccessible_sources": 0, "acquisition_failures": 0,
        })
        row["sources_discovered"] += 1
        row["sources_metadata_acquired"] += 1
        if s.acquisition_status == "HASHED":
            row["sources_fulltext_acquired"] += 1
            row["pdf_sources"] += 1
        if s.acquisition_status in ("ACCESS_RESTRICTED", "LICENSE_RESTRICTED"):
            row["inaccessible_sources"] += 1
        if s.acquisition_status in ("ACQUISITION_FAILED", "NOT_FOUND"):
            row["acquisition_failures"] += 1

    def coverage_status(row: dict) -> str:
        if row["sources_fulltext_acquired"] > 0:
            return "MACHINE_READABLE" if row["pdf_sources"] == row["sources_fulltext_acquired"] else "SUBSTANTIAL"
        if row["sources_discovered"] > 0:
            return "DISCOVERY_ONLY"
        return "NOT_STARTED"

    coverage_rows = []
    query_counts: dict[tuple, int] = {}
    for q in executed_queries:
        query_counts[(q.domain, q.subdomain)] = query_counts.get((q.domain, q.subdomain), 0) + 1
    for key, row in sorted(by_domain.items()):
        row["discovery_queries"] = query_counts.get(key, 0)
        row["coverage_status"] = coverage_status(row)
        coverage_rows.append(row)

    coverage_fieldnames = ["domain", "subdomain", "structure_target", "discovery_queries",
                           "sources_discovered", "sources_metadata_acquired", "sources_fulltext_acquired",
                           "machine_readable_sources", "latex_sources", "xml_sources", "mathml_sources",
                           "pdf_sources", "inaccessible_sources", "acquisition_failures", "coverage_status"]
    coverage_csv = corpus_dir / "coverage" / "SOURCE_COVERAGE_MATRIX.csv"
    with coverage_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=coverage_fieldnames)
        writer.writeheader()
        for row in coverage_rows:
            writer.writerow({k: row.get(k, 0) for k in coverage_fieldnames})

    # Derived source index CSV (brief section XXV -- derived view)
    index_fieldnames = ["source_id", "arxiv_id", "title", "domain", "subdomain",
                        "acquisition_priority", "acquisition_status", "duplicate_group"]
    index_csv = corpus_dir / "coverage" / "SCIENTIFIC_SOURCE_INDEX.csv"
    index_rows = [{k: getattr(s, k) for k in index_fieldnames} for s in discovered]
    with index_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=index_fieldnames)
        writer.writeheader()
        for row in index_rows:
            writer.writerow(row)

    _write_xlsx(corpus_dir / "coverage" / "SOURCE_COVERAGE_MATRIX.xlsx", "coverage",
                coverage_fieldnames, coverage_rows)
    _write_xlsx(corpus_dir / "coverage" / "SCIENTIFIC_SOURCE_INDEX.xlsx", "sources",
                index_fieldnames, index_rows)

    # Append-only discovery run record (brief section XXIV)
    run_log_path = corpus_dir / "SCIENTIFIC_DISCOVERY_RUNS.jsonl"
    prior_runs = read_jsonl(run_log_path)
    run_record = {
        "discovery_run_id": f"RUN-{len(prior_runs) + 1:04d}",
        "timestamp": _now_iso(),
        "software_version": SOFTWARE_VERSION,
        "mode": "OFFLINE_FIXTURE" if offline else "LIVE",
        "query_registry_hash": _hash_records([q.to_dict() for q in executed_queries]),
        "source_registry_hash": _hash_records([s.to_dict() for s in discovered]),
        "acquisition_manifest_hash": _hash_records([m.to_dict() for m in manifests]),
        "discovery_stats": discovery_stats,
        "n_acquired": len(manifests), "n_failures": len(failures), "n_linked_existing": len(links),
    }
    with run_log_path.open("a") as f:
        f.write(json.dumps(run_record, sort_keys=True) + "\n")

    return {
        "discovered": discovered, "executed_queries": executed_queries,
        "discovery_stats": discovery_stats, "manifests": manifests, "failures": failures,
        "links": links, "run_record": run_record, "coverage_rows": coverage_rows,
    }


def write_report(result: dict, report_path: Path) -> None:
    discovered = result["discovered"]
    manifests = result["manifests"]
    failures = result["failures"]
    links = result["links"]
    stats = result["discovery_stats"]

    hashed = [s for s in discovered if s.acquisition_status == "HASHED"]
    linked = [s for s in discovered if s.duplicate_group and s.duplicate_group.startswith("LINK_EXISTING_SOURCE")]
    restricted = [s for s in discovered if s.acquisition_status in ("ACCESS_RESTRICTED", "LICENSE_RESTRICTED")]
    domains = sorted({s.domain for s in discovered})

    discovery_state = "DISCOVERY_COMPLETE" if stats["queries_failed"] == 0 else "DISCOVERY_PARTIAL"
    acquisition_state = "ACQUISITION_COMPLETE" if not failures and hashed else "ACQUISITION_PARTIAL"

    lines = [
        "# Phase 13, Phases C+D: Scientific Source Discovery + Acquisition",
        "",
        f"**{discovery_state} / {acquisition_state} / EXTRACTION READY: NO** "
        "(equation/variable/operator extraction, per brief section XIX, has not been attempted "
        "on any acquired source this phase).",
        "",
        "## Discovery",
        "",
        f"- Queries executed: {stats['queries_executed']} (failed: {stats['queries_failed']})",
        f"- Raw hits across all queries: {stats['raw_hits_across_all_queries']}",
        f"- Unique sources after arXiv-id dedup: {stats['unique_sources_after_dedup']}",
        f"- Duplicate hits removed: {stats['duplicate_hits_removed']}",
        f"- Domains covered: {', '.join(domains)}",
        f"- Channel used: arXiv API only (export.arxiv.org/api/query) -- INSPIRE-HEP, NASA ADS, "
        "NIST/DLMF, HEPData, Crossref, OpenAlex are brief-listed Level 2 sources NOT implemented "
        "this slice.",
        "",
        "## Acquisition",
        "",
        f"- Sources fulltext-acquired (PDF, hashed): {len(hashed)}",
        f"- Access-restricted / license-restricted: {len(restricted)}",
        f"- Acquisition failures (preserved, not discarded): {len(failures)}",
        f"- Linked to an existing Phase A/B project source (never duplicated): {len(linked)}",
        "- LaTeX source packages (arXiv /e-print): 0 -- arxiv.org/robots.txt explicitly "
        "Disallows /e-print and /src for automated agents; only /pdf (Allowed) was fetched. "
        "This is a real, disclosed limitation, not an oversight.",
        "",
        "## External UOCP/UDP/DER corpus",
        "",
        "EXTERNAL_CORPUS_NOT_PRESENT. That corpus was not searched for, fabricated, or "
        "reconstructed from memory this phase (brief section XXI).",
        "",
        "## Unresolved acquisition issues",
        "",
    ]
    if failures:
        for f in failures:
            lines.append(f"- {f['source_id']} ({f['arxiv_id']}): {f['failure_type']} -- {f['error']}")
    else:
        lines.append("- None this run.")
    lines += [
        "",
        "## Reproducibility",
        "",
        f"- discovery_run_id: {result['run_record']['discovery_run_id']}",
        f"- software_version: {result['run_record']['software_version']}",
        f"- mode: {result['run_record']['mode']}",
        f"- source_registry_hash: {result['run_record']['source_registry_hash']}",
        "",
        "See `data/scientific_corpus/SCIENTIFIC_DISCOVERY_RUNS.jsonl` (append-only) for the full "
        "history of discovery runs, and `data/scientific_corpus/coverage/SOURCE_COVERAGE_MATRIX.csv` "
        "for per-domain coverage state.",
    ]
    report_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-fixture", action="store_true",
                         help="Use bundled fixtures instead of live network (deterministic, for tests).")
    parser.add_argument("--max-results-per-query", type=int, default=8)
    parser.add_argument("--max-acquisitions", type=int, default=10)
    parser.add_argument("--output-root", type=Path, default=ROOT,
                         help="Root directory to write corpus artifacts under (default: this "
                              "repository). Tests pass a tmp_path here so no test run ever "
                              "touches real repository data.")
    args = parser.parse_args()

    result = main(offline=args.offline_fixture, max_results_per_query=args.max_results_per_query,
                  max_acquisitions=args.max_acquisitions, output_root=args.output_root)
    write_report(result, args.output_root / "PHASE13_SOURCE_DISCOVERY_REPORT.md")
    print(f"discovered: {len(result['discovered'])} unique sources "
          f"({result['discovery_stats']['raw_hits_across_all_queries']} raw hits, "
          f"{result['discovery_stats']['duplicate_hits_removed']} deduped)")
    print(f"linked to existing project sources: {len(result['links'])}")
    print(f"acquired (hashed): {len(result['manifests'])}")
    print(f"failures: {len(result['failures'])}")
    print(f"run: {result['run_record']['discovery_run_id']} ({result['run_record']['mode']})")
