"""Tests for seit_lang.incidence_clifford (Phase 6)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian
from scientific_corpus.derivation import dirac_candidates

from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.incidence_clifford import (
    INCIDENCE_CLIFFORD_BINDINGS,
    INCIDENCE_CLIFFORD_TRANSFORMATIONS,
    block_dirac,
    edge_laplacian,
    grading_operator,
    ring_incidence_matrix,
    vertex_laplacian,
)
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program


# --- B is the same construction H2B uses -----------------------------------

def test_ring_incidence_matrix_vertex_laplacian_matches_independent_graph_backend():
    """L_A = B B^T must equal the standard D-A Laplacian of the SAME
    k-nearest-neighbour ring graph, cross-checked against
    compiler/backends/graph_laplacian.py (the same construction
    dirac_candidates.py's H2B test uses internally) -- this is the real
    load-bearing check that B is built correctly, not just "B has the
    right shape"."""
    n, k = 12, 3
    B = ring_incidence_matrix(n, k)
    L_A = vertex_laplacian(B)
    W = np.zeros((n, n))
    for i in range(n):
        for kk in range(1, k + 1):
            j = (i + kk) % n
            W[i, j] = W[j, i] = 1.0
    expected = graph_laplacian.laplacian(W)
    assert np.allclose(L_A, expected)


def test_ring_incidence_matrix_shape():
    n, k = 10, 2
    B = ring_incidence_matrix(n, k)
    assert B.shape[0] == n


# --- L_A, L_B --------------------------------------------------------------

def test_vertex_laplacian_symmetric_and_psd():
    B = ring_incidence_matrix(15, 3)
    L_A = vertex_laplacian(B)
    assert np.allclose(L_A, L_A.T)
    assert np.all(np.linalg.eigvalsh(L_A) >= -1e-8)


def test_edge_laplacian_symmetric_and_psd():
    B = ring_incidence_matrix(15, 3)
    L_B = edge_laplacian(B)
    assert np.allclose(L_B, L_B.T)
    assert np.all(np.linalg.eigvalsh(L_B) >= -1e-8)
    n, m = B.shape
    assert L_B.shape == (m, m)


# --- D_B ---------------------------------------------------------------------

def test_block_dirac_is_self_adjoint():
    B = ring_incidence_matrix(15, 3)
    D = block_dirac(B)
    assert np.allclose(D, D.T)


def test_block_dirac_squares_to_block_diagonal_of_L_A_and_L_B():
    B = ring_incidence_matrix(15, 3)
    L_A = vertex_laplacian(B)
    L_B = edge_laplacian(B)
    D = block_dirac(B)
    n, m = B.shape
    D2 = D @ D
    assert np.allclose(D2[:n, :n], L_A)
    assert np.allclose(D2[n:, n:], L_B)
    assert np.allclose(D2[:n, n:], 0)
    assert np.allclose(D2[n:, :n], 0)


# --- gamma -------------------------------------------------------------------

def test_grading_operator_is_an_involution():
    B = ring_incidence_matrix(10, 3)
    gamma = grading_operator(B)
    assert np.allclose(gamma @ gamma, np.eye(gamma.shape[0]))


def test_grading_operator_anticommutes_with_block_dirac_exactly():
    B = ring_incidence_matrix(10, 3)
    D = block_dirac(B)
    gamma = grading_operator(B)
    anticommutator = gamma @ D + D @ gamma
    assert np.allclose(anticommutator, 0.0, atol=1e-10)


def test_grading_operator_signs_match_vertex_edge_split():
    B = ring_incidence_matrix(8, 3)
    n, m = B.shape
    gamma = grading_operator(B)
    diag = np.diag(gamma)
    assert np.all(diag[:n] == 1.0)
    assert np.all(diag[n:] == -1.0)


# --- existing H2B report, unchanged, exposed as a primitive -----------------

def test_h2b_report_binding_matches_direct_call_to_existing_module():
    n, k = 30, 3
    via_binding = INCIDENCE_CLIFFORD_BINDINGS["h2b_block_dirac_report"].fn(n, k)
    direct = dirac_candidates.build_block_dirac_locality_test(n, k)
    assert via_binding == direct


def test_h2b_report_still_reports_claim_id_H2B_unchanged():
    report = INCIDENCE_CLIFFORD_BINDINGS["h2b_block_dirac_report"].fn(20, 3)
    assert report["claim_id"] == "H2B"
    assert report["D_self_adjoint"] is True


# --- .seit type checking ------------------------------------------------------

def test_block_dirac_typed_operator_not_spectral_triple():
    assert INCIDENCE_CLIFFORD_TRANSFORMATIONS["block_dirac"].return_type == "Operator"


def test_ring_incidence_matrix_param_types_are_scalar_scalar():
    sig = INCIDENCE_CLIFFORD_TRANSFORMATIONS["ring_incidence_matrix"]
    assert sig.param_types == ["Scalar", "Scalar"]
    assert sig.return_type == "IncidenceMatrix"


def test_vertex_laplacian_requires_incidence_matrix_argument_type():
    # a bare Matrix is NOT accepted where IncidenceMatrix is required --
    # this is a real, deliberate type restriction (see module docstring).
    src = "variable M: Matrix; derive vertex_laplacian(M);"
    from seit_lang.semantic import TypeMismatchError
    with pytest.raises(TypeMismatchError):
        check_program(parse(src), extra_transformations=INCIDENCE_CLIFFORD_TRANSFORMATIONS)


# --- full-stack integration: Phases 1-6 together, zero external inputs -----

def test_full_incidence_clifford_pipeline_computes_end_to_end():
    src = (
        "derive B = ring_incidence_matrix(12, 3); "
        "derive L_A = vertex_laplacian(B); "
        "derive L_B = edge_laplacian(B); "
        "derive D = block_dirac(B); "
        "derive gamma = grading_operator(B); "
        "verify symmetric(L_A);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **INCIDENCE_CLIFFORD_TRANSFORMATIONS}
    bindings = {**PHYSICS_KERNEL_BINDINGS, **INCIDENCE_CLIFFORD_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}
    for name in ("B", "L_A", "L_B", "D", "gamma"):
        assert dag.states[name].value == "CALCULATED"

    env = evaluate_program(dag, program, inputs={}, bindings=bindings)
    n, m = env["B"].shape
    D2 = env["D"] @ env["D"]
    assert np.allclose(D2[:n, :n], env["L_A"])
    assert np.allclose(D2[n:, n:], env["L_B"])
    assert np.allclose(env["gamma"] @ env["D"] + env["D"] @ env["gamma"], 0.0, atol=1e-10)
