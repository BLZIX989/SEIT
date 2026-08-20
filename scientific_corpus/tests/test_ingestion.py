"""Tests for Phase 13 Phase A+B ingestion (scripts/generate_scientific_corpus_phase_ab.py).

Covers the subset of master brief section L's testing requirements that
apply to THIS slice (provenance preservation, duplicate detection,
source isolation, canonical registry isolation, reproducibility, honest
coverage reporting) -- not the equivalence/dimensional-analysis/OCR
tests, since those subsystems have not been built yet (see
scientific_corpus/__init__.py).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.generate_scientific_corpus_phase_ab import (
    build_coverage_report, build_sources, ingest_compiler_equations,
    ingest_literature_equations, ingest_operators,
)


def test_every_compiler_equation_traces_to_a_real_registry_id():
    real_ids = {e["id"] for e in json.loads((ROOT / "equation_registry.json").read_text())}
    corpus_eqs = ingest_compiler_equations()
    assert len(corpus_eqs) == len(real_ids)
    for e in corpus_eqs:
        assert e.source_equation_id in real_ids


def test_every_literature_equation_traces_to_a_real_registry_id():
    real_ids = {e["STRING_ITEM_ID"] for e in json.loads(
        (ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json").read_text())}
    corpus_eqs = ingest_literature_equations()
    assert len(corpus_eqs) == len(real_ids)
    for e in corpus_eqs:
        assert e.source_equation_id in real_ids


def test_source_isolation_compiler_vs_workbook_never_conflated():
    """A compiler-executed equation (real Status) and a historical-
    workbook-imported equation (PROPOSED, explicitly not trusted at face
    value by the compiler's own registration) must never share a
    status_category -- conflating them would silently upgrade a source
    claim to a compiler result."""
    corpus_eqs = ingest_compiler_equations()
    for e in corpus_eqs:
        if e.source_id == "UOC-COMPILER":
            assert e.status_category == "COMPILER_DERIVED"
        else:
            assert e.status_category == "SOURCE_CLAIM"
            assert e.source_id == "FC005-SOURCE-WORKBOOK-04"


def test_literature_equations_are_always_source_claim_never_compiler_derived():
    for e in ingest_literature_equations():
        assert e.status_category == "SOURCE_CLAIM"


def test_no_duplicate_equation_ids():
    all_eqs = ingest_compiler_equations() + ingest_literature_equations()
    ids = [e.equation_id for e in all_eqs]
    assert len(ids) == len(set(ids)), "duplicate equation_id in the corpus"


def test_no_duplicate_source_ids():
    sources = build_sources()
    ids = [s.source_id for s in sources]
    assert len(ids) == len(set(ids))


def test_operator_ids_trace_to_real_transformation_registry():
    real_ids = {t["id"] for t in json.loads((ROOT / "transformation_registry.json").read_text())}
    ops = ingest_operators()
    assert len(ops) == len(real_ids)
    for op in ops:
        assert op.source_transformation_id in real_ids
        assert op.status_category == "COMPILER_DERIVED"


def test_equation_hash_is_deterministic():
    a = ingest_compiler_equations()
    b = ingest_compiler_equations()
    assert [e.equation_hash for e in a] == [e.equation_hash for e in b]


def test_coverage_report_never_claims_completeness():
    sources = build_sources()
    compiler_eqs = ingest_compiler_equations()
    lit_eqs = ingest_literature_equations()
    ops = ingest_operators()
    coverage = build_coverage_report(sources, compiler_eqs, lit_eqs, ops)
    assert coverage["equations_extracted"] == len(compiler_eqs) + len(lit_eqs)
    assert "explicit_non_claim" in coverage
    assert "does NOT contain" in coverage["explicit_non_claim"]
    # Every count must be small and real, not a large fabricated number.
    assert coverage["sources_discovered"] < 100
    assert coverage["equations_extracted"] < 1000


def test_running_the_generator_touches_no_canonical_registry(tmp_path, monkeypatch):
    """The generator script must never write to equation_registry.json,
    transformation_registry.json, or any other canonical compiler
    artifact -- it only reads them (brief section XLVIII)."""
    canonical_files = [
        "equation_registry.json", "transformation_registry.json", "object_registry.json",
        "master_mdcl.json", "self_audit_report.json", "chainlink_registry.json",
        "protocol_registry.json",
    ]
    before = {f: (ROOT / f).read_bytes() for f in canonical_files}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase_ab.py")],
                    cwd=ROOT, check=True, capture_output=True, timeout=30)
    after = {f: (ROOT / f).read_bytes() for f in canonical_files}
    assert before == after, "generator script modified a canonical registry file"


def test_generator_output_is_reproducible_in_content(tmp_path):
    """Running twice must produce byte-identical equation/operator/source
    JSONL content (the underlying source data doesn't change between
    runs, so neither should the corpus)."""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase_ab.py")],
                    cwd=ROOT, check=True, capture_output=True, timeout=30)
    eq1 = (ROOT / "data" / "scientific_corpus" / "equations" / "equations.jsonl").read_text()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase_ab.py")],
                    cwd=ROOT, check=True, capture_output=True, timeout=30)
    eq2 = (ROOT / "data" / "scientific_corpus" / "equations" / "equations.jsonl").read_text()
    assert eq1 == eq2
