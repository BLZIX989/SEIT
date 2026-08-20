"""seit CLI (Phase 13): parse/check/build/run/verify/audit/status/graph/
report subcommands, with --target default/FC005/NCG/geometry variants
selecting which primitive registry (transformations + bindings) is
active. No new language or execution logic lives here -- this module
is argument parsing and output formatting over Phases 1-12
(seit_lang.parser/semantic/dag/evaluate and every *_branch/*_kernel
primitive registry); every command computes and reports a provenance
dict (source file path, sha256 of its exact contents, the target used,
a UTC timestamp) rather than silently omitting where a result came
from.

TARGET PRESETS: "default" is the union of every primitive registry
built across Phases 5-12. "NCG" and "geometry" are real, populated
subsets (NCG: Phase 5's generic kernel + Phase 9's KO-dimension
primitives; geometry: Phase 5 + Phase 6's incidence/Clifford + Phase
7's persistence primitives). "FC005" is HONEST about a real, current
gap: this project's FC-005 DESI pipeline
(compiler/backends/desi_*.py) has never been exposed to `.seit` --
Phase 5 exposed the generic graph/Laplacian/spectral/heat-kernel
backends it shares with FC-005, not the DESI-specific pipeline itself
-- so `--target FC005` falls back to the generic Phase 5 registry and
the CLI's own output carries an explicit `target_note` saying so,
rather than silently mapping the name to something unrelated or
pretending the binding exists.

Every command's JSON output is produced by _json_safe(), a small
recursive serializer for the real Python objects Phases 1-12 produce
(numpy ndarrays -- real and complex, using a {"__complex_ndarray__":
true, "real": ..., "imag": ...} representation for the latter --
numpy scalar types, SeitState enum values, and the dataclasses
compiler.backends.graph_laplacian.Graph and
compiler.backends.spectral.SpectralData) -- not a generic `default=str`
fallback that would silently stringify a numeric result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import ast_nodes as ast
from .clifford_branch import CLIFFORD_BRANCH_BINDINGS, CLIFFORD_BRANCH_TRANSFORMATIONS
from .continuum_bridge import CONTINUUM_BRIDGE_BINDINGS, CONTINUUM_BRIDGE_TRANSFORMATIONS
from .dag import DagCompileError, SeitDAG, _expr_repr, compile_dag
from .evaluate import UnboundInputError, UnboundTransformationError, evaluate_expr, evaluate_program
from .gauge_branch import GAUGE_BRANCH_BINDINGS, GAUGE_BRANCH_TRANSFORMATIONS
from .incidence_clifford import INCIDENCE_CLIFFORD_BINDINGS, INCIDENCE_CLIFFORD_TRANSFORMATIONS
from .ncg_branch import NCG_BRANCH_BINDINGS, NCG_BRANCH_TRANSFORMATIONS
from .parser import parse as parse_seit
from .persistence_kernel import PERSISTENCE_KERNEL_BINDINGS, PERSISTENCE_KERNEL_TRANSFORMATIONS
from .primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from .semantic import CheckResult, SemanticError, check_program
from .spectral_action import SPECTRAL_ACTION_BINDINGS, SPECTRAL_ACTION_TRANSFORMATIONS
from .state import SeitState

_ALL_TRANSFORMATIONS = {
    **PHYSICS_KERNEL_TRANSFORMATIONS, **INCIDENCE_CLIFFORD_TRANSFORMATIONS,
    **PERSISTENCE_KERNEL_TRANSFORMATIONS, **CONTINUUM_BRIDGE_TRANSFORMATIONS,
    **NCG_BRANCH_TRANSFORMATIONS, **CLIFFORD_BRANCH_TRANSFORMATIONS,
    **GAUGE_BRANCH_TRANSFORMATIONS, **SPECTRAL_ACTION_TRANSFORMATIONS,
}
_ALL_BINDINGS = {
    **PHYSICS_KERNEL_BINDINGS, **INCIDENCE_CLIFFORD_BINDINGS,
    **PERSISTENCE_KERNEL_BINDINGS, **CONTINUUM_BRIDGE_BINDINGS,
    **NCG_BRANCH_BINDINGS, **CLIFFORD_BRANCH_BINDINGS,
    **GAUGE_BRANCH_BINDINGS, **SPECTRAL_ACTION_BINDINGS,
}

TARGET_PRESETS: dict[str, dict] = {
    "default": {"transformations": _ALL_TRANSFORMATIONS, "bindings": _ALL_BINDINGS, "note": None},
    "NCG": {
        "transformations": {**PHYSICS_KERNEL_TRANSFORMATIONS, **NCG_BRANCH_TRANSFORMATIONS},
        "bindings": {**PHYSICS_KERNEL_BINDINGS, **NCG_BRANCH_BINDINGS},
        "note": None,
    },
    "geometry": {
        "transformations": {**PHYSICS_KERNEL_TRANSFORMATIONS, **INCIDENCE_CLIFFORD_TRANSFORMATIONS,
                             **PERSISTENCE_KERNEL_TRANSFORMATIONS},
        "bindings": {**PHYSICS_KERNEL_BINDINGS, **INCIDENCE_CLIFFORD_BINDINGS,
                     **PERSISTENCE_KERNEL_BINDINGS},
        "note": None,
    },
    "FC005": {
        "transformations": dict(PHYSICS_KERNEL_TRANSFORMATIONS),
        "bindings": dict(PHYSICS_KERNEL_BINDINGS),
        "note": ("FC-005 DESI-specific primitives (compiler/backends/desi_*.py) are not yet "
                 "exposed to .seit -- only the generic graph/Laplacian/spectral/heat-kernel "
                 "primitives from Phase 5 are available under this target."),
    },
}


def _json_safe(value):
    if isinstance(value, SeitState):
        return value.value
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {"__complex_ndarray__": True, "shape": list(value.shape),
                     "real": value.real.tolist(), "imag": value.imag.tolist()}
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _json_safe(getattr(value, f.name)) for f in fields(value)}
    return value


def _load_inputs(path: str | None) -> dict:
    """Phase 16: loads declared external input VALUES from a JSON file
    (a flat {name: value} mapping; a JSON array becomes a numpy array,
    e.g. for a Matrix/IncidenceMatrix-typed `variable`). This is what
    makes `seit run` able to actually execute a program like the
    brief's own milestone example, whose `variable B: IncidenceMatrix;`
    is never assigned by any derive/calculate statement (see
    seit_lang.dag's Phase 4 module docstring) -- real input data has to
    come from somewhere outside the program text itself."""
    if path is None:
        return {}
    raw = json.loads(Path(path).read_text())
    return {k: (np.array(v) if isinstance(v, list) else v) for k, v in raw.items()}


def _provenance(path: Path, target: str) -> dict:
    text = path.read_text()
    return {
        "source_file": str(path),
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "target": target,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


class _StageFailure(Exception):
    def __init__(self, payload: dict):
        self.payload = payload


def _stage_parse(path: Path, prov: dict) -> ast.Program:
    try:
        return parse_seit(path.read_text())
    except SyntaxError as exc:
        raise _StageFailure({"ok": False, "stage": "parse", "error": str(exc), "provenance": prov})


def _stage_check(program: ast.Program, preset: dict, prov: dict) -> CheckResult:
    try:
        return check_program(program, extra_transformations=preset["transformations"])
    except SemanticError as exc:
        raise _StageFailure({"ok": False, "stage": "check", "error": str(exc), "provenance": prov})


def _stage_build(program: ast.Program, check_result: CheckResult, prov: dict,
                  supplied_inputs: dict | None = None) -> SeitDAG:
    try:
        return compile_dag(program, check_result, supplied_inputs)
    except DagCompileError as exc:
        raise _StageFailure({"ok": False, "stage": "build", "error": str(exc), "provenance": prov})


def _stage_run(dag: SeitDAG, program: ast.Program, preset: dict, prov: dict, inputs: dict | None = None) -> dict:
    try:
        return evaluate_program(dag, program, inputs=inputs or {}, bindings=preset["bindings"])
    except (UnboundInputError, UnboundTransformationError) as exc:
        raise _StageFailure({"ok": False, "stage": "run", "error": str(exc),
                              "error_type": type(exc).__name__, "provenance": prov})
    except Exception as exc:  # a bound primitive itself raised (e.g. an invalid parameter)
        raise _StageFailure({"ok": False, "stage": "run", "error": str(exc),
                              "error_type": type(exc).__name__, "provenance": prov})


def _run_verify_statements(program: ast.Program, env: dict, preset: dict) -> list[dict]:
    results = []
    for stmt in program.statements:
        if not isinstance(stmt, ast.VerifyStmt):
            continue
        entry = {"expr": _expr_repr(stmt.expr), "line": stmt.line}
        try:
            value = evaluate_expr(stmt.expr, env, preset["bindings"])
            entry["passed"] = bool(value)
        except Exception as exc:
            entry["passed"] = None
            entry["error"] = str(exc)
        results.append(entry)
    return results


def _target_preset(name: str) -> dict:
    if name not in TARGET_PRESETS:
        raise KeyError(f"unknown target {name!r}, expected one of {sorted(TARGET_PRESETS)}")
    return TARGET_PRESETS[name]


# --- subcommands -------------------------------------------------------

def cmd_parse(file: str, target: str = "default") -> dict:
    path = Path(file)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
    except _StageFailure as fail:
        return fail.payload
    return {"ok": True, "module_name": next(
        (s.name for s in program.statements if isinstance(s, ast.ModuleDecl)), None),
        "n_statements": len(program.statements), "provenance": prov}


def cmd_check(file: str, target: str = "default") -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
    except _StageFailure as fail:
        return fail.payload
    return {
        "ok": True,
        "module_name": result.module_name,
        "symbols": result.symbols,
        "unresolved_calls": [{"callee": c.callee, "line": c.line} for c in result.unresolved_calls],
        "target_note": preset["note"],
        "provenance": prov,
    }


def cmd_build(file: str, target: str = "default") -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov)
    except _StageFailure as fail:
        return fail.payload
    return {
        "ok": True,
        "topological_order": dag.topological_order(),
        "states": {k: v.value for k, v in dag.states.items()},
        "blocked": dag.blocked,
        "edges": [
            {"source": e.source, "target": e.target, "transformation": e.transformation,
             "proof_obligation": e.proof_obligation, "status": e.status.value, "provenance": e.provenance}
            for e in dag.edges.values()
        ],
        "provenance": prov,
    }


def cmd_run(file: str, target: str = "default", inputs_path: str | None = None) -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    inputs = _load_inputs(inputs_path)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov, inputs)
        env = _stage_run(dag, program, preset, prov, inputs)
    except _StageFailure as fail:
        return fail.payload
    return {"ok": True, "environment": _json_safe(env),
            "states": {k: v.value for k, v in dag.states.items()},
            "declared_inputs": sorted(inputs), "provenance": prov}


def cmd_verify(file: str, target: str = "default", inputs_path: str | None = None) -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    inputs = _load_inputs(inputs_path)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov, inputs)
        env = _stage_run(dag, program, preset, prov, inputs)
    except _StageFailure as fail:
        return fail.payload
    verify_results = _run_verify_statements(program, env, preset)
    all_ok = all(r["passed"] is True for r in verify_results)
    return {"ok": all_ok, "verify_results": verify_results, "provenance": prov}


def cmd_audit(file: str, target: str = "default") -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov)
    except _StageFailure as fail:
        return fail.payload
    audits = []
    for stmt in program.statements:
        if isinstance(stmt, ast.AuditStmt):
            state = dag.states.get(stmt.target)
            obligations = [e.proof_obligation for e in dag.edges.values() if e.target == stmt.target]
            audits.append({"target": stmt.target,
                            "state": state.value if state is not None else None,
                            "proof_obligations": obligations})
    return {"ok": True, "audits": audits, "provenance": prov}


def cmd_status(file: str, target: str = "default") -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov)
    except _StageFailure as fail:
        return fail.payload
    status_stmts = {s.target: s.value for s in program.statements if isinstance(s, ast.StatusStmt)}
    return {
        "ok": True,
        "dag_states": {k: v.value for k, v in dag.states.items()},
        "declared_status_statements": status_stmts,
        "provenance": prov,
    }


def cmd_graph(file: str, target: str = "default") -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov)
    except _StageFailure as fail:
        return fail.payload
    return {
        "ok": True,
        "topological_order": dag.topological_order(),
        "edges": [{"source": s, "target": t} for (s, t) in dag.edges],
        "provenance": prov,
    }


def cmd_report(file: str, target: str = "default", inputs_path: str | None = None) -> dict:
    path = Path(file)
    preset = _target_preset(target)
    prov = _provenance(path, target)
    inputs = _load_inputs(inputs_path)
    try:
        program = _stage_parse(path, prov)
        result = _stage_check(program, preset, prov)
        dag = _stage_build(program, result, prov, inputs)
    except _StageFailure as fail:
        return fail.payload
    try:
        env = _stage_run(dag, program, preset, prov, inputs)
        verify_results = _run_verify_statements(program, env, preset)
        run_ok = True
    except _StageFailure as fail:
        env, verify_results, run_ok = {}, [], False
        run_error = fail.payload
    else:
        run_error = None
    return {
        "ok": run_ok and all(r["passed"] is True for r in verify_results),
        "module_name": result.module_name,
        "n_symbols": len(result.symbols),
        "states": {k: v.value for k, v in dag.states.items()},
        "blocked": dag.blocked,
        "verify_results": verify_results,
        "run_error": run_error,
        "target_note": preset["note"],
        "provenance": prov,
    }


def cmd_manifest(file: str, target: str = "default", output_dir: str = ".",
                  inputs_path: str | None = None) -> dict:
    """Phase 14: writes the combined reproducibility manifest (execution
    manifest, dependency DAG, equation/variable/operator/status
    registries, provenance, numerical outputs, audit results) to
    `output_dir`. Implemented in seit_lang.manifest, kept out of this
    module to avoid a circular import (manifest.py itself reuses this
    module's stage helpers)."""
    from .manifest import write_manifest
    inputs = _load_inputs(inputs_path)
    path = write_manifest(file, output_dir, target, inputs)
    return {"ok": True, "manifest_path": str(path)}


_COMMANDS = {
    "parse": cmd_parse, "check": cmd_check, "build": cmd_build, "run": cmd_run,
    "verify": cmd_verify, "audit": cmd_audit, "status": cmd_status, "graph": cmd_graph,
    "report": cmd_report, "manifest": cmd_manifest,
}

# subcommands that actually execute the program (as opposed to just
# parsing/checking/building its static structure) and therefore accept
# --inputs for declared external values (Phase 16).
_EXECUTING_COMMANDS = {"run", "verify", "report", "manifest"}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="seit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in _COMMANDS:
        sub = subparsers.add_parser(name)
        sub.add_argument("file")
        sub.add_argument("--target", choices=sorted(TARGET_PRESETS), default="default")
        if name in _EXECUTING_COMMANDS:
            sub.add_argument("--inputs", dest="inputs_path", default=None,
                              help="JSON file of declared external input values")
        if name == "manifest":
            sub.add_argument("--output-dir", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    handler = _COMMANDS[args.command]
    kwargs = {}
    if args.command in _EXECUTING_COMMANDS:
        kwargs["inputs_path"] = args.inputs_path
    if args.command == "manifest":
        kwargs["output_dir"] = args.output_dir
    result = handler(args.file, args.target, **kwargs)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
