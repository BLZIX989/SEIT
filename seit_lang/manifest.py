"""Reproducibility manifests for `.seit` execution (Phase 14): given a
source file plus a declared-inputs dict, produces ONE combined,
machine-readable manifest bundling everything the brief asks for --
execution manifest, dependency DAG, equation/variable/operator/status
registries, provenance record, numerical outputs, and audit results --
reproducible from the source file's own sha256 and the declared inputs,
with no hidden state.

This module adds no new language/execution semantics; it assembles
Phase 13's own CLI stage helpers (parse/check/build/run/verify/audit)
plus one genuinely new piece Phase 13 did not need: an OPERATOR
REGISTRY that cross-references every Call actually made in the program
against the active target preset's transformation registry, including
each PrimitiveBinding's own `source` string (Phases 5-12's dotted path
back to the real compiler/backends/... or
scientific_corpus/derivation/... function that computed it) -- so the
manifest records not just WHAT was computed but WHICH real
implementation computed it.

REPRODUCIBILITY: build_manifest() is a pure function of (source file
contents, target, declared inputs) except for its own timestamp field
-- two calls with the same file and inputs produce byte-identical
output once that one field is excluded (verified by
seit_lang/tests/test_manifest.py, not merely asserted).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ast_nodes as ast
from . import cli
from .evaluate import evaluate_program


def _collect_call_names(expr: ast.Expr) -> set[str]:
    if isinstance(expr, ast.Call):
        names = {expr.callee}
        for a in expr.args:
            names |= _collect_call_names(a)
        return names
    if isinstance(expr, ast.UnaryOp):
        return _collect_call_names(expr.operand)
    if isinstance(expr, ast.BinaryOp):
        return _collect_call_names(expr.left) | _collect_call_names(expr.right)
    return set()


def _all_call_names(program: ast.Program) -> set[str]:
    names: set[str] = set()
    for stmt in program.statements:
        expr = getattr(stmt, "expr", None) or getattr(stmt, "value", None)
        if expr is not None:
            names |= _collect_call_names(expr)
    return names


_VALUE_HOLDING_KINDS = {"variable", "primitive", "constant", "derived", "definition"}


def build_manifest(file: str, target: str = "default", inputs: dict | None = None) -> dict:
    path = Path(file)
    preset = cli._target_preset(target)
    prov = cli._provenance(path, target)
    inputs = inputs or {}

    try:
        program = cli._stage_parse(path, prov)
        check_result = cli._stage_check(program, preset, prov)
        dag = cli._stage_build(program, check_result, prov)
    except cli._StageFailure as fail:
        return {
            "execution_manifest": {
                "source_file": str(path), "target": target, "target_note": preset["note"],
                "declared_inputs": sorted(inputs), "run_succeeded": False,
                "run_error": fail.payload,
            },
            "dependency_dag": None, "equation_registry": {}, "variable_registry": {},
            "operator_registry": {}, "status_registry": {}, "provenance": prov,
            "numerical_outputs": {}, "audit_results": [], "verify_results": [],
        }

    run_error = None
    env: dict = {}
    try:
        env = evaluate_program(dag, program, inputs=inputs, bindings=preset["bindings"])
    except Exception as exc:  # UnboundInputError/UnboundTransformationError, or a bound primitive's own error
        run_error = {"error": str(exc), "error_type": type(exc).__name__}

    verify_results = cli._run_verify_statements(program, env, preset) if run_error is None else []

    audits = []
    for stmt in program.statements:
        if isinstance(stmt, ast.AuditStmt):
            state = dag.states.get(stmt.target)
            obligations = [e.proof_obligation for e in dag.edges.values() if e.target == stmt.target]
            audits.append({"target": stmt.target,
                            "state": state.value if state is not None else None,
                            "proof_obligations": obligations})

    equation_registry = {name: {"type": t} for name, t in check_result.symbols.items()
                          if check_result.kinds.get(name) == "equation"}
    variable_registry = {name: {"type": t, "kind": check_result.kinds.get(name)}
                          for name, t in check_result.symbols.items()
                          if check_result.kinds.get(name) in _VALUE_HOLDING_KINDS}
    called_names = _all_call_names(program)
    operator_registry = {
        name: {"param_types": sig.param_types, "return_type": sig.return_type,
               "source": preset["bindings"][name].source if name in preset["bindings"] else None}
        for name, sig in preset["transformations"].items() if name in called_names
    }
    status_stmts = {s.target: s.value for s in program.statements if isinstance(s, ast.StatusStmt)}
    status_registry = {
        name: {"dag_state": state.value, "declared_status_statement": status_stmts.get(name)}
        for name, state in dag.states.items()
    }

    return {
        "execution_manifest": {
            "source_file": str(path),
            "module_name": check_result.module_name,
            "target": target,
            "target_note": preset["note"],
            "n_statements": len(program.statements),
            "declared_inputs": sorted(inputs),
            "run_succeeded": run_error is None,
            "run_error": run_error,
        },
        "dependency_dag": {
            "topological_order": dag.topological_order(),
            "edges": [
                {"source": e.source, "target": e.target, "transformation": e.transformation,
                 "proof_obligation": e.proof_obligation, "status": e.status.value, "provenance": e.provenance}
                for e in dag.edges.values()
            ],
        },
        "equation_registry": equation_registry,
        "variable_registry": variable_registry,
        "operator_registry": operator_registry,
        "status_registry": status_registry,
        "provenance": prov,
        "numerical_outputs": cli._json_safe(env),
        "audit_results": audits,
        "verify_results": verify_results,
    }


def write_manifest(file: str, output_dir: str, target: str = "default", inputs: dict | None = None) -> Path:
    manifest = build_manifest(file, target, inputs)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{Path(file).stem}.manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2))
    return out_path
