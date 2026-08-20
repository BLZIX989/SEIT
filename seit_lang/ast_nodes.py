"""AST node definitions for the `.seit` language (Phase 1 -- see
GRAMMAR.md). Plain dataclasses -- no behavior here; Phase 2+ (type
checker, DAG compiler, CLI) walks this tree, it does not extend it with
methods here.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    line: int
    column: int


# --- expressions -------------------------------------------------------

@dataclass(frozen=True)
class NumberLit(Node):
    value: float


@dataclass(frozen=True)
class StringLit(Node):
    value: str


@dataclass(frozen=True)
class Identifier(Node):
    name: str


@dataclass(frozen=True)
class UnaryOp(Node):
    op: str  # "-"
    operand: "Expr"


@dataclass(frozen=True)
class BinaryOp(Node):
    op: str  # "+", "-", "*", "/", "=", "==", "!="
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Call(Node):
    callee: str
    args: list["Expr"] = field(default_factory=list)


Expr = NumberLit | StringLit | Identifier | UnaryOp | BinaryOp | Call


# --- type expressions (Phase 1: bare identifier; Phase 2 gives meaning) ---

@dataclass(frozen=True)
class TypeExpr(Node):
    name: str


@dataclass(frozen=True)
class Param(Node):
    name: str
    type: TypeExpr


# --- statements ----------------------------------------------------------

@dataclass(frozen=True)
class ModuleDecl(Node):
    name: str


@dataclass(frozen=True)
class VariableDecl(Node):
    name: str
    type: TypeExpr


@dataclass(frozen=True)
class ConstantDecl(Node):
    name: str
    type: TypeExpr
    value: Expr


@dataclass(frozen=True)
class PrimitiveDecl(Node):
    name: str
    type: TypeExpr


@dataclass(frozen=True)
class OperatorDecl(Node):
    name: str
    params: list[Param]
    return_type: TypeExpr


@dataclass(frozen=True)
class EquationDecl(Node):
    name: str
    expr: Expr


@dataclass(frozen=True)
class DefinitionDecl(Node):
    name: str
    expr: Expr


@dataclass(frozen=True)
class AssumptionDecl(Node):
    name: str
    expr: Expr


@dataclass(frozen=True)
class DependencyDecl(Node):
    name: str
    depends_on: list[str]


@dataclass(frozen=True)
class DeriveStmt(Node):
    target: str | None  # None for the bare-expression form, e.g. `derive spectrum(L);`
    expr: Expr


@dataclass(frozen=True)
class CalculateStmt(Node):
    target: str | None
    expr: Expr


@dataclass(frozen=True)
class VerifyStmt(Node):
    expr: Expr


@dataclass(frozen=True)
class TheoremDecl(Node):
    name: str
    expr: Expr


@dataclass(frozen=True)
class LemmaDecl(Node):
    name: str
    expr: Expr


@dataclass(frozen=True)
class AuditStmt(Node):
    target: str


@dataclass(frozen=True)
class StatusStmt(Node):
    target: str
    value: str


@dataclass(frozen=True)
class ProvenanceStmt(Node):
    target: str
    value: str


@dataclass(frozen=True)
class OutputStmt(Node):
    target: str


@dataclass(frozen=True)
class ReportStmt(Node):
    pass


Statement = (
    ModuleDecl | VariableDecl | ConstantDecl | PrimitiveDecl | OperatorDecl
    | EquationDecl | DefinitionDecl | AssumptionDecl | DependencyDecl
    | DeriveStmt | CalculateStmt | VerifyStmt | TheoremDecl | LemmaDecl
    | AuditStmt | StatusStmt | ProvenanceStmt | OutputStmt | ReportStmt
)


@dataclass(frozen=True)
class Program(Node):
    statements: list[Statement] = field(default_factory=list)
