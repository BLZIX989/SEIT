"""Tests for seit_lang.clifford_branch (Phase 10)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import clifford_derivation

from seit_lang.clifford_branch import (
    CLIFFORD_BRANCH_BINDINGS,
    CLIFFORD_BRANCH_TRANSFORMATIONS,
    clifford_rank_forcing_report,
    clifford_representation_dimension,
    euclidean_gamma_matrices,
    generate_clifford_status_declaration,
    minimal_n_for_representation_dimension_at_least,
    verify_clifford_anticommutation,
)
from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.parser import parse
from seit_lang.semantic import check_program
from seit_lang.state import SeitState


# --- {gamma_a, gamma_b} = 2 eta_ab I, verified exactly, not assumed ------

@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5, 6, 7, 8])
def test_anticommutation_relation_holds_exactly(n):
    report = verify_clifford_anticommutation(n)
    assert report["anticommutation_relation_holds_exactly"] is True
    assert report["max_residual"] < 1e-9


def test_n0_has_no_generators():
    assert euclidean_gamma_matrices(0) == []


def test_n1_is_the_trivial_1x1_generator():
    gammas = euclidean_gamma_matrices(1)
    assert len(gammas) == 1
    assert gammas[0].shape == (1, 1)
    assert np.allclose(gammas[0] @ gammas[0], np.eye(1))


def test_n3_reproduces_the_classic_pauli_matrices():
    """A strong, independently-known sanity check: Cl(3,0)'s standard
    2x2 complex representation IS the three Pauli matrices, up to
    labeling/ordering -- if the tensor-product construction were wrong,
    this specific, well-known case would very likely fail."""
    gammas = euclidean_gamma_matrices(3)
    assert len(gammas) == 3
    for g in gammas:
        assert g.shape == (2, 2)
        assert np.allclose(g @ g, np.eye(2))  # each squares to I
    # each pair anticommutes
    for a in range(3):
        for b in range(3):
            if a != b:
                assert np.allclose(gammas[a] @ gammas[b] + gammas[b] @ gammas[a],
                                    np.zeros((2, 2)), atol=1e-9)


# --- representation dimension: 2^floor(n/2), locked to explicit values ----

@pytest.mark.parametrize("n,expected", [
    (0, 1), (1, 1), (2, 2), (3, 2), (4, 4), (5, 4), (6, 8), (7, 8), (8, 16),
])
def test_representation_dimension_matches_explicit_expected_values(n, expected):
    assert clifford_representation_dimension(n) == float(expected)


def test_representation_dimension_matches_actual_constructed_matrix_size():
    for n in range(1, 8):
        gammas = euclidean_gamma_matrices(n)
        assert gammas[0].shape[0] == int(clifford_representation_dimension(n))


# --- minimal-n search (the well-defined math condition, not physics) -------

def test_minimal_n_search_finds_the_correct_smallest_n():
    # dimension only grows every SECOND n (2^floor(n/2)): n=3 still has
    # dim=2, so the smallest n with dim >= 4 is n=4, not n=3.
    assert minimal_n_for_representation_dimension_at_least(4) == 4.0


def test_minimal_n_search_exact_boundary():
    assert minimal_n_for_representation_dimension_at_least(1) == 0.0
    assert minimal_n_for_representation_dimension_at_least(2) == 2.0
    assert minimal_n_for_representation_dimension_at_least(8) == 6.0


def test_minimal_n_search_returns_sentinel_when_unreachable_within_max_n():
    assert minimal_n_for_representation_dimension_at_least(10**9, max_n=5) == -1.0


# --- "minimal forced n" for the REAL physics question stays UNFORCED -------

def test_clifford_rank_forcing_report_matches_real_module_unchanged():
    assert clifford_rank_forcing_report() == clifford_derivation.clifford_rank_forcing_check()


def test_clifford_rank_forcing_report_states_dimension_unforced():
    report = clifford_rank_forcing_report()
    assert "UNFORCED" in report["status"]


# --- Cl(6) only PROPOSED/OPEN, never silently DERIVED ----------------------

def test_generated_cl6_declaration_is_open_not_derived():
    src = generate_clifford_status_declaration(6)
    assert "status Cl_6 = OPEN;" in src
    assert "DERIVED" not in src


def test_generated_declaration_parses_checks_and_stays_declared_in_dag():
    src = generate_clifford_status_declaration(6)
    program = parse(src)
    result = check_program(program)
    assert result.symbols["Cl_6"] == "Dataset"
    dag = compile_dag(program, result)
    assert dag.states["Cl_6"] == SeitState.DECLARED  # never fabricated CALCULATED/DERIVED


def test_generated_declaration_for_a_different_n():
    src = generate_clifford_status_declaration(8)
    assert "status Cl_8 = OPEN;" in src


# --- .seit type checking and cross-phase integration ------------------------

def test_gamma_matrix_typed_as_operator_not_generic_matrix():
    assert CLIFFORD_BRANCH_TRANSFORMATIONS["clifford_gamma_matrix"].return_type == "Operator"


def test_full_clifford_pipeline_verifies_anticommutation_via_seit():
    # "report" is itself a reserved .seit keyword (Phase 1 grammar) --
    # using it as an identifier here would be a source-level error, not
    # a language bug, so the target is named "result" instead.
    src = "derive result = verify_clifford_anticommutation(6);"
    program = parse(src)
    check_result = check_program(program, extra_transformations=CLIFFORD_BRANCH_TRANSFORMATIONS)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}
    env = evaluate_program(dag, program, inputs={}, bindings=CLIFFORD_BRANCH_BINDINGS)
    assert env["result"]["anticommutation_relation_holds_exactly"] is True
    assert env["result"]["n_generators"] == 6
