"""Tests for seit_lang.dag (Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.dag import DagCompileError, compile_dag
from seit_lang.parser import parse
from seit_lang.state import SeitState

FIXTURES = Path(__file__).parent / "fixtures"


# --- the milestone example, honestly reported --------------------------

def test_milestone_fixture_L_is_blocked_because_B_is_never_computed():
    """B is only ever `variable`-declared, never derive/calculate'd --
    Phase 4 must not pretend it has a value. L, which depends on it, is
    correctly reported BLOCKED rather than CALCULATED."""
    program = parse((FIXTURES / "spectral_test_complete.seit").read_text())
    dag = compile_dag(program)
    assert dag.states["B"] == SeitState.DECLARED
    assert dag.states["L"] == SeitState.BLOCKED
    assert "L" in dag.blocked


def test_milestone_fixture_edge_from_B_to_L_recorded_with_transformation():
    program = parse((FIXTURES / "spectral_test_complete.seit").read_text())
    dag = compile_dag(program)
    edge = dag.edges[("B", "L")]
    assert edge.source == "B"
    assert edge.target == "L"
    assert edge.transformation == "binary:*"


# --- explicit dependency declarations ---------------------------------

def test_explicit_dependency_decl_creates_edge():
    program = parse("variable L: Laplacian; variable B: IncidenceMatrix; dependency L -> B;")
    dag = compile_dag(program)
    edge = dag.edges[("B", "L")]
    assert edge.transformation == "dependency declaration"


# --- implicit edges from producing statements ---------------------------

def test_implicit_edge_from_call_uses_callee_as_transformation():
    program = parse("variable M: Matrix; definition N = transpose(M);")
    dag = compile_dag(program)
    edge = dag.edges[("M", "N")]
    assert edge.transformation == "transpose"


def test_implicit_edge_from_binary_op():
    program = parse("constant x: Scalar = 1.0; constant y: Scalar = 2.0; definition z = x + y;")
    dag = compile_dag(program)
    assert dag.edges[("x", "z")].transformation == "binary:+"
    assert dag.edges[("y", "z")].transformation == "binary:+"


# --- proof obligations ---------------------------------------------------

def test_verify_statement_recorded_as_proof_obligation():
    src = "variable B: IncidenceMatrix; definition L = B * transpose(B); verify symmetric(L);"
    program = parse(src)
    dag = compile_dag(program)
    edge = dag.edges[("B", "L")]
    assert edge.proof_obligation == "symmetric(L)"


def test_missing_verify_statement_is_explicit_not_blank():
    program = parse("variable M: Matrix; definition N = transpose(M);")
    dag = compile_dag(program)
    edge = dag.edges[("M", "N")]
    assert edge.proof_obligation != ""
    assert "UNSTATED" in edge.proof_obligation
    assert "N" in edge.proof_obligation


def test_multiple_verify_statements_on_same_target_all_recorded():
    src = "variable M: Matrix; definition N = transpose(M); verify symmetric(N); verify positive_semidefinite(N);"
    dag = compile_dag(parse(src))
    obligation = dag.edges[("M", "N")].proof_obligation
    assert "symmetric(N)" in obligation
    assert "positive_semidefinite(N)" in obligation


# --- provenance -----------------------------------------------------------

def test_provenance_statement_attached_to_edges_targeting_that_node():
    src = 'variable M: Matrix; definition N = transpose(M); provenance N = "run 42";'
    dag = compile_dag(parse(src))
    assert dag.edges[("M", "N")].provenance == "run 42"


def test_no_provenance_statement_is_none_not_a_fabricated_value():
    dag = compile_dag(parse("variable M: Matrix; definition N = transpose(M);"))
    assert dag.edges[("M", "N")].provenance is None


# --- state advancement for fully-ready dependency chains -------------------

def test_constant_with_no_dependencies_reaches_calculated():
    dag = compile_dag(parse("constant x: Scalar = 2.0;"))
    assert dag.states["x"] == SeitState.CALCULATED
    assert "x" not in dag.blocked


def test_definition_chain_with_ready_dependencies_reaches_calculated():
    src = "constant x: Scalar = 2.0; definition y = x * x;"
    dag = compile_dag(parse(src))
    assert dag.states["x"] == SeitState.CALCULATED
    assert dag.states["y"] == SeitState.CALCULATED
    assert dag.blocked == {}


def test_transitive_chain_of_ready_dependencies_all_reach_calculated():
    src = "constant x: Scalar = 1.0; definition y = x * x; definition z = y + x;"
    dag = compile_dag(parse(src))
    assert dag.states["x"] == dag.states["y"] == dag.states["z"] == SeitState.CALCULATED


def test_equation_theorem_lemma_assumption_stay_declared_not_calculated():
    src = (
        "variable L: Laplacian; "
        "equation heat_eq: L == L; "
        "theorem T1: L == L; "
        "lemma L1: L == L; "
        "assumption a1: L == L;"
    )
    dag = compile_dag(parse(src))
    assert dag.states["heat_eq"] == SeitState.DECLARED
    assert dag.states["T1"] == SeitState.DECLARED
    assert dag.states["L1"] == SeitState.DECLARED
    assert dag.states["a1"] == SeitState.DECLARED


# --- cycle rejection --------------------------------------------------------

def test_cycle_via_derive_statements_raises():
    src = "variable X: Scalar; variable Y: Scalar; derive X = f(Y); derive Y = g(X);"
    with pytest.raises(DagCompileError):
        compile_dag(parse(src))


def test_cycle_via_explicit_dependency_decls_raises():
    src = "variable A: Scalar; variable B: Scalar; dependency A -> B; dependency B -> A;"
    with pytest.raises(DagCompileError):
        compile_dag(parse(src))


def test_self_dependency_is_ignored_not_treated_as_a_cycle():
    # A statement that (degenerately) references its own target name
    # must not be treated as a self-loop cycle.
    dag = compile_dag(parse("variable X: Scalar; derive X = X + 1;"))
    assert ("X", "X") not in dag.edges


# --- topological order ------------------------------------------------------

def test_topological_order_respects_dependency_edges():
    src = "constant x: Scalar = 1.0; definition y = x * x; definition z = y + x;"
    dag = compile_dag(parse(src))
    order = dag.topological_order()
    assert order.index("x") < order.index("y") < order.index("z")
