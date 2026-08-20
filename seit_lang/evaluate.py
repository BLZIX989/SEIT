"""Evaluator for `.seit` (Phase 5, second half): executes a compiled
program's NAMED producing statements (derive/calculate/definition/
constant/equation/theorem/lemma/assumption targets -- the same set
seit_lang.dag.compile_dag already tracks as DAG nodes) in topological
order, using real values and the real primitive bindings from
seit_lang.primitives (or any PrimitiveBinding table a caller supplies).

Deliberately OUT OF SCOPE for this phase (left for Phase 13's CLI /
Phase 16's milestone, not rushed here): sequential execution of bare-
expression statements (`derive spectrum(L);` with no target -- these
bind no name, so they are not part of the value environment this
evaluator builds), `verify` statements actually driving SeitState
transitions (VERIFIED on success), `report` output formatting, and
`status`/`audit`/`output`/`provenance` statement side effects. Building
a full sequential program executor is a genuinely separate concern from
"can a produced value's expression be evaluated with real primitives
given real inputs," which is what this module answers.
"""
from __future__ import annotations

import operator

import numpy as np

from . import ast_nodes as ast
from .dag import SeitDAG, _producing_statements
from .primitives import PrimitiveBinding


class UnboundInputError(Exception):
    """A name was referenced but never supplied via `inputs=` and is not
    produced by any statement in the program -- mirrors
    seit_lang.dag's honest BLOCKED finding at the value-evaluation
    level: this evaluator does not fabricate a value for an unset
    input."""

    def __init__(self, name: str):
        super().__init__(f"{name!r} has no value -- not supplied via inputs= and not "
                          f"produced by any statement")
        self.name = name


class UnboundTransformationError(Exception):
    """A call references a transformation name with no PrimitiveBinding
    -- evaluation must not silently return a fabricated value for an
    unregistered/unbound transformation."""

    def __init__(self, callee: str):
        super().__init__(f"{callee!r} has no PrimitiveBinding -- cannot evaluate this call")
        self.callee = callee


def _multiply(a: object, b: object) -> object:
    """Python's `*` on two numpy ndarrays is ELEMENTWISE, but `.seit`'s
    "*" between two Matrix-family values (e.g. `B * transpose(B)` in the
    brief's own milestone example) means matrix multiplication -- using
    plain elementwise `*` here would silently compute the wrong physics
    for exactly the example this project cares about. Scalar involved on
    either side (a plain Python/numpy scalar, or a 0-d array) still uses
    ordinary multiplication/broadcasting, which is correct for scaling."""
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and a.ndim >= 1 and b.ndim >= 1:
        return a @ b
    return a * b


_BINARY_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": _multiply,
    "/": operator.truediv,
}


def _values_equal(a: object, b: object) -> bool:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return bool(np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float)))
    return bool(a == b)


def evaluate_expr(expr: ast.Expr, env: dict[str, object], bindings: dict[str, PrimitiveBinding]) -> object:
    if isinstance(expr, ast.NumberLit):
        return expr.value
    if isinstance(expr, ast.StringLit):
        return expr.value
    if isinstance(expr, ast.Identifier):
        if expr.name not in env:
            raise UnboundInputError(expr.name)
        return env[expr.name]
    if isinstance(expr, ast.UnaryOp):
        value = evaluate_expr(expr.operand, env, bindings)
        return -value
    if isinstance(expr, ast.BinaryOp):
        left = evaluate_expr(expr.left, env, bindings)
        right = evaluate_expr(expr.right, env, bindings)
        if expr.op in _BINARY_OPS:
            return _BINARY_OPS[expr.op](left, right)
        if expr.op in ("=", "=="):
            return _values_equal(left, right)
        if expr.op == "!=":
            return not _values_equal(left, right)
        raise TypeError(f"unhandled binary operator: {expr.op!r}")  # pragma: no cover
    if isinstance(expr, ast.Call):
        binding = bindings.get(expr.callee)
        if binding is None:
            raise UnboundTransformationError(expr.callee)
        args = [evaluate_expr(a, env, bindings) for a in expr.args]
        return binding.fn(*args)
    raise TypeError(f"unhandled expression node: {type(expr).__name__}")  # pragma: no cover


def evaluate_program(
    dag: SeitDAG,
    program: ast.Program,
    inputs: dict[str, object],
    bindings: dict[str, PrimitiveBinding],
) -> dict[str, object]:
    """Evaluate every producible node in `dag`'s topological order,
    seeding the environment with `inputs` (real values for `variable`/
    `primitive` declarations that nothing in the program itself
    computes). Returns the full environment (inputs plus every computed
    value). Raises UnboundInputError / UnboundTransformationError
    lazily, exactly when a missing value or transformation is actually
    needed -- a node nothing downstream depends on being unbound is not
    an error."""
    env: dict[str, object] = dict(inputs)
    target_to_expr = {target: expr for target, expr, _kind in _producing_statements(program)}
    for node in dag.topological_order():
        if node in env:
            continue
        expr = target_to_expr.get(node)
        if expr is None:
            continue  # a bare declaration with no producing statement and no supplied input
        env[node] = evaluate_expr(expr, env, bindings)
    return env
