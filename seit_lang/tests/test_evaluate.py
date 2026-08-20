"""Tests for seit_lang.evaluate (Phase 5)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang import ast_nodes as ast
from seit_lang.dag import compile_dag
from seit_lang.evaluate import UnboundInputError, UnboundTransformationError, evaluate_expr, evaluate_program
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program

FIXTURES = Path(__file__).parent / "fixtures"


# --- evaluate_expr: literals, identifiers, operators, calls ----------------

def test_number_literal():
    expr = ast.NumberLit(1, 1, 3.0)
    assert evaluate_expr(expr, {}, {}) == 3.0


def test_string_literal():
    expr = ast.StringLit(1, 1, "hello")
    assert evaluate_expr(expr, {}, {}) == "hello"


def test_identifier_looks_up_env():
    expr = ast.Identifier(1, 1, "x")
    assert evaluate_expr(expr, {"x": 42}, {}) == 42


def test_identifier_missing_raises_unbound_input_error():
    expr = ast.Identifier(1, 1, "missing")
    with pytest.raises(UnboundInputError):
        evaluate_expr(expr, {}, {})


def test_unary_minus():
    expr = ast.UnaryOp(1, 1, "-", ast.NumberLit(1, 1, 5.0))
    assert evaluate_expr(expr, {}, {}) == -5.0


def test_binary_arithmetic():
    expr = ast.BinaryOp(1, 1, "+", ast.NumberLit(1, 1, 2.0), ast.NumberLit(1, 1, 3.0))
    assert evaluate_expr(expr, {}, {}) == 5.0


def test_binary_star_between_two_matrices_is_matrix_multiplication_not_elementwise():
    # a real, non-commuting-under-elementwise pair so the two
    # interpretations would actually disagree if the wrong one were used
    A = np.array([[1.0, 1.0], [0.0, 1.0]])
    B = np.array([[1.0, 0.0], [1.0, 1.0]])
    expr = ast.BinaryOp(1, 1, "*", ast.Identifier(1, 1, "A"), ast.Identifier(1, 1, "B"))
    result = evaluate_expr(expr, {"A": A, "B": B}, {})
    assert np.array_equal(result, A @ B)
    assert not np.array_equal(result, A * B)  # elementwise would give a DIFFERENT, wrong answer here


def test_binary_star_scalar_times_matrix_is_ordinary_scaling():
    M = np.array([[1.0, 2.0], [3.0, 4.0]])
    expr = ast.BinaryOp(1, 1, "*", ast.NumberLit(1, 1, 2.0), ast.Identifier(1, 1, "M"))
    result = evaluate_expr(expr, {"M": M}, {})
    assert np.array_equal(result, 2.0 * M)


def test_equality_true_for_close_arrays():
    A = np.array([1.0, 2.0, 3.0])
    B = np.array([1.0, 2.0, 3.0 + 1e-12])
    expr = ast.BinaryOp(1, 1, "==", ast.Identifier(1, 1, "A"), ast.Identifier(1, 1, "B"))
    assert evaluate_expr(expr, {"A": A, "B": B}, {}) is True


def test_equality_false_for_different_arrays():
    A = np.array([1.0, 2.0])
    B = np.array([1.0, 9.0])
    expr = ast.BinaryOp(1, 1, "==", ast.Identifier(1, 1, "A"), ast.Identifier(1, 1, "B"))
    assert evaluate_expr(expr, {"A": A, "B": B}, {}) is False


def test_not_equal_operator():
    expr = ast.BinaryOp(1, 1, "!=", ast.NumberLit(1, 1, 1.0), ast.NumberLit(1, 1, 2.0))
    assert evaluate_expr(expr, {}, {}) is True


def test_call_invokes_bound_primitive():
    M = np.array([[1.0, 2.0], [3.0, 4.0]])
    expr = ast.Call(1, 1, "transpose", [ast.Identifier(1, 1, "M")])
    result = evaluate_expr(expr, {"M": M}, PHYSICS_KERNEL_BINDINGS)
    assert np.array_equal(result, M.T)


def test_call_to_unbound_transformation_raises():
    expr = ast.Call(1, 1, "nonexistent_fn", [ast.NumberLit(1, 1, 1.0)])
    with pytest.raises(UnboundTransformationError):
        evaluate_expr(expr, {}, {})


# --- evaluate_program: full pipeline, zero external inputs needed ----------

def test_full_graph_pipeline_computes_with_zero_external_inputs():
    """Unlike the milestone example's `variable B` (an undriven input),
    a program that constructs its own graph via build_graph() has NO
    unset leaf inputs -- it should compile to all-CALCULATED and
    evaluate end to end with inputs={}."""
    src = (
        'derive G = build_graph("cycle", 6); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "derive S = spectrum(L); "
        "derive gap = spectral_gap(S);"
    )
    program = parse(src)
    check_result = check_program(program, extra_transformations=PHYSICS_KERNEL_TRANSFORMATIONS)
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}
    for name in ("G", "A", "L", "S", "gap"):
        assert dag.states[name].value == "CALCULATED"

    env = evaluate_program(dag, program, inputs={}, bindings=PHYSICS_KERNEL_BINDINGS)
    assert env["G"].n == 6
    assert env["A"].shape == (6, 6)
    assert env["L"].shape == (6, 6)
    assert np.allclose(env["L"], env["L"].T)  # a real graph Laplacian is symmetric
    assert env["gap"] > 0  # a connected cycle has a nonzero spectral gap


def test_verify_expression_evaluates_true_on_real_computed_laplacian():
    src = (
        'derive G = build_graph("path", 5); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A);"
    )
    program = parse(src)
    check_result = check_program(program, extra_transformations=PHYSICS_KERNEL_TRANSFORMATIONS)
    dag = compile_dag(program, check_result)
    env = evaluate_program(dag, program, inputs={}, bindings=PHYSICS_KERNEL_BINDINGS)
    verify_expr = ast.Call(1, 1, "symmetric", [ast.Identifier(1, 1, "L")])
    assert evaluate_expr(verify_expr, env, PHYSICS_KERNEL_BINDINGS) is True


# --- honest failure: unsupplied inputs, matching Phase 4's BLOCKED finding -

def test_milestone_fixture_raises_unbound_input_for_B_without_supplied_input():
    program = parse((FIXTURES / "spectral_test_complete.seit").read_text())
    dag = compile_dag(program)
    with pytest.raises(UnboundInputError) as excinfo:
        evaluate_program(dag, program, inputs={}, bindings=PHYSICS_KERNEL_BINDINGS)
    assert excinfo.value.name == "B"


def test_milestone_fixture_computes_correctly_once_B_is_supplied():
    program = parse((FIXTURES / "spectral_test_complete.seit").read_text())
    dag = compile_dag(program)
    B = np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    env = evaluate_program(dag, program, inputs={"B": B}, bindings=PHYSICS_KERNEL_BINDINGS)
    assert np.allclose(env["L"], B @ B.T)


def test_a_node_nothing_depends_on_being_unbound_does_not_error():
    # `unused` is declared but nothing in the program references it --
    # evaluate_program must not spuriously demand a value for it.
    src = "variable unused: Scalar; constant x: Scalar = 1.0; definition y = x * x;"
    program = parse(src)
    check_result = check_program(program)
    dag = compile_dag(program, check_result)
    env = evaluate_program(dag, program, inputs={}, bindings={})
    assert env["y"] == 1.0
    assert "unused" not in env
