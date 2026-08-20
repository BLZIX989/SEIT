"""Tests for seit_lang.semantic (Phase 2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.parser import parse
from seit_lang.semantic import (
    ArgumentError,
    RedeclarationError,
    TypeMismatchError,
    UndeclaredIdentifierError,
    UnknownTypeError,
    check_program,
)
from seit_lang.types import UNRESOLVED

FIXTURES = Path(__file__).parent / "fixtures"


# --- the brief's literal milestone example --------------------------------

def test_milestone_fixture_as_written_flags_undeclared_beta():
    """The brief's own spectral_test.seit example calls
    heat_kernel(L, beta) without ever declaring `beta`. Phase 2's job is
    to catch exactly this kind of thing at compile time rather than
    silently accepting it -- this is a real gap in the example program,
    not a bug in the checker, so it is asserted here rather than papered
    over."""
    program = parse((FIXTURES / "spectral_test.seit").read_text())
    with pytest.raises(UndeclaredIdentifierError):
        check_program(program)


def test_completed_fixture_with_beta_declared_type_checks_cleanly():
    program = parse((FIXTURES / "spectral_test_complete.seit").read_text())
    result = check_program(program)
    assert result.module_name == "spectral_test"
    assert result.symbols["B"] == "IncidenceMatrix"
    assert result.symbols["L"] == "Laplacian"  # declared type stands, not widened to Matrix
    assert result.symbols["beta"] == "Scalar"
    assert result.unresolved_calls == []


# --- declarations ----------------------------------------------------------

def test_variable_decl_with_unknown_type_raises():
    with pytest.raises(UnknownTypeError):
        check_program(parse("variable X: NotAType;"))


def test_redeclaring_a_name_raises():
    with pytest.raises(RedeclarationError):
        check_program(parse("variable X: Scalar; variable X: Vector;"))


def test_constant_decl_with_compatible_initializer():
    result = check_program(parse("constant beta: Scalar = 2.5;"))
    assert result.symbols["beta"] == "Scalar"


def test_constant_decl_with_incompatible_initializer_raises():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable G: Graph; constant beta: Scalar = G;"))


def test_primitive_decl():
    result = check_program(parse("primitive D: Operator;"))
    assert result.symbols["D"] == "Operator"
    assert result.kinds["D"] == "primitive"


# --- operator declarations register new transformations --------------------

def test_operator_decl_registers_callable_transformation():
    src = "operator my_op(x: Matrix): Scalar; variable M: Matrix; verify my_op(M);"
    result = check_program(parse(src))
    assert "my_op" in result.transformations
    assert result.unresolved_calls == []


def test_operator_decl_duplicate_name_raises():
    with pytest.raises(RedeclarationError):
        check_program(parse("operator transpose(x: Matrix): Matrix;"))


def test_calling_operator_before_its_declaration_is_unresolved():
    # declare-before-use: a call preceding its `operator` decl in program
    # order is treated as unresolved, not retroactively resolved.
    src = "variable M: Matrix; verify my_op(M); operator my_op(x: Matrix): Scalar;"
    result = check_program(parse(src))
    assert len(result.unresolved_calls) == 1
    assert result.unresolved_calls[0].callee == "my_op"


# --- unresolved transformations ---------------------------------------------

def test_unregistered_call_is_unresolved_not_an_error():
    result = check_program(parse("variable M: Matrix; derive X = some_unknown_fn(M);"))
    assert result.symbols["X"] == UNRESOLVED
    assert len(result.unresolved_calls) == 1
    assert result.unresolved_calls[0].callee == "some_unknown_fn"


def test_unresolved_propagates_through_arithmetic_without_error():
    src = "variable M: Matrix; definition Y = some_unknown_fn(M) * M;"
    result = check_program(parse(src))
    assert result.symbols["Y"] == UNRESOLVED


def test_undeclared_identifier_still_errors_even_inside_unresolved_call_args():
    with pytest.raises(UndeclaredIdentifierError):
        check_program(parse("derive X = some_unknown_fn(never_declared);"))


# --- registered-transformation argument checking ----------------------------

def test_wrong_arg_count_to_registered_transformation_raises():
    with pytest.raises(ArgumentError):
        check_program(parse("variable M: Matrix; derive spectrum(M, M);"))


def test_incompatible_arg_type_to_registered_transformation_raises():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable v: Vector; derive spectrum(v);"))


def test_subtype_argument_accepted_by_registered_transformation():
    result = check_program(parse("variable B: IncidenceMatrix; derive transpose(B);"))
    assert result.unresolved_calls == []


# --- binary operator type rules ---------------------------------------------

def test_incompatible_operand_types_for_plus_raises():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable s: Scalar; variable v: Vector; definition x = s + v;"))


def test_scalar_times_matrix_is_scaling_not_an_error():
    result = check_program(parse("variable M: Matrix; constant c: Scalar = 2.0; definition Y = c * M;"))
    assert result.symbols["Y"] == "Matrix"


def test_matrix_times_matrix_widens_to_common_ancestor():
    src = "variable B: IncidenceMatrix; variable L: Laplacian; definition Y = B * L;"
    with pytest.raises(TypeMismatchError):
        # IncidenceMatrix and Laplacian are SIBLINGS (both specialize
        # Matrix) -- not comparable to each other, so this must fail.
        check_program(parse(src))


def test_equality_between_comparable_types_yields_scalar():
    result = check_program(parse("variable L: Laplacian; variable M: Matrix; definition ok = L == M;"))
    assert result.symbols["ok"] == "Scalar"


def test_equality_between_incomparable_types_raises():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable s: Scalar; variable v: Vector; definition ok = s == v;"))


# --- derive/calculate target binding -----------------------------------------

def test_derive_into_predeclared_variable_keeps_declared_type():
    src = "variable B: IncidenceMatrix; variable L: Laplacian; derive L = B * transpose(B);"
    result = check_program(parse(src))
    assert result.symbols["L"] == "Laplacian"


def test_derive_into_fresh_name_binds_inferred_type():
    result = check_program(parse("variable M: Matrix; derive X = transpose(M);"))
    assert result.symbols["X"] == "Matrix"
    assert result.kinds["X"] == "derived"


def test_derive_incompatible_type_into_predeclared_variable_raises():
    src = "variable s: Scalar; variable v: Vector; derive s = v;"
    with pytest.raises(TypeMismatchError):
        check_program(parse(src))


def test_derive_bare_expression_form_requires_no_target():
    result = check_program(parse("variable M: Matrix; derive transpose(M);"))
    assert "M" in result.symbols  # untouched
    assert len(result.symbols) == 1  # no phantom binding created


# --- verify / theorem / lemma require scalar-valued expressions -------------

def test_verify_non_scalar_expression_raises():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable M: Matrix; verify M;"))


def test_verify_call_result_ok():
    result = check_program(parse("variable M: Matrix; verify symmetric(M);"))
    assert result.unresolved_calls == []


def test_theorem_and_lemma_declare_theorem_typed_names():
    src = "variable L: Laplacian; theorem T1: L == L; lemma L1: L == L;"
    result = check_program(parse(src))
    assert result.symbols["T1"] == "Theorem"
    assert result.symbols["L1"] == "Theorem"
    assert result.kinds["L1"] == "lemma"


# --- equation / assumption / definition -------------------------------------

def test_equation_decl_binds_equation_type_regardless_of_body():
    src = "variable B: IncidenceMatrix; variable L: Laplacian; equation heat_eq: L = B * transpose(B);"
    result = check_program(parse(src))
    assert result.symbols["heat_eq"] == "Equation"


def test_assumption_decl_requires_scalar_body():
    with pytest.raises(TypeMismatchError):
        check_program(parse("variable M: Matrix; assumption bad: M;"))


def test_assumption_decl_binds_scalar_type():
    result = check_program(parse("variable L: Laplacian; assumption nondeg: det(L) != 0;"))
    assert result.symbols["nondeg"] == "Scalar"


# --- dependency, audit, status, provenance, output --------------------------

def test_dependency_decl_registers_forward_references_as_unresolved():
    result = check_program(parse("dependency spectrum_result -> L, B;"))
    assert result.symbols["spectrum_result"] == UNRESOLVED
    assert result.symbols["L"] == UNRESOLVED
    assert result.symbols["B"] == UNRESOLVED
    assert result.dependency_edges == [("spectrum_result", "L"), ("spectrum_result", "B")]


def test_dependency_decl_does_not_clobber_a_real_prior_declaration():
    src = "variable L: Laplacian; dependency X -> L;"
    result = check_program(parse(src))
    assert result.symbols["L"] == "Laplacian"


def test_audit_status_provenance_output_require_declared_target():
    with pytest.raises(UndeclaredIdentifierError):
        check_program(parse("audit nope;"))
    with pytest.raises(UndeclaredIdentifierError):
        check_program(parse("status nope = VERIFIED;"))
    with pytest.raises(UndeclaredIdentifierError):
        check_program(parse('provenance nope = "x";'))
    with pytest.raises(UndeclaredIdentifierError):
        check_program(parse("output nope;"))


def test_audit_status_provenance_output_on_declared_target_ok():
    src = 'variable L: Laplacian; audit L; status L = VERIFIED; provenance L = "run"; output L;'
    result = check_program(parse(src))  # must not raise
    assert result.symbols["L"] == "Laplacian"


def test_report_statement_is_a_no_op():
    result = check_program(parse("report;"))
    assert result.symbols == {}
