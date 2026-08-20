"""Tests for seit_lang.parser (Phase 1)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang import ast_nodes as ast
from seit_lang.parser import ParseError, parse
from seit_lang.lexer import LexError


FIXTURE = (Path(__file__).parent / "fixtures" / "spectral_test.seit").read_text()


def test_parses_milestone_fixture_program_end_to_end():
    program = parse(FIXTURE)
    assert isinstance(program, ast.Program)
    kinds = [type(stmt).__name__ for stmt in program.statements]
    assert kinds == [
        "ModuleDecl", "VariableDecl", "VariableDecl", "DeriveStmt",
        "VerifyStmt", "VerifyStmt", "DeriveStmt", "DeriveStmt", "ReportStmt",
    ]


def test_module_decl():
    program = parse("module spectral_test;")
    decl = program.statements[0]
    assert isinstance(decl, ast.ModuleDecl)
    assert decl.name == "spectral_test"


def test_variable_decl_records_name_and_type():
    program = parse("variable B: IncidenceMatrix;")
    decl = program.statements[0]
    assert isinstance(decl, ast.VariableDecl)
    assert decl.name == "B"
    assert decl.type.name == "IncidenceMatrix"


def test_constant_decl_with_expression():
    program = parse("constant beta: Scalar = 2.5;")
    decl = program.statements[0]
    assert isinstance(decl, ast.ConstantDecl)
    assert decl.name == "beta"
    assert decl.type.name == "Scalar"
    assert isinstance(decl.value, ast.NumberLit)
    assert decl.value.value == 2.5


def test_primitive_decl():
    program = parse("primitive D: Operator;")
    decl = program.statements[0]
    assert isinstance(decl, ast.PrimitiveDecl)
    assert decl.name == "D"


def test_operator_decl_with_params_and_return_type():
    program = parse("operator heat_kernel(L: Laplacian, beta: Scalar): Operator;")
    decl = program.statements[0]
    assert isinstance(decl, ast.OperatorDecl)
    assert decl.name == "heat_kernel"
    assert [p.name for p in decl.params] == ["L", "beta"]
    assert [p.type.name for p in decl.params] == ["Laplacian", "Scalar"]
    assert decl.return_type.name == "Operator"


def test_operator_decl_with_no_params():
    program = parse("operator identity(): Operator;")
    decl = program.statements[0]
    assert decl.params == []


def test_equation_decl():
    program = parse("equation heat_eq: L = B * transpose(B);")
    decl = program.statements[0]
    assert isinstance(decl, ast.EquationDecl)
    assert decl.name == "heat_eq"
    assert isinstance(decl.expr, ast.BinaryOp)
    assert decl.expr.op == "="


def test_definition_decl():
    program = parse("definition x = 1 + 2;")
    decl = program.statements[0]
    assert isinstance(decl, ast.DefinitionDecl)
    assert decl.name == "x"


def test_assumption_decl():
    program = parse("assumption nondegenerate: det(L) != 0;")
    decl = program.statements[0]
    assert isinstance(decl, ast.AssumptionDecl)
    assert isinstance(decl.expr, ast.BinaryOp)
    assert decl.expr.op == "!="


def test_dependency_decl_single_and_multiple():
    program = parse("dependency L -> B; dependency spectrum -> L, B;")
    d1, d2 = program.statements
    assert isinstance(d1, ast.DependencyDecl)
    assert d1.depends_on == ["B"]
    assert d2.depends_on == ["L", "B"]


def test_derive_bound_form():
    program = parse("derive L = B * transpose(B);")
    stmt = program.statements[0]
    assert isinstance(stmt, ast.DeriveStmt)
    assert stmt.target == "L"
    assert isinstance(stmt.expr, ast.BinaryOp)
    assert stmt.expr.op == "*"


def test_derive_bare_expression_form():
    program = parse("derive spectrum(L);")
    stmt = program.statements[0]
    assert isinstance(stmt, ast.DeriveStmt)
    assert stmt.target is None
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == "spectrum"
    assert [a.name for a in stmt.expr.args] == ["L"]


def test_calculate_statement_bound_and_bare():
    program = parse("calculate x = 1 + 1; calculate norm(x);")
    s1, s2 = program.statements
    assert isinstance(s1, ast.CalculateStmt) and s1.target == "x"
    assert isinstance(s2, ast.CalculateStmt) and s2.target is None


def test_verify_statement_with_call_expression():
    program = parse("verify symmetric(L);")
    stmt = program.statements[0]
    assert isinstance(stmt, ast.VerifyStmt)
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == "symmetric"


def test_theorem_and_lemma_decls():
    program = parse("theorem T1: L = transpose(L); lemma L1: det(L) == 0;")
    thm, lem = program.statements
    assert isinstance(thm, ast.TheoremDecl) and thm.name == "T1"
    assert isinstance(lem, ast.LemmaDecl) and lem.name == "L1"


def test_audit_status_provenance_output_statements():
    program = parse('audit L; status L = VERIFIED; provenance L = "compiler run 2026"; output L;')
    audit, status, prov, out = program.statements
    assert isinstance(audit, ast.AuditStmt) and audit.target == "L"
    assert isinstance(status, ast.StatusStmt) and status.value == "VERIFIED"
    assert isinstance(prov, ast.ProvenanceStmt) and prov.value == "compiler run 2026"
    assert isinstance(out, ast.OutputStmt) and out.target == "L"


def test_report_statement():
    program = parse("report;")
    assert isinstance(program.statements[0], ast.ReportStmt)


def test_nested_call_and_binary_precedence():
    program = parse("derive L = B * transpose(B);")
    expr = program.statements[0].expr
    assert isinstance(expr, ast.BinaryOp) and expr.op == "*"
    assert isinstance(expr.left, ast.Identifier) and expr.left.name == "B"
    assert isinstance(expr.right, ast.Call) and expr.right.callee == "transpose"


def test_operator_precedence_additive_vs_term():
    # 1 + 2 * 3 must parse as 1 + (2 * 3), not (1 + 2) * 3
    program = parse("definition x = 1 + 2 * 3;")
    expr = program.statements[0].expr
    assert isinstance(expr, ast.BinaryOp) and expr.op == "+"
    assert isinstance(expr.left, ast.NumberLit) and expr.left.value == 1
    assert isinstance(expr.right, ast.BinaryOp) and expr.right.op == "*"


def test_parenthesized_expression_overrides_precedence():
    program = parse("definition x = (1 + 2) * 3;")
    expr = program.statements[0].expr
    assert isinstance(expr, ast.BinaryOp) and expr.op == "*"
    assert isinstance(expr.left, ast.BinaryOp) and expr.left.op == "+"


def test_unary_minus():
    program = parse("definition x = -1;")
    expr = program.statements[0].expr
    assert isinstance(expr, ast.UnaryOp) and expr.op == "-"
    assert expr.operand.value == 1


def test_multi_arg_call():
    program = parse("derive heat_kernel(L, beta);")
    expr = program.statements[0].expr
    assert isinstance(expr, ast.Call)
    assert [a.name for a in expr.args] == ["L", "beta"]


def test_string_literal_expression():
    program = parse('provenance L = "run 1";')
    stmt = program.statements[0]
    assert stmt.value == "run 1"


# --- error cases ---------------------------------------------------------

def test_missing_semicolon_raises_parse_error():
    with pytest.raises(ParseError):
        parse("module m")


def test_missing_type_after_colon_raises_parse_error():
    with pytest.raises(ParseError):
        parse("variable B: ;")


def test_identifier_in_statement_position_raises_parse_error():
    # "nonsense" is a valid IDENT token, not a statement keyword -- this is
    # a parse-level error (unexpected token), not a lex-level one.
    with pytest.raises(ParseError):
        parse("nonsense B;")


def test_truly_unlexable_character_raises_lex_error():
    with pytest.raises(LexError):
        parse("variable B: T; @")


def test_calling_a_non_identifier_raises_parse_error():
    with pytest.raises(ParseError):
        parse("definition x = 1(2);")


def test_empty_program_parses_to_empty_statement_list():
    program = parse("")
    assert program.statements == []


def test_unclosed_paren_raises_parse_error():
    with pytest.raises(ParseError):
        parse("derive spectrum(L;")
