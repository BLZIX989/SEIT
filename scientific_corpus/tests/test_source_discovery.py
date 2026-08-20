"""Offline tests for scientific_corpus/source_discovery/ (brief section
XXII/XXIII). No test in this file makes a real network call -- every
fetch is a fixture or an injected fake. Live acquisition is exercised
separately by scripts/generate_scientific_corpus_phase_cd.py, which is
not part of the ordinary test run.
"""
from __future__ import annotations

import sys
import time
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CORPUS_DIR_FOR_TEST = ROOT / "data" / "scientific_corpus"

from scientific_corpus.schema import Source
from scientific_corpus.source_discovery.acquisition import acquire_sources
from scientific_corpus.source_discovery.arxiv_client import (
    RateLimiter, parse_atom_feed, parse_total_results,
)
from scientific_corpus.source_discovery.crosswalk import link_existing_sources
from scientific_corpus.source_discovery.discovery import run_discovery
from scientific_corpus.source_discovery.queries import build_query_registry, query_priorities
from scientific_corpus.source_discovery.schema import (
    DiscoveredSource, sha256_bytes, stable_source_id,
)

SAMPLE_XML = (FIXTURES / "arxiv_atom_sample.xml").read_bytes()
EMPTY_XML = (FIXTURES / "arxiv_atom_empty.xml").read_bytes()


# --- parsing ---------------------------------------------------------

def test_parse_atom_feed_extracts_real_fields():
    entries = parse_atom_feed(SAMPLE_XML)
    assert len(entries) == 2
    e = entries[0]
    assert e.arxiv_id == "1301.6896"
    assert e.version == "v1"
    assert e.title == "Laplacians on periodic discrete graphs"
    assert e.authors == ["Test Author One", "Test Author Two"]
    assert "math.SP" in e.categories
    assert e.pdf_url == "http://arxiv.org/pdf/1301.6896v1"


def test_parse_atom_feed_empty_result_returns_empty_list():
    assert parse_atom_feed(EMPTY_XML) == []


def test_parse_total_results():
    assert parse_total_results(SAMPLE_XML) == 288630
    assert parse_total_results(EMPTY_XML) == 0


def test_parse_atom_feed_preserves_old_style_arxiv_id_archive_prefix():
    """Regression test: old-style arXiv ids carry an archive prefix
    (e.g. "math/0002194", "hep-th/9709062") that a naive last-"/"-segment
    split silently drops, corrupting the identifier. Found live against
    a real arXiv result (Fiore, "On q-Deformations of Clifford Algebras",
    math/0002194) during this phase's actual discovery run."""
    xml = b"""<?xml version='1.0'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/math/0002194v2</id>
    <title>On q-Deformations of Clifford Algebras</title>
  </entry>
</feed>"""
    entries = parse_atom_feed(xml)
    assert entries[0].arxiv_id == "math/0002194"
    assert entries[0].version == "v2"


def test_parse_atom_feed_malformed_missing_fields_does_not_crash():
    malformed = b"""<?xml version='1.0'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><id>http://arxiv.org/abs/9999.99999</id></entry>
</feed>"""
    entries = parse_atom_feed(malformed)
    assert len(entries) == 1
    assert entries[0].title == ""
    assert entries[0].authors == []
    assert entries[0].version is None  # no "vN" suffix present


# --- source id / hashing ---------------------------------------------

def test_stable_source_id_is_deterministic():
    assert stable_source_id("arxiv", "1301.6896") == stable_source_id("arxiv", "1301.6896")


def test_stable_source_id_differs_by_channel_and_id():
    a = stable_source_id("arxiv", "1301.6896")
    b = stable_source_id("doi", "1301.6896")
    c = stable_source_id("arxiv", "0908.0333")
    assert len({a, b, c}) == 3


def test_stable_source_id_never_embeds_a_url():
    sid = stable_source_id("arxiv", "http://arxiv.org/abs/1301.6896v1")
    assert "http" not in sid
    assert "/" not in sid


def test_sha256_bytes_matches_hashlib_directly():
    import hashlib
    data = b"some real pdf-like byte content"
    assert sha256_bytes(data) == hashlib.sha256(data).hexdigest()


