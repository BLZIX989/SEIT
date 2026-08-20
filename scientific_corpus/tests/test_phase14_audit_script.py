"""Tests for scripts/generate_phase14_extraction_audit.py's individual
audit functions. Includes a regression test for a real bug found while
running this phase's own audit against real data: the source-provenance
check originally assumed every record type carries a `provenance`
field, but SymbolOccurrence/OperatorOccurrence carry their provenance in
`source_location`/`extraction_method` instead (by schema design) -- the
bug produced 54 false-positive failures against every real, correctly-
provenanced operator record.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "phase14_audit_script", ROOT / "scripts" / "generate_phase14_extraction_audit.py"
)
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("phase14_audit_script", _MODULE)
_SPEC.loader.exec_module(_MODULE)  # real script execution (imports only, no I/O at module scope)


def test_source_provenance_audit_passes_for_real_operator_shaped_records():
    """Regression: a real OperatorOccurrence dict (no top-level
    `provenance` key by schema design) must not be flagged as missing
    provenance -- it has real source_id/source_location/extraction_method."""
    operators = [{
        "operator_id": "SCIOPX-abc", "equation_id": "SCIEQ14-xyz", "symbol": "\\partial",
        "source_id": "LIT-TONG-ST", "source_location": "p.9, eq.(1.1)", "definition": "UNKNOWN",
        "extraction_method": "LATEX_SOURCE", "confidence": "TOKENIZER_HEURISTIC",
        "algebraic_properties": "NOT_EXTRACTED",
    }]
    result = _MODULE.audit_source_provenance([], [], operators, [], [])
    assert result["passed"], result["issues"]


def test_source_provenance_audit_still_catches_a_genuinely_missing_source_id():
    operators = [{
        "operator_id": "SCIOPX-abc", "equation_id": "SCIEQ14-xyz", "symbol": "\\partial",
        "source_id": "", "source_location": "p.9, eq.(1.1)", "definition": "UNKNOWN",
        "extraction_method": "LATEX_SOURCE", "confidence": "TOKENIZER_HEURISTIC",
    }]
    result = _MODULE.audit_source_provenance([], [], operators, [], [])
    assert not result["passed"]
    assert result["n_issues"] == 1


def test_duplicate_audit_detects_a_real_duplicate_id():
    equations = [
        {"equation_id": "EQ-1"}, {"equation_id": "EQ-1"}, {"equation_id": "EQ-2"},
    ]
    result = _MODULE.audit_duplicates(equations, [], [], [], [])
    assert not result["passed"]
    assert result["duplicates"]["equation"] == ["EQ-1"]


def test_dimensional_metadata_audit_flags_a_fabricated_dimension():
    equations = [{"equation_id": "EQ-1", "dimensional_information": "NOT_EXTRACTED"},
                 {"equation_id": "EQ-2", "dimensional_information": "[M L T^-2]"}]
    result = _MODULE.audit_dimensional_metadata(equations)
    assert not result["passed"]
    assert result["equations_with_fabricated_dimensions"] == ["EQ-2"]
