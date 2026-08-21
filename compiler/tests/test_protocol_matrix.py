"""Tests for compiler/protocol/protocol_matrix.py -- the peer-review
protocol-taxonomy crosswalk against this repository's real registries."""
from __future__ import annotations

from pathlib import Path

import pytest

from compiler.protocol.protocol_matrix import (
    NO_ARTIFACT, _CORRESPONDENCES, build_protocol_matrix, layer_summary,
)
from compiler.protocol.protocol_taxonomy import TAXONOMY, TAXONOMY_BY_ID
from compiler.run_compiler import build_and_run


def test_taxonomy_ids_are_unique():
    ids = [e.protocol_id for e in TAXONOMY]
    assert len(ids) == len(set(ids))


def test_every_correspondence_key_is_a_real_taxonomy_id():
    for protocol_id in _CORRESPONDENCES:
        assert protocol_id in TAXONOMY_BY_ID, f"'{protocol_id}' not in the taxonomy"


@pytest.fixture(scope="module")
def matrix():
    result = build_and_run()
    return build_protocol_matrix(
        result["registries"], result["chainlinks"], result["protocols"],
        result["audit_results"], Path(".").resolve(),
    )


def test_full_build_produces_no_reference_errors(matrix):
    assert len(matrix) == len(TAXONOMY)
    reference_errors = [e for e in matrix if e.computed_status == "REFERENCE_ERROR"]
    assert reference_errors == [], f"broken correspondences: {reference_errors}"


def test_every_mapped_protocol_resolves_to_a_real_or_absent_status_never_fabricated(matrix):
    for e in matrix:
        if e.protocol_id not in _CORRESPONDENCES:
            assert e.computed_status == NO_ARTIFACT
            assert e.correspondence_kind is None
        else:
            assert e.computed_status != NO_ARTIFACT


def test_layer_summary_counts_are_internally_consistent(matrix):
    for row in layer_summary(matrix):
        assert row["n_with_real_backing"] + row["n_no_corresponding_artifact"] == row["n_protocols_total"]
        assert row["n_protocols_total"] > 0


def test_closure_gate_has_no_real_artifact(matrix):
    """UCC-001 is the single most consequential absence this crosswalk is
    meant to surface: nothing in this corpus computes end-to-end closure."""
    ucc = next(e for e in matrix if e.protocol_id == "UCC-001")
    assert ucc.computed_status == NO_ARTIFACT