def test_sha256_bytes_differs_for_different_content():
    assert sha256_bytes(b"a") != sha256_bytes(b"b")


# --- discovery / dedup -------------------------------------------------

def _fake_fetch_factory(xml_by_call):
    calls = {"n": 0}
    def fetch(query_text, max_results=8):
        idx = min(calls["n"], len(xml_by_call) - 1)
        calls["n"] += 1
        return xml_by_call[idx]
    fetch.calls = calls
    return fetch


def test_run_discovery_dedups_across_queries():
    queries = build_query_registry()[:2]
    fetch = _fake_fetch_factory([SAMPLE_XML, SAMPLE_XML])  # same 2 entries both times
    sources, executed_queries, stats = run_discovery(queries, fetch_fn=fetch)
    assert stats["raw_hits_across_all_queries"] == 4
    assert stats["unique_sources_after_dedup"] == 2
    assert stats["duplicate_hits_removed"] == 2
    assert len(sources) == 2
    assert all(q.retrieval_status == "OK" for q in executed_queries)


def test_run_discovery_records_query_failures_without_raising():
    queries = build_query_registry()[:1]
    def failing_fetch(query_text, max_results=8):
        raise urllib.error.URLError("simulated network failure")
    sources, executed_queries, stats = run_discovery(queries, fetch_fn=failing_fetch)
    assert sources == []
    assert executed_queries[0].retrieval_status.startswith("FAILED")
    assert stats["queries_failed"] == 1


def test_discovered_sources_are_deterministic_given_same_fixture():
    queries1 = build_query_registry()[:1]
    queries2 = build_query_registry()[:1]
    fetch = _fake_fetch_factory([SAMPLE_XML])
    sources1, _, _ = run_discovery(queries1, fetch_fn=fetch)
    fetch2 = _fake_fetch_factory([SAMPLE_XML])
    sources2, _, _ = run_discovery(queries2, fetch_fn=fetch2)
    ids1 = sorted(s.source_id for s in sources1)
    ids2 = sorted(s.source_id for s in sources2)
    assert ids1 == ids2


def test_discovered_source_version_preserved():
    queries = build_query_registry()[:1]
    fetch = _fake_fetch_factory([SAMPLE_XML])
    sources, _, _ = run_discovery(queries, fetch_fn=fetch)
    by_id = {s.arxiv_id: s for s in sources}
    assert by_id["1301.6896"].version == "v1"
    assert by_id["0908.0333"].version == "v3"


def test_query_priorities_cover_every_query():
    queries = build_query_registry()
    priorities = query_priorities()
    assert set(q.query_id for q in queries) == set(priorities.keys())
    assert set(priorities.values()) <= {1, 3}


# --- existing-corpus crosswalk -----------------------------------------

def test_link_existing_source_never_duplicates():
    """The fixture deliberately includes arXiv id 0908.0333 (Tong,
    already ingested in Phase A/B as LIT-TONG-ST) -- rediscovering it via
    the arXiv API must link to the existing source, never create a
    second, competing record for the same paper."""
    queries = build_query_registry()[:1]
    fetch = _fake_fetch_factory([SAMPLE_XML])
    sources, _, _ = run_discovery(queries, fetch_fn=fetch)

    existing = [Source(source_id="LIT-TONG-ST", title="String Theory",
                        document_type="lecture_notes_arxiv", repository="literature/",
                        arxiv_id="0908.0333v3")]
    linked, links = link_existing_sources(sources, existing)

    tong = next(s for s in linked if s.arxiv_id == "0908.0333")
    assert tong.duplicate_group == "LINK_EXISTING_SOURCE:LIT-TONG-ST"
    assert tong.parent_source_id == "LIT-TONG-ST"
    assert tong.acquisition_status == "DISCOVERED_ONLY"
    assert len(links) == 1
    assert links[0]["relation"] == "LINK_EXISTING_SOURCE"

    other = next(s for s in linked if s.arxiv_id == "1301.6896")
    assert other.duplicate_group is None


# --- acquisition ---------------------------------------------------------

