"""Dependency-graph compilation for `.seit` (Phase 4): compiles a checked
Program into a real DAG, reusing compiler/dependencies/graph.py's
DependencyGraph for structure and cycle rejection, and seit_lang.state's
SeitStateMachine (Phase 3) for per-node status and dependency-validity
enforcement, rather than reimplementing either.

Edges carry the four pieces of metadata the brief asks for
(source/target/transformation/proof obligation), plus status and
provenance:

  - source/target: the dependency edge itself (target depends on source).
  - transformation: what produced the target from the source -- a call's
    callee name for `derive X = f(Y);`, `binary:<op>` for
    `derive X = Y + Z;`, or "dependency declaration" for an explicit
    `dependency X -> Y;` statement.
  - proof_obligation: the text of any `verify` statement(s) in the
    program whose expression references the target node. When none
    exist, this is recorded explicitly as "no `verify` statement found
    ... UNSTATED" -- never silently left blank, matching this project's
    standing rule that an absent check is a fact to report, not an
    implementation detail to omit.
  - status: the target node's SeitState after DAG compilation attempts
    to advance every `derive`/`calculate`/`definition`/`constant`
    target through RESOLVED -> CALCULATED via SeitStateMachine.
  - provenance: the string from a `provenance X = "...";` statement
    targeting that node, if any.

A DELIBERATE, DOCUMENTED CONSEQUENCE of reusing Phase 3's dependency
gate honestly: a `variable` declaration with no `derive`/`calculate`/
`definition` statement ever producing it (e.g. `variable B:
IncidenceMatrix;` on its own, with no assignment) never advances past
SeitState.DECLARED -- SeitState.DECLARED reconciles to Status.OPEN,
which is not in EXECUTABLE_UPSTREAM_STATUSES, so anything depending on
it is marked BLOCKED rather than CALCULATED. This is not a bug: a bare
`variable` declaration states that a value of that type will exist, not
that one has been supplied. Concretely, the brief's own Phase 16
milestone example (derive L = B * transpose(B);, with B only ever
`variable`-declared) compiles to a DAG where L is BLOCKED, not
CALCULATED, until something actually supplies B a value -- which is
exactly the physics-kernel data-ingestion work Phase 5 exists to do.
Phase 4 does not fabricate a placeholder value for an unset input to
make the milestone example look further along than it is.

UPDATE (Phase 16): compile_dag() gained an optional `supplied_inputs`
parameter for exactly the case above, once a caller genuinely intends
to supply B externally (e.g. seit_lang.cli's `--inputs` flag). Passing
the same input names used at evaluation time lets that node reach
CALCULATED here too, so the DAG's reported state matches what actually
gets computed -- this does not relax the dependency-validity rule
above (a supplied input's value still comes from outside the program
text, never from a producing statement); it only distinguishes "no
producing statement AND no value at all" (still honestly BLOCKED, the
default when supplied_inputs is omitted) from "no producing statement
but a real value is coming from the caller" (now correctly CALCULATED).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from compiler.dependencies.graph import CycleError, DependencyGraph

from . import ast_nodes as ast
from .semantic import CheckResult, check_program
from .state import DependencyNotReadyError, SeitState, SeitStateMachine

# Statement kinds that represent an actual computation of a named value
# (as opposed to a meta-level proposition ABOUT already-named values --
# equation/theorem/lemma/assumption state claims, they do not themselves
# get calculated).
_PRODUCED_KINDS = {"DeriveStmt", "CalculateStmt", "DefinitionDecl", "ConstantDecl"}


class DagCompileError(Exception):
    """Raised when compiling a .seit program's statements into a
    dependency graph is impossible -- currently only for cycles,
    surfaced from the real compiler.dependencies.graph.CycleError rather
    than a reimplementation of cycle detection."""


@dataclass(frozen=True)
class EdgeInfo:
    source: str
    target: str
    transformation: str
    proof_obligation: str
    status: SeitState
    provenance: str | None


@dataclass
class SeitDAG:
    graph: DependencyGraph
    edges: dict[tuple[str, str], EdgeInfo] = field(default_factory=dict)
    states: dict[str, SeitState] = field(default_factory=dict)
    blocked: dict[str, str] = field(default_factory=dict)  # node -> reason
    check_result: CheckResult | None = None

    def topological_order(self) -> list[str]:
        return self.graph.topological_order()


def _free_identifiers(expr: ast.Expr) -> set[str]:
    if isinstance(expr, ast.Identifier):
        return {expr.name}
    if isinstance(expr, (ast.NumberLit, ast.StringLit)):
        return set()
    if isinstance(expr, ast.UnaryOp):
        return _free_identifiers(expr.operand)
    if isinstance(expr, ast.BinaryOp):
        return _free_identifiers(expr.left) | _free_identifiers(expr.right)
    if isinstance(expr, ast.Call):
        out: set[str] = set()
        for a in expr.args:
            out |= _free_identifiers(a)
        return out
    raise TypeError(f"unhandled expression node: {type(expr).__name__}")  # pragma: no cover


def _transformation_label(expr: ast.Expr) -> str:
    if isinstance(expr, ast.Call):
        return expr.callee
    if isinstance(expr, ast.BinaryOp):
        return f"binary:{expr.op}"
    if isinstance(expr, ast.UnaryOp):
        return f"unary:{expr.op}"
    if isinstance(expr, ast.Identifier):
        return "identifier-reference"
    if isinstance(expr, (ast.NumberLit, ast.StringLit)):
        return "literal"
    raise TypeError(f"unhandled expression node: {type(expr).__name__}")  # pragma: no cover


def _expr_repr(expr: ast.Expr) -> str:
    if isinstance(expr, ast.Identifier):
        return expr.name
    if isinstance(expr, ast.NumberLit):
        return repr(expr.value)
    if isinstance(expr, ast.StringLit):
        return repr(expr.value)
    if isinstance(expr, ast.Call):
        return f"{expr.callee}({', '.join(_expr_repr(a) for a in expr.args)})"
    if isinstance(expr, ast.BinaryOp):
        return f"({_expr_repr(expr.left)} {expr.op} {_expr_repr(expr.right)})"
    if isinstance(expr, ast.UnaryOp):
        return f"-{_expr_repr(expr.operand)}"
    return "<expr>"  # pragma: no cover


def _collect_verify_obligations(program: ast.Program) -> dict[str, list[str]]:
    obligations: dict[str, list[str]] = {}
    for stmt in program.statements:
        if isinstance(stmt, ast.VerifyStmt):
            desc = _expr_repr(stmt.expr)
            for name in _free_identifiers(stmt.expr):
                obligations.setdefault(name, []).append(desc)
    return obligations


def _producing_statements(program: ast.Program) -> list[tuple[str, ast.Expr, str]]:
    producing: list[tuple[str, ast.Expr, str]] = []
    for stmt in program.statements:
        if isinstance(stmt, (ast.DeriveStmt, ast.CalculateStmt)) and stmt.target is not None:
            producing.append((stmt.target, stmt.expr, type(stmt).__name__))
        elif isinstance(stmt, ast.EquationDecl):
            producing.append((stmt.name, stmt.expr, "EquationDecl"))
        elif isinstance(stmt, ast.DefinitionDecl):
            producing.append((stmt.name, stmt.expr, "DefinitionDecl"))
        elif isinstance(stmt, ast.AssumptionDecl):
            producing.append((stmt.name, stmt.expr, "AssumptionDecl"))
        elif isinstance(stmt, ast.TheoremDecl):
            producing.append((stmt.name, stmt.expr, "TheoremDecl"))
        elif isinstance(stmt, ast.LemmaDecl):
            producing.append((stmt.name, stmt.expr, "LemmaDecl"))
        elif isinstance(stmt, ast.ConstantDecl):
            producing.append((stmt.name, stmt.value, "ConstantDecl"))
    return producing


def _collect_provenance(program: ast.Program) -> dict[str, str]:
    return {stmt.target: stmt.value for stmt in program.statements if isinstance(stmt, ast.ProvenanceStmt)}


def compile_dag(
    program: ast.Program,
    check_result: CheckResult | None = None,
    supplied_inputs: set[str] | dict | None = None,
) -> SeitDAG:
    """Compile a parsed `.seit` Program into a SeitDAG. Runs
    seit_lang.semantic.check_program first unless an already-computed
    CheckResult is supplied (so callers who already type-checked the
    program, e.g. a future CLI, don't pay for it twice). Raises
    DagCompileError if the program's dependency edges (explicit
    `dependency` statements plus the implicit edges from every
    `derive`/`calculate`/`definition`/`constant`/`equation`/`theorem`/
    `lemma`/`assumption` target to the free identifiers in its
    expression) contain a cycle.

    `supplied_inputs` (Phase 16): names of `variable`/`primitive`
    declarations that will be given a real value from OUTSIDE the
    program text at evaluation time (seit_lang.evaluate.evaluate_program's
    own `inputs=` dict, or just its key set). Without this, a node like
    the brief's own `variable B: IncidenceMatrix;` -- which has no
    producing statement in the source, by design -- stays honestly
    BLOCKED even when the caller fully intends to supply B externally,
    because static compilation has no way to know that on its own (this
    is exactly what seit_lang/tests/test_phase16_milestone.py's own
    development surfaced: `seit run spectral_test_complete.seit
    --inputs ...` genuinely computed L, yet the DAG's reported state for
    L stayed BLOCKED, because compile_dag ran before --inputs was even
    read). Passing the same input names used at evaluation time lets a
    supplied node reach SeitState.CALCULATED here too -- its value
    still comes from outside, not from a producing statement, so this
    is not a relaxation of Phase 4's original dependency-validity rule,
    only an acknowledgment that "no producing statement" and "no value
    at all" are not the same claim."""
    if check_result is None:
        check_result = check_program(program)
    supplied = set(supplied_inputs) if supplied_inputs else set()

    graph = DependencyGraph()
    machine = SeitStateMachine()
    provenance = _collect_provenance(program)
    obligations = _collect_verify_obligations(program)
    producing = _producing_statements(program)

    for name in check_result.symbols:
        graph.add_node(name)
        machine.declare(name)
    for name in supplied:
        if name in machine.states:
            machine.transition(name, SeitState.RESOLVED)
            machine.transition(name, SeitState.CALCULATED)

    edges: dict[tuple[str, str], EdgeInfo] = {}

    def _add_edge(target: str, source: str, transformation: str) -> None:
        if source == target:
            return
        try:
            graph.add_dependency(target, source)
        except CycleError as exc:
            raise DagCompileError(str(exc)) from exc
        machine.add_dependency(target, source)
        proof = "; ".join(obligations.get(target, [])) or \
            f"no `verify` statement found for {target!r} in the source program " \
            "-- proof obligation UNSTATED"
        edges[(source, target)] = EdgeInfo(
            source=source, target=target, transformation=transformation,
            proof_obligation=proof, status=SeitState.DECLARED, provenance=provenance.get(target))

    for target, expr, _kind in producing:
        transformation = _transformation_label(expr)
        for source in sorted(_free_identifiers(expr)):
            _add_edge(target, source, transformation)

    for target, source in check_result.dependency_edges:
        _add_edge(target, source, "dependency declaration")

    blocked: dict[str, str] = {}
    for target, _expr, kind in producing:
        if kind not in _PRODUCED_KINDS:
            continue
        if machine.state_of(target) != SeitState.DECLARED:
            continue  # already advanced by an earlier producing statement for the same name
        try:
            machine.transition(target, SeitState.RESOLVED)
            machine.transition(target, SeitState.CALCULATED)
        except DependencyNotReadyError as exc:
            blocked[target] = str(exc)
            machine.transition(target, SeitState.BLOCKED)

    final_edges = {
        key: EdgeInfo(info.source, info.target, info.transformation, info.proof_obligation,
                      machine.states.get(info.target, SeitState.DECLARED), info.provenance)
        for key, info in edges.items()
    }

    return SeitDAG(graph=graph, edges=final_edges, states=dict(machine.states),
                    blocked=blocked, check_result=check_result)
