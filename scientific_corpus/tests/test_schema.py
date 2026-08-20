"""Unit tests for scientific_corpus/schema.py's record shapes themselves,
independent of the ingestion script."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scientific_corpus.schema import CorpusEquation, CorpusOperator, Source, read_jsonl, write_jsonl


def test_equation_hash_is_stable_for_identical_input():
    a = CorpusEquation(
        equation_id="SCIEQ-X", source_id="S1", source_equation_id="X",
        source_location="p.1", equation_latex_original="a=b", equation_text="",
        domain="d", subdomain=None, status_category="SOURCE_CLAIM",
        source_status_verbatim="PROPOSED", extraction_method="TEST",
        extraction_confidence="EXACT", semantic_confidence="NOT_ASSESSED",
    )
    b = CorpusEquation(
        equation_id="SCIEQ-X", source_id="S1", source_equation_id="X",
        source_location="p.1", equation_latex_original="a=b", equation_text="",
        domain="d", subdomain=None, status_category="SOURCE_CLAIM",
        source_status_verbatim="PROPOSED", extraction_method="TEST",
        extraction_confidence="EXACT", semantic_confidence="NOT_ASSESSED",
    )
    assert a.equation_hash == b.equation_hash


def test_equation_hash_differs_for_different_latex():
    a = CorpusEquation(
        equation_id="SCIEQ-X", source_id="S1", source_equation_id="X",
        source_location="p.1", equation_latex_original="a=b", equation_text="",
        domain="d", subdomain=None, status_category="SOURCE_CLAIM",
        source_status_verbatim="PROPOSED", extraction_method="TEST",
        extraction_confidence="EXACT", semantic_confidence="NOT_ASSESSED",
    )
    b = CorpusEquation(
        equation_id="SCIEQ-X", source_id="S1", source_equation_id="X",
        source_location="p.1", equation_latex_original="a=c", equation_text="",
        domain="d", subdomain=None, status_category="SOURCE_CLAIM",
        source_status_verbatim="PROPOSED", extraction_method="TEST",
        extraction_confidence="EXACT", semantic_confidence="NOT_ASSESSED",
    )
    assert a.equation_hash != b.equation_hash


def test_write_and_read_jsonl_round_trip(tmp_path):
    sources = [Source(source_id="S1", title="T", document_type="test", repository="r")]
    path = tmp_path / "sources.jsonl"
    write_jsonl(sources, path)
    loaded = read_jsonl(path)
    assert len(loaded) == 1
    assert loaded[0]["source_id"] == "S1"


def test_read_jsonl_missing_file_returns_empty_list(tmp_path):
    assert read_jsonl(tmp_path / "does_not_exist.jsonl") == []


def test_corpus_operator_to_dict_is_json_serializable():
    op = CorpusOperator(
        operator_id="SCIOP-X", source_id="UOC-COMPILER", source_transformation_id="X",
        domain="A", codomain="B", action="f", status_category="COMPILER_DERIVED",
        source_status_verbatim="VERIFIED",
    )
    payload = json.dumps(op.to_dict())
    assert "SCIOP-X" in payload