def _make_source(arxiv_id="1301.6896", priority=1, pdf_url="http://example.invalid/pdf"):
    return DiscoveredSource(
        source_id=stable_source_id("arxiv", arxiv_id), title="t", authors=["a"],
        publication_year="2013", doi=None, arxiv_id=arxiv_id, repository_id=None,
        journal=None, publisher="arXiv", abstract="", subject_categories=[],
        domain="mathematics", subdomain="spectral graph theory", source_type="preprint",
        discovery_method="arxiv_api", discovery_query_id="QUERY-001",
        discovery_timestamp="2026-08-20T00:00:00Z", source_url="http://example.invalid/abs",
        fulltext_url=pdf_url, source_package_url=None, acquisition_priority=priority,
    )


def test_acquire_sources_writes_manifest_with_real_hash(tmp_path):
    source = _make_source()
    fetch = lambda url: b"%PDF-1.4 fake pdf bytes"
    manifests, failures = acquire_sources([source], tmp_path, fetch_fn=fetch)
    assert len(manifests) == 1
    assert failures == []
    m = manifests[0]
    assert m.source_hash == f"sha256:{sha256_bytes(b'%PDF-1.4 fake pdf bytes')}"
    assert m.file_size == len(b"%PDF-1.4 fake pdf bytes")
    assert (tmp_path / m.filename).read_bytes() == b"%PDF-1.4 fake pdf bytes"
    assert source.acquisition_status == "HASHED"


def test_acquire_sources_records_access_restricted_without_raising(tmp_path):
    source = _make_source()
    def fetch(url):
        raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
    manifests, failures = acquire_sources([source], tmp_path, fetch_fn=fetch)
    assert manifests == []
    assert len(failures) == 1
    assert source.acquisition_status == "ACCESS_RESTRICTED"
    assert failures[0]["failure_type"] == "HTTPError"


def test_acquire_sources_records_not_found_without_raising(tmp_path):
    source = _make_source()
    def fetch(url):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    manifests, failures = acquire_sources([source], tmp_path, fetch_fn=fetch)
    assert source.acquisition_status == "NOT_FOUND"
    assert len(failures) == 1


def test_acquire_sources_skips_already_hashed_sources(tmp_path):
    """Cache reuse (brief section XII): a source already HASHED must not
    be re-fetched on a subsequent acquisition pass."""
    source = _make_source()
    source.acquisition_status = "HASHED"
    calls = []
    def fetch(url):
        calls.append(url)
        return b"should not be called"
    manifests, failures = acquire_sources([source], tmp_path, fetch_fn=fetch)
    assert calls == []
    assert manifests == []


def test_acquire_sources_respects_priority_ordering(tmp_path):
    low = _make_source(arxiv_id="1111.1111", priority=3)
    high = _make_source(arxiv_id="2222.2222", priority=1)
    fetch_order = []
    def fetch(url):
        fetch_order.append(url)
        return b"x"
    acquire_sources([low, high], tmp_path, max_acquisitions=1, fetch_fn=fetch)
    assert len(fetch_order) == 1
    assert fetch_order[0] == high.fulltext_url


def test_acquire_sources_never_exceeds_max_acquisitions(tmp_path):
    sources = [_make_source(arxiv_id=f"{i}.{i}") for i in range(5)]
    fetch = lambda url: b"x"
    manifests, _ = acquire_sources(sources, tmp_path, max_acquisitions=2, fetch_fn=fetch)
    assert len(manifests) == 2


# --- rate limiting ---------------------------------------------------

def test_rate_limiter_enforces_minimum_interval():
    limiter = RateLimiter(min_interval_seconds=0.1)
    t0 = time.monotonic()
    limiter.wait()
    limiter.wait()
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.1


def test_rate_limiter_first_call_does_not_block():
    limiter = RateLimiter(min_interval_seconds=5.0)
    t0 = time.monotonic()
    limiter.wait()
    assert time.monotonic() - t0 < 1.0


# --- retry / backoff (mocked urllib, no real network) -------------------

