"""Semantic type checker for `.seit` (Phase 2). Walks the AST produced by
seit_lang.parser, enforcing the type system in seit_lang.types.

Two governing rules from the brief, both implemented literally:

  1. "Prevent invalid operations at compile time" -- e.g. adding two
     unrelated types, or calling a REGISTERED transformation with the
     wrong argument count or an incompatible argument type, is a hard
     SemanticError, raised immediately (fail-fast, matching
     seit_lang.parser.ParseError's style).

  2. "Unregistered transformations remain unresolved rather than
     silently succeeding" -- calling a name that is not in the
     transformation registry (built-in or declared via an `operator`
     statement earlier in the same program) is NOT an error. It is
     recorded as an UnresolvedCall and its result type is the
     `Unresolved` pseudo-type (seit_lang.types.UNRESOLVED), which then
     propagates through further expressions without triggering false
     type errors -- because nothing here actually knows what that
     transformation returns.

Two different compatibility rules are used deliberately, not by
oversight:

  - Declaration/assignment (`variable`/`constant` type vs. a `derive`/
    `calculate` target's inferred expression type) uses
    `types.comparable()`: EITHER type may be the more specific one. This
    is what lets `variable L: Laplacian; derive L = B * transpose(B);`
    type-check even though `B * transpose(B)` only proves `Matrix` --
    the specific-subtype claim (that this Matrix really is symmetric
    positive-semidefinite, i.e. a Laplacian) is exactly what the
    program's own `verify symmetric(L); verify positive_semidefinite(L);`
    lines check, later and separately. The type system's job is to
    reject types that could never be related (Scalar assigned where a
    Spectrum is declared), not to pre-decide a claim this project's own
    VERIFIED/DERIVED discipline reserves for actual verification.

  - Function-argument passing uses strict Liskov subtyping
    (`types.is_subtype(arg_type, param_type)`): an argument must be the
    declared parameter type or a specialization of it. A transformation
    genuinely requires at least that structure to run; widening the
    other way would be unsound.

There is no Boolean type in the brief's 24-type list. Equality
comparisons (`=`/`==`/`!=`), `verify` targets, `assumption` predicates,
and theorem/lemma bodies are typed as `Scalar` by convention -- documented
here rather than silently assumed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import ast_nodes as ast
from .types import SEIT_TYPES, UNRESOLVED, comparable, is_known_type, is_subtype, widen


class SemanticError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} (line {line}, column {column})")
        self.line = line
        self.column = column


class UnknownTypeError(SemanticError):
    pass


class UndeclaredIdentifierError(SemanticError):
    pass


class RedeclarationError(SemanticError):
    pass


class TypeMismatchError(SemanticError):
    pass


class ArgumentError(SemanticError):
    pass


@dataclass(frozen=True)
class TransformationSignature:
    name: str
    param_types: list[str]
    return_type: str


@dataclass(frozen=True)
class UnresolvedCall:
    callee: str
    line: int
    column: int


# Built-in transformations covering the brief's own Phase 16 milestone
# example, plus a handful of natural companions at the same minimal
# level. This is NOT the Phase 5 physics-kernel binding (which exposes
# the real compiler/backends implementations); it is only enough
# signature information for Phase 2's type checker to do its job. Phase
# 5 must not silently redefine these signatures -- if it needs different
# ones, that is a new, documented decision, not an overwrite.
BUILTIN_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    sig.name: sig
    for sig in [
        TransformationSignature("transpose", ["Matrix"], "Matrix"),
        TransformationSignature("symmetric", ["Matrix"], "Scalar"),
        TransformationSignature("positive_semidefinite", ["Matrix"], "Scalar"),
        TransformationSignature("spectrum", ["Matrix"], "Spectrum"),
        TransformationSignature("heat_kernel", ["Matrix", "Scalar"], "Operator"),
        TransformationSignature("det", ["Matrix"], "Scalar"),
        TransformationSignature("norm", ["Vector"], "Scalar"),
    ]
}


@dataclass
class CheckResult:
    symbols: dict[str, str] = field(default_factory=dict)
    kinds: dict[str, str] = field(default_factory=dict)
    transformations: dict[str, TransformationSignature] = field(default_factory=dict)
    unresolved_calls: list[UnresolvedCall] = field(default_factory=list)
    dependency_edges: list[tuple[str, str]] = field(default_factory=list)
    module_name: str | None = None


class SemanticChecker:
    def __init__(self, extra_transformations: dict[str, TransformationSignature] | None = None) -> None:
        """`extra_transformations` (Phase 5+) supplies additional
        registered transformations beyond BUILTIN_TRANSFORMATIONS --
        e.g. real physics-kernel bindings from seit_lang.primitives. If
        a name collides with an existing signature that DIFFERS, this
        is a setup-time configuration error (raised immediately, not
        deferred to check()) -- Phase 5 must not silently redefine a
        signature Phase 2 already declared (see seit_lang/primitives.py
        module docstring)."""
        self.symbols: dict[str, str] = {}
        self.kinds: dict[str, str] = {}
        self.transformations: dict[str, TransformationSignature] = dict(BUILTIN_TRANSFORMATIONS)
        for name, sig in (extra_transformations or {}).items():
            existing = self.transformations.get(name)
            if existing is not None and existing != sig:
                raise ValueError(
                    f"extra_transformations[{name!r}] = {sig!r} conflicts with an "
                    f"already-registered signature {existing!r}")
            self.transformations[name] = sig
        self.unresolved_calls: list[UnresolvedCall] = []
        self.dependency_edges: list[tuple[str, str]] = []
        self.module_name: str | None = None

    # -- entry point --

    def check(self, program: ast.Program) -> CheckResult:
        for stmt in program.statements:
            self._check_statement(stmt)
        return CheckResult(
            symbols=dict(self.symbols),
            kinds=dict(self.kinds),
            transformations=dict(self.transformations),
            unresolved_calls=list(self.unresolved_calls),
            dependency_edges=list(self.dependency_edges),
            module_name=self.module_name,
        )

    # -- helpers --

    def _require_known_type(self, type_expr: ast.TypeExpr) -> str:
        if not is_known_type(type_expr.name):
            raise UnknownTypeError(
                f"unknown type {type_expr.name!r} (not one of the {len(SEIT_TYPES)} "
                f"declared .seit types)", type_expr.line, type_expr.column)
        return type_expr.name

    def _declare(self, name: str, type_name: str, kind: str, node: ast.Node) -> None:
        if name in self.symbols:
            raise RedeclarationError(f"{name!r} is already declared", node.line, node.column)
        self.symbols[name] = type_name
        self.kinds[name] = kind

    def _bind_derive_target(self, target: str, expr_type: str, node: ast.Node) -> None:
        if target in self.symbols:
            declared = self.symbols[target]
            if expr_type != UNRESOLVED and declared != UNRESOLVED and not comparable(expr_type, declared):
                raise TypeMismatchError(
                    f"cannot derive {target!r} (declared {declared}) from an expression of "
                    f"type {expr_type}", node.line, node.column)
            # A prior real declaration's type stands; deriving into it
            # does not redefine it (CALCULATED/DERIVED != re-declaring).
        else:
            self.symbols[target] = expr_type
            self.kinds[target] = "derived"

    def _require_declared(self, name: str, node: ast.Node) -> str:
        if name not in self.symbols:
            raise UndeclaredIdentifierError(f"{name!r} is not declared", node.line, node.column)
        return self.symbols[name]

    # -- expressions --

    def _infer(self, expr: ast.Expr) -> str:
        if isinstance(expr, ast.NumberLit):
            return "Scalar"
        if isinstance(expr, ast.StringLit):
            # No String/Label type in the brief's 24-type list; typed
            # permissively as Scalar (documented gap, not silent).
            return "Scalar"
        if isinstance(expr, ast.Identifier):
            return self._require_declared(expr.name, expr)
        if isinstance(expr, ast.UnaryOp):
            return self._infer(expr.operand)
        if isinstance(expr, ast.BinaryOp):
            return self._infer_binary(expr)
        if isinstance(expr, ast.Call):
            return self._infer_call(expr)
        raise TypeError(f"unhandled expression node: {type(expr).__name__}")  # pragma: no cover

    def _infer_binary(self, expr: ast.BinaryOp) -> str:
        left_t = self._infer(expr.left)
        right_t = self._infer(expr.right)
        if left_t == UNRESOLVED or right_t == UNRESOLVED:
            return UNRESOLVED
        if expr.op in ("+", "-"):
            if not comparable(left_t, right_t):
                raise TypeMismatchError(
                    f"incompatible operand types for {expr.op!r}: {left_t} and {right_t}",
                    expr.line, expr.column)
            return widen(left_t, right_t)
        if expr.op in ("*", "/"):
            if left_t == "Scalar":
                return right_t
            if right_t == "Scalar":
                return left_t
            if not comparable(left_t, right_t):
                raise TypeMismatchError(
                    f"incompatible operand types for {expr.op!r}: {left_t} and {right_t}",
                    expr.line, expr.column)
            return widen(left_t, right_t)
        if expr.op in ("=", "==", "!="):
            if not comparable(left_t, right_t):
                raise TypeMismatchError(
                    f"incompatible operand types for {expr.op!r}: {left_t} and {right_t}",
                    expr.line, expr.column)
            return "Scalar"
        raise TypeError(f"unhandled binary operator: {expr.op!r}")  # pragma: no cover

    def _infer_call(self, expr: ast.Call) -> str:
        arg_types = [self._infer(a) for a in expr.args]
        sig = self.transformations.get(expr.callee)
        if sig is None:
            self.unresolved_calls.append(UnresolvedCall(expr.callee, expr.line, expr.column))
            return UNRESOLVED
        if len(arg_types) != len(sig.param_types):
            raise ArgumentError(
                f"{expr.callee!r} expects {len(sig.param_types)} argument(s), got {len(arg_types)}",
                expr.line, expr.column)
        for i, (arg_t, param_t) in enumerate(zip(arg_types, sig.param_types)):
            if arg_t == UNRESOLVED:
                continue
            if not is_subtype(arg_t, param_t):
                raise TypeMismatchError(
                    f"argument {i + 1} to {expr.callee!r}: expected {param_t} (or a "
                    f"specialization), got {arg_t}", expr.line, expr.column)
        return sig.return_type

    def _require_scalar_or_unresolved(self, expr: ast.Expr, context: str) -> None:
        t = self._infer(expr)
        if t not in ("Scalar", UNRESOLVED):
            raise TypeMismatchError(f"{context} expects a boolean-valued (Scalar) expression, "
                                     f"got {t}", expr.line, expr.column)

    # -- statements --

    def _check_statement(self, stmt: ast.Statement) -> None:
        if isinstance(stmt, ast.ModuleDecl):
            self.module_name = stmt.name
            return
        if isinstance(stmt, ast.VariableDecl):
            type_name = self._require_known_type(stmt.type)
            self._declare(stmt.name, type_name, "variable", stmt)
            return
        if isinstance(stmt, ast.PrimitiveDecl):
            type_name = self._require_known_type(stmt.type)
            self._declare(stmt.name, type_name, "primitive", stmt)
            return
        if isinstance(stmt, ast.ConstantDecl):
            type_name = self._require_known_type(stmt.type)
            value_t = self._infer(stmt.value)
            if value_t != UNRESOLVED and not comparable(value_t, type_name):
                raise TypeMismatchError(
                    f"constant {stmt.name!r} declared {type_name} but initializer has type "
                    f"{value_t}", stmt.line, stmt.column)
            self._declare(stmt.name, type_name, "constant", stmt)
            return
        if isinstance(stmt, ast.OperatorDecl):
            for p in stmt.params:
                self._require_known_type(p.type)
            return_t = self._require_known_type(stmt.return_type)
            if stmt.name in self.transformations:
                raise RedeclarationError(f"operator {stmt.name!r} is already declared",
                                          stmt.line, stmt.column)
            self.transformations[stmt.name] = TransformationSignature(
                stmt.name, [p.type.name for p in stmt.params], return_t)
            return
        if isinstance(stmt, ast.EquationDecl):
            self._infer(stmt.expr)
            self._declare(stmt.name, "Equation", "equation", stmt)
            return
        if isinstance(stmt, ast.DefinitionDecl):
            value_t = self._infer(stmt.expr)
            self._declare(stmt.name, value_t, "definition", stmt)
            return
        if isinstance(stmt, ast.AssumptionDecl):
            self._require_scalar_or_unresolved(stmt.expr, "an assumption")
            self._declare(stmt.name, "Scalar", "assumption", stmt)
            return
        if isinstance(stmt, ast.DependencyDecl):
            # Structural recording only -- real DAG construction and
            # cycle detection is Phase 4's job (compiler/dependencies/
            # graph.py). Names may be forward references (this
            # statement declares that an edge WILL exist), so unknown
            # names are registered as Unresolved rather than erroring.
            for name in [stmt.name, *stmt.depends_on]:
                if name not in self.symbols:
                    self.symbols[name] = UNRESOLVED
                    self.kinds[name] = "dependency-forward-ref"
            for dep in stmt.depends_on:
                self.dependency_edges.append((stmt.name, dep))
            return
        if isinstance(stmt, ast.DeriveStmt):
            expr_t = self._infer(stmt.expr)
            if stmt.target is not None:
                self._bind_derive_target(stmt.target, expr_t, stmt)
            return
        if isinstance(stmt, ast.CalculateStmt):
            expr_t = self._infer(stmt.expr)
            if stmt.target is not None:
                self._bind_derive_target(stmt.target, expr_t, stmt)
            return
        if isinstance(stmt, ast.VerifyStmt):
            self._require_scalar_or_unresolved(stmt.expr, "verify")
            return
        if isinstance(stmt, ast.TheoremDecl):
            self._require_scalar_or_unresolved(stmt.expr, "a theorem")
            self._declare(stmt.name, "Theorem", "theorem", stmt)
            return
        if isinstance(stmt, ast.LemmaDecl):
            # No separate Lemma type in the brief's 24-type list; a
            # lemma is typed as Theorem by convention (documented, not
            # silent -- see module docstring).
            self._require_scalar_or_unresolved(stmt.expr, "a lemma")
            self._declare(stmt.name, "Theorem", "lemma", stmt)
            return
        if isinstance(stmt, ast.AuditStmt):
            self._require_declared(stmt.target, stmt)
            return
        if isinstance(stmt, ast.StatusStmt):
            # The status VALUE vocabulary (VERIFIED/DERIVED/... vs. the
            # brief's new DECLARED/RESOLVED/.../CERTIFIED states) is
            # reconciled in Phase 3, not here -- Phase 2 only checks
            # that the target being described actually exists.
            self._require_declared(stmt.target, stmt)
            return
        if isinstance(stmt, ast.ProvenanceStmt):
            self._require_declared(stmt.target, stmt)
            return
        if isinstance(stmt, ast.OutputStmt):
            self._require_declared(stmt.target, stmt)
            return
        if isinstance(stmt, ast.ReportStmt):
            return
        raise TypeError(f"unhandled statement node: {type(stmt).__name__}")  # pragma: no cover


def check_program(
    program: ast.Program,
    extra_transformations: dict[str, TransformationSignature] | None = None,
) -> CheckResult:
    """Type-check a parsed `.seit` Program. Raises a SemanticError
    subclass on the first hard error encountered; otherwise returns a
    CheckResult describing the final symbol table, the transformation
    registry (built-ins, any `extra_transformations` supplied by a
    caller such as seit_lang.primitives, plus any `operator`
    declarations), and any unresolved-transformation calls encountered."""
    return SemanticChecker(extra_transformations).check(program)
