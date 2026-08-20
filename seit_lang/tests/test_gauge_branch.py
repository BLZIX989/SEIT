"""Tests for seit_lang.gauge_branch (Phase 11)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian
from scientific_corpus.derivation import gauge_rank

from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.gauge_branch import (
    GAUGE_BRANCH_BINDINGS,
    GAUGE_BRANCH_TRANSFORMATIONS,
    eigenvalue_multiplicity_pattern,
    h4c_missing_link_report,
    h4c_pattern_match_report,
    su2xu1_in_spin8_check,
    su3_in_g2_check,
)
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program


# --- existing gauge derivations exposed unchanged ------------------------

def test_su3_in_g2_check_matches_real_module():
    assert su3_in_g2_check() == gauge_rank.su3_in_g2_check()


def test_su2xu1_in_spin8_check_matches_real_module():
    assert su2xu1_in_spin8_check() == gauge_rank.su2xu1_in_spin8_check()


def test_h4c_missing_link_report_matches_real_module():
    assert h4c_missing_link_report() == gauge_rank.missing_link_to_compiler_spectrum()


def test_h4c_missing_link_report_states_no_construction_rule_exists():
    report = h4c_missing_link_report()
    assert "No such construction rule exists" in report["missing_object"]


# --- eigenvalue multiplicity pattern: a pure measurement -------------------

def test_multiplicity_pattern_on_complete_graph_matches_known_spectrum():
    """K_5's Laplacian spectrum is a well-known, exactly-checkable case:
    eigenvalue 0 with multiplicity 1, eigenvalue n=5 with multiplicity
    n-1=4 -- a real, independent cross-check, not a tautology."""
    A = graph_laplacian.build_graph("complete", 5).adjacency()
    L = graph_laplacian.laplacian(A)
    pattern = eigenvalue_multiplicity_pattern(L, n_lowest=2)
    assert pattern == [1, 4]


def test_multiplicity_pattern_on_path_graph_is_mostly_nondegenerate():
    A = graph_laplacian.build_graph("path", 10).adjacency()
    L = graph_laplacian.laplacian(A)
    pattern = eigenvalue_multiplicity_pattern(L, n_lowest=4)
    assert pattern == [1, 1, 1, 1]  # path graph Laplacian eigenvalues are all distinct


def test_multiplicity_pattern_is_a_pure_measurement_idempotent():
    A = graph_laplacian.build_graph("cycle", 12).adjacency()
    L = graph_laplacian.laplacian(A)
    first = eigenvalue_multiplicity_pattern(L, n_lowest=3)
    second = eigenvalue_multiplicity_pattern(L, n_lowest=3)
    assert first == second  # no hidden search/adaptive state


# --- H4C pattern match report: honest, never target-conditioned ------------

def test_h4c_report_on_a_generic_graph_does_not_match_and_says_so_honestly():
    A = graph_laplacian.build_graph("path", 10).adjacency()
    L = graph_laplacian.laplacian(A)
    report = h4c_pattern_match_report(L)
    assert report["claim_id"] == "H4C"
    assert report["required_pattern_per_SEIT_7"] == [3, 2, 1]
    assert report["matches"] is False  # path graph genuinely doesn't match
    assert "does not search for" in report["caveat"]
    assert "would not by itself" in report["caveat"]


def test_h4c_report_never_searches_it_only_measures_what_is_given():
    """Calling the report on two DIFFERENT, independently-chosen graphs
    must never internally try other graphs to find a match -- confirmed
    by checking each report's observed pattern is exactly what that
    SPECIFIC graph's own spectrum has, with no side effects."""
    A1 = graph_laplacian.build_graph("star", 6).adjacency()
    L1 = graph_laplacian.laplacian(A1)
    A2 = graph_laplacian.build_graph("grid2d", 3).adjacency()
    L2 = graph_laplacian.laplacian(A2)
    r1 = h4c_pattern_match_report(L1)
    r2 = h4c_pattern_match_report(L2)
    assert r1["observed_multiplicity_pattern_lowest_3"] == eigenvalue_multiplicity_pattern(L1, n_lowest=3)
    assert r2["observed_multiplicity_pattern_lowest_3"] == eigenvalue_multiplicity_pattern(L2, n_lowest=3)


# --- .seit integration -------------------------------------------------------

def test_full_gauge_pipeline_zero_external_inputs():
    src = (
        'derive G = build_graph("star", 6); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "derive result = h4c_pattern_match_report(L);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **GAUGE_BRANCH_TRANSFORMATIONS}
    bindings = {**PHYSICS_KERNEL_BINDINGS, **GAUGE_BRANCH_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}
    env = evaluate_program(dag, program, inputs={}, bindings=bindings)
    assert env["result"]["claim_id"] == "H4C"
    assert isinstance(env["result"]["matches"], bool)