def test_fetch_raw_retries_on_transient_failure_then_succeeds(monkeypatch):
    from scientific_corpus.source_discovery import arxiv_client

    monkeypatch.setattr(arxiv_client, "_RATE_LIMITER", RateLimiter(min_interval_seconds=0.0))
    monkeypatch.setattr(time, "sleep", lambda s: None)

    calls = {"n": 0}

    class _FakeResp:
        def __init__(self, data):
            self._data = data
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self):
            return self._data

    def fake_urlopen(req, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.URLError("simulated transient failure")
        return _FakeResp(SAMPLE_XML)

    monkeypatch.setattr(arxiv_client.urllib.request, "urlopen", fake_urlopen)
    result = arxiv_client.fetch_raw("graph laplacian", max_results=2)
    assert calls["n"] == 3
    assert result == SAMPLE_XML


def test_fetch_raw_does_not_retry_on_4xx(monkeypatch):
    from scientific_corpus.source_discovery import arxiv_client

    monkeypatch.setattr(arxiv_client, "_RATE_LIMITER", RateLimiter(min_interval_seconds=0.0))
    calls = {"n": 0}

    def fake_urlopen(req, timeout):
        calls["n"] += 1
        raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, None)

    monkeypatch.setattr(arxiv_client.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(urllib.error.HTTPError):
        arxiv_client.fetch_raw("graph laplacian")
    assert calls["n"] == 1  # never retried


# --- source isolation --------------------------------------------------

def test_offline_fixture_run_never_touches_canonical_registries(tmp_path):
    """Runs the real Phase C/D generator script end-to-end in
    --offline-fixture mode (no network, deterministic), writing all
    output under an isolated tmp_path (--output-root) so this test run
    itself cannot disturb the repository's real corpus data, and proves
    every canonical compiler registry is byte-identical before and after
    -- same before/after diff discipline as Phase A/B's own test."""
    import subprocess
    canonical_files = [
        "equation_registry.json", "transformation_registry.json", "object_registry.json",
        "master_mdcl.json", "self_audit_report.json", "chainlink_registry.json",
        "protocol_registry.json",
    ]
    before = {f: (ROOT / f).read_bytes() for f in canonical_files}
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase_cd.py"),
         "--offline-fixture", "--max-results-per-query", "2", "--max-acquisitions", "1",
         "--output-root", str(tmp_path)],
        cwd=ROOT, check=True, capture_output=True, timeout=30,
    )
    after = {f: (ROOT / f).read_bytes() for f in canonical_files}
    assert before == after, "Phase C/D generator modified a canonical registry file"
    # and it really did write real output, just isolated under tmp_path
    assert (tmp_path / "data" / "scientific_corpus" / "sources" / "discovery" /
            "SCIENTIFIC_SOURCE_DISCOVERY_REGISTRY.jsonl").exists()


def test_offline_fixture_run_never_modifies_phase_ab_corpus_files(tmp_path):
    """The Phase C/D script must extend, not overwrite, the Phase A/B
    corpus (brief section II: "extend the existing corpus architecture") --
    even though it reads sources.jsonl from the real repo, it must never
    write there."""
    import subprocess
    ab_files = [
        CORPUS_DIR_FOR_TEST / "equations" / "equations.jsonl",
        CORPUS_DIR_FOR_TEST / "operators" / "operators.jsonl",
        CORPUS_DIR_FOR_TEST / "sources" / "sources.jsonl",
    ]
    before = {f: f.read_bytes() for f in ab_files}
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase_cd.py"),
         "--offline-fixture", "--max-results-per-query", "2", "--max-acquisitions", "1",
         "--output-root", str(tmp_path)],
        cwd=ROOT, check=True, capture_output=True, timeout=30,
    )
    after = {f: f.read_bytes() for f in ab_files}
    assert before == after


def test_discovered_source_is_not_a_canonical_scientific_corpus_source():
    """DiscoveredSource (this subpackage) and scientific_corpus.schema.Source
    (Phase A/B, the corpus's canonical source registry) are deliberately
    different types -- discovery evidence must not silently become a
    canonical corpus source without going through link_existing_sources
    or a later, explicit acquisition-to-corpus promotion step."""
    d = _make_source()
    assert not isinstance(d, Source)
    assert type(d).__name__ == "DiscoveredSource"
