"""Master orchestrator (spec section 37/41). Builds the MDCL, runs the two
executable tests, registers historical branches, runs the self-audit, and
writes every required artifact at the repository root.

Usage: python3 -m compiler.run_compiler
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compiler.backends.graph_laplacian import build_graph, laplacian
from compiler.backends.spectral import spectrum
from compiler.core.status import Status, TerminalStatus
from compiler.falsification.protocols import (
    FalsificationRecord, representation_invariance_test,
)
from compiler.historical.register import register_historical_nodes
from compiler.ir.executable_tests import register_executable_tests
from compiler.ir.forward_chain import register_template_chain
from compiler.ir.registry import MDCLRegistries
from compiler.verification.self_audit import run_self_audit

ROOT = Path(__file__).resolve().parents[1]
# Registries/artifacts are generated at the repository root (spec section 37
# lists master_mdcl.json, object_registry.json, etc. as top-level deliverables).
OUT_DIR = ROOT

TYPE_DEFS = [
    ("formal_foundation", "F0 = (Logic, in, Axioms)", None),
    ("forward_chain_template", "spec-section-6 dependency template node", None),
    ("mathematical_object", "a directly postulated candidate structure", None),
    ("graph_laplacian_operator", "L = D - A over a graph", "mathematical_object"),
    ("spectral_data", "eigenvalues/eigenvectors of an operator", "mathematical_object"),
    ("heat_semigroup", "R(t) = e^{-tL}", "mathematical_object"),
    ("projector", "a linear projector, e.g. onto ker(L)", "mathematical_object"),
    ("diffusion_distance", "d_t(i,j) built from Spec(L)", "mathematical_object"),
    ("geometry_candidate", "a candidate metric/geometry, status never above CONDITIONAL "
                           "without an analytic proof", "mathematical_object"),
    ("historical_claim", "a prose claim from a pre-compiler source document", None),
    ("reproduction_attempt", "an attempt to re-execute a historical claim in this compiler", None),
    ("forward_derivation_attempt", "an attempt at a target-independent forward derivation", None),
    ("external_literature_reference", "a third-party published result, comparison-only", None),
    ("missing_artifact", "a named artifact the build command required but that was not "
                         "found in the repository", None),
    ("self_acknowledged_obstruction", "a project-internal statement of a derivation "
                                       "obstruction, predating this compiler", None),
]


def _representation_invariance_falsification_test() -> FalsificationRecord:
    """A concrete instance of spec section 25's Representation Invariance
    Test: the eigenvalue spectrum of L must not depend on how the graph's
    vertices happen to be labeled."""
    g = build_graph("cycle", 10)
    base_edges = g.edges
    rng = np.random.default_rng(7)
    perms = [rng.permutation(g.n) for _ in range(4)]

    def spectrum_under_permutation(perm):
        remap = {old: int(new) for old, new in zip(range(g.n), perm)}
        relabeled_edges = [(remap[i], remap[j]) for i, j in base_edges]
        A = np.zeros((g.n, g.n))
        for i, j in relabeled_edges:
            A[i, j] = A[j, i] = 1.0
        L = laplacian(A)
        return tuple(np.round(np.sort(spectrum(L).eigenvalues), 8))

    reps = [np.arange(g.n)] + perms
    rec = representation_invariance_test(
        record_id="FALS-SPECTRUM-RELABELING-INVARIANCE",
        target="Spec(L) for cycle(n=10) under vertex relabeling",
        representations=reps,
        invariant_fn=spectrum_under_permutation,
    )
    return rec


def build_and_run() -> dict:
    registries = MDCLRegistries()
    for name, desc, parent in TYPE_DEFS:
        registries.types.add_type(name, desc, parent)

    register_template_chain(registries)
    test_results = register_executable_tests(registries)
    register_historical_nodes(registries)

    falsifications: list[FalsificationRecord] = list(test_results["falsifications"])
    falsifications.append(_representation_invariance_falsification_test())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registries.dump_all(OUT_DIR)

    proof_registry = []
    for t in registries.transformations:
        if t.proof:
            proof_registry.append({
                "id": f"PROOF-{t.id}", "transformation_id": t.id,
                "statement": t.action, "method": t.proof, "status": t.status.value,
            })
    (OUT_DIR / "proof_registry.json").write_text(json.dumps(proof_registry, indent=2))

    (OUT_DIR / "calculation_registry.json").write_text(
        json.dumps(test_results["calculations"], indent=2)
    )

    falsification_registry = [f.to_dict() for f in falsifications]
    (OUT_DIR / "falsification_registry.json").write_text(json.dumps(falsification_registry, indent=2))

    provenance_registry = {
        n.id: n.provenance.to_dict() for n in registries.all_nodes() if n.provenance is not None
    }
    (OUT_DIR / "provenance_registry.json").write_text(json.dumps(provenance_registry, indent=2))

    from compiler.falsification.target_independence import scan_registries
    ti_findings = [f.to_dict() for f in scan_registries(registries)]
    (OUT_DIR / "target_independence.json").write_text(json.dumps({
        "findings": ti_findings,
        "n_flagged": sum(1 for f in ti_findings if not f["allowed"]),
    }, indent=2))

    master_mdcl = {
        "types": registries.types.to_list(),
        "objects": registries.objects.to_list(),
        "transformations": registries.transformations.to_list(),
        "equations": registries.equations.to_list(),
        "status_matrix": registries.status_matrix(),
    }
    (OUT_DIR / "master_mdcl.json").write_text(json.dumps(master_mdcl, indent=2))

    required_paths = [OUT_DIR / name for name in (
        "type_registry.json", "object_registry.json", "transformation_registry.json",
        "equation_registry.json", "status_matrix.json", "proof_registry.json",
        "calculation_registry.json", "falsification_registry.json",
        "provenance_registry.json", "target_independence.json", "master_mdcl.json",
    )]
    audit_results = run_self_audit(registries, required_paths=required_paths)
    (OUT_DIR / "self_audit_report.json").write_text(
        json.dumps([a.to_dict() for a in audit_results], indent=2)
    )

    all_audits_passed = all(a.passed for a in audit_results)
    all_test1_passed = all(r.passed for r in test_results["test1_results"])
    any_open_upstream = any(
        n.status in (Status.OPEN,) for n in registries.objects
        if n.type == "forward_chain_template"
    ) or any(t.status == Status.OPEN for t in registries.transformations if t.id == "SELECTION-SIGMA")

    if not all_audits_passed:
        terminal = TerminalStatus.PARTIALLY_CLOSED
    elif any_open_upstream:
        terminal = TerminalStatus.CONDITIONALLY_CLOSED
    else:
        terminal = TerminalStatus.PARTIALLY_CLOSED

    return {
        "registries": registries,
        "test_results": test_results,
        "falsifications": falsifications,
        "audit_results": audit_results,
        "all_audits_passed": all_audits_passed,
        "all_test1_passed": all_test1_passed,
        "terminal_status": terminal,
    }


if __name__ == "__main__":
    result = build_and_run()
    print(f"terminal status: {result['terminal_status'].value}")
    print(f"audits passed: {result['all_audits_passed']}")
    for a in result["audit_results"]:
        mark = "PASS" if a.passed else "FAIL"
        print(f"  [{mark}] {a.name} ({len(a.issues)} issues)")
        for issue in a.issues[:10]:
            print(f"      - {issue}")

    from compiler.workbook.build_workbook import build_workbook
    build_workbook(result, ROOT / "Master Calculation Workbook.xlsx")
    print("wrote Master Calculation Workbook.xlsx")
