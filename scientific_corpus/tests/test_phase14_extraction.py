"""Offline tests for the Phase 14 mathematical extraction layer. All
tests here run against real data already on disk (the real literature
registry, the real status_matrix.json) -- no network calls, no
synthetic corpus data. Canonical-isolation tests run the real generator
script as a subprocess against an isolated tmp_path (--output-root),
following the same fixed pattern established in Phase 13 C/D after a
real bug there (an early version of that phase's test wrote to real
repository paths and clobbered a completed live run).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from scientific_corpus.extraction.literature_extractor import extract_from_literature_registry
from scientific_corpus.extraction.pdf_extractor import _line_is_candidate_equation, extract_pdf_review_candidates
from scientific_corpus.extraction.schema import stable_id
from scientific_corpus.extraction.structure_extractor import extract_structures_from_literature
from scientific_corpus.extraction.uoc_chain_crosswalk import build_uoc_chain_crosswalk

LITERATURE_REGISTRY_PATH = ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json"


def _real_literature_items():
    return json.loads(LITERATURE_REGISTRY_PATH.read_text())


# --- literature extractor ------------------------------------------------

def test_extracts_exactly_one_equation_record_per_literature_item():
    items = _real_literature_items()
    eqs, _v, _o, _r, _review = extract_from_literature_registry(items)
    assert len(eqs) == len(items)


def test_every_equation_source_status_is_source_extracted_never_verified():
    """Brief section III: 'established physics' is not a compiler
    verification status -- nothing this layer produces may be VERIFIED."""
    items = _real_literature_items()
    eqs, _v, _o, _r, _review = extract_from_literature_registry(items)
    for eq in eqs:
        assert eq.source_status == "SOURCE_EXTRACTED"
        assert eq.extraction_quality == "EXACT_LATEX"


def test_exact_representation_preserves_original_source_notation_verbatim():
    items = _real_literature_items()
    eqs, _v, _o, _r, _review = extract_from_literature_registry(items)
    by_id = {eq.equation_id: eq for eq in eqs}
    st001 = next(e for e in eqs if "1.1" in (e.equation_label or "") and e.source_id == "LIT-TONG-ST")
    original = next(i["SOURCE_NOTATION"] for i in items if i["EQUATION_NUMBER"] == "(1.1)")
    assert st001.exact_representation == original


def test_real_poisson_bracket_relations_are_detected_and_typed():
    """ST-024/ST-025 contain real _{PB}-subscripted brace relations --
    must come through as POISSON_BRACKET, not COMMUTATOR/ANTICOMMUTATOR."""
    items = _real_literature_items()
    _eqs, _v, _o, rels, _review = extract_from_literature_registry(items)
    pb_relations = [r for r in rels if r.relation_type == "POISSON_BRACKET"]
    assert len(pb_relations) >= 2


def test_variable_occurrences_are_source_scoped_not_globally_merged():
    """Brief section X: the same literal symbol in two different
    equations must be two different variable_id occurrences."""
    items = _real_literature_items()
    _eqs, variables, _o, _r, _review = extract_from_literature_registry(items)
    by_symbol: dict[str, set[str]] = {}
    for v in variables:
        by_symbol.setdefault(v.literal_symbol, set()).add(v.equation_id)
    repeated = {sym: eqs for sym, eqs in by_symbol.items() if len(eqs) > 1}
    assert repeated, "expected at least one symbol to recur across multiple real equations"
    for sym, eq_ids in repeated.items():
        ids_for_symbol = [v.variable_id for v in variables if v.literal_symbol == sym]
        assert len(set(ids_for_symbol)) == len(eq_ids), (
            f"symbol {sym!r} occurrences across equations must have distinct variable_ids"
        )


def test_deterministic_ids_across_repeated_extraction():
    items = _real_literature_items()
    eqs1, v1, o1, r1, _rv1 = extract_from_literature_registry(items)
    eqs2, v2, o2, r2, _rv2 = extract_from_literature_registry(items)
    assert [e.to_dict() for e in eqs1] == [e.to_dict() for e in eqs2]
    assert [x.to_dict() for x in v1] == [x.to_dict() for x in v2]
    assert [x.to_dict() for x in o1] == [x.to_dict() for x in o2]
    assert [x.to_dict() for x in r1] == [x.to_dict() for x in r2]


# --- structure extractor --------------------------------------------------

def test_structure_extraction_only_fires_on_explicit_keyword_evidence():
    items = _real_literature_items()
    structures = extract_structures_from_literature(items)
    assert len(structures) > 0
    for s in structures:
        assert s.evidence, "every structure record must carry the literal source text it came from"
        assert s.source_id in {"LIT-TONG-ST", "LIT-KIRITSIS-SST"}


# --- UOC chain crosswalk --------------------------------------------------

def test_crosswalk_covers_all_eleven_chain_positions():
    status_matrix = json.loads((ROOT / "status_matrix.json").read_text())
    items = _real_literature_items()
    rows = build_uoc_chain_crosswalk(status_matrix, items, [])
    positions = {row.chain_position for row in rows}
    assert positions == {str(i) for i in range(1, 12)}


def test_crosswalk_never_claims_worldsheet_metric_equals_spacetime_metric():
    """The metric chain position's compiler row must carry the explicit
    non-equivalence caveat -- this must never silently disappear."""
    status_matrix = json.loads((ROOT / "status_matrix.json").read_text())
    items = _real_literature_items()
    rows = build_uoc_chain_crosswalk(status_matrix, items, [])
    metric_compiler_rows = [
        r for r in rows if r.chain_position == "6" and r.source_id == "UOC-COMPILER"
    ]
    assert len(metric_compiler_rows) == 1
    assert "not asserted" in metric_compiler_rows[0].provenance.lower()


def test_crosswalk_compiler_status_reflects_real_status_matrix():
    status_matrix = json.loads((ROOT / "status_matrix.json").read_text())
    items = _real_literature_items()
    rows = build_uoc_chain_crosswalk(status_matrix, items, [])
    graph_row = next(r for r in rows if r.chain_position == "3" and r.source_id == "UOC-COMPILER")
    real_status = next(r["status"] for r in status_matrix if r["id"] == "GRAPH-G-SEED")
    assert real_status in graph_row.evidence


# --- PDF extractor ---------------------------------------------------------

def test_candidate_line_heuristic_accepts_real_math_dense_line():
    assert _line_is_candidate_equation(r"II(X,Y ) = πνN")


def test_candidate_line_heuristic_rejects_ordinary_prose():
    assert not _line_is_candidate_equation(
        "The analogy of natural selection as measurement and the analogy of heredity"
    )


def test_candidate_line_heuristic_rejects_too_short_or_too_long():
    assert not _line_is_candidate_equation("=")
    assert not _line_is_candidate_equation("x" * 300)


def test_pdf_extraction_against_a_real_acquired_pdf():
    pdf_dir = ROOT / "data" / "scientific_corpus" / "sources" / "raw"
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        return  # no PDFs acquired in this checkout -- nothing to test against
    items, stats = extract_pdf_review_candidates(pdfs[0], "TEST-SRC", max_pages=2)
    assert stats["pages_processed"] <= 2
    assert "file_failure" not in stats
    for item in items:
        assert item.issue == "PDF_TEXT_CANDIDATE_NOT_STRUCTURED"
        assert item.status == "UNRESOLVED"


def test_pdf_extraction_records_failure_for_nonexistent_file():
    items, stats = extract_pdf_review_candidates(Path("/nonexistent/does-not-exist.pdf"), "TEST-SRC")
    assert items == []
    assert "file_failure" in stats


# --- canonical / corpus isolation (real subprocess, isolated tmp_path) ---

def test_extraction_run_never_touches_canonical_registries(tmp_path):
    canonical_files = [
        "equation_registry.json", "transformation_registry.json", "object_registry.json",
        "master_mdcl.json", "self_audit_report.json", "chainlink_registry.json",
        "protocol_registry.json", "status_matrix.json",
    ]
    before = {f: (ROOT / f).read_bytes() for f in canonical_files}
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase14_extraction.py"),
         "--output-root", str(tmp_path), "--max-pdf-pages", "1", "--max-pdfs", "1"],
        cwd=ROOT, check=True, capture_output=True, timeout=60,
    )
    after = {f: (ROOT / f).read_bytes() for f in canonical_files}
    assert before == after, "Phase 14 extraction modified a canonical registry file"
    assert (tmp_path / "data" / "scientific_corpus" / "equations" / "equation_registry.jsonl").exists()


def test_extraction_run_never_modifies_phase13_corpus_files(tmp_path):
    ab_files = [
        ROOT / "data" / "scientific_corpus" / "equations" / "equations.jsonl",
        ROOT / "data" / "scientific_corpus" / "operators" / "operators.jsonl",
        ROOT / "data" / "scientific_corpus" / "sources" / "discovery" /
        "SCIENTIFIC_SOURCE_DISCOVERY_REGISTRY.jsonl",
    ]
    before = {f: f.read_bytes() for f in ab_files if f.exists()}
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase14_extraction.py"),
         "--output-root", str(tmp_path), "--max-pdf-pages", "1", "--max-pdfs", "1"],
        cwd=ROOT, check=True, capture_output=True, timeout=60,
    )
    after = {f: f.read_bytes() for f in ab_files if f.exists()}
    assert before == after


def test_extraction_run_never_modifies_literature_source_registry(tmp_path):
    """The Phase 14 layer reads STRING_THEORY_LITERATURE_REGISTRY.json --
    it must never write back to it."""
    before = LITERATURE_REGISTRY_PATH.read_bytes()
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase14_extraction.py"),
         "--output-root", str(tmp_path), "--max-pdf-pages", "1", "--max-pdfs", "1"],
        cwd=ROOT, check=True, capture_output=True, timeout=60,
    )
    after = LITERATURE_REGISTRY_PATH.read_bytes()
    assert before == after
