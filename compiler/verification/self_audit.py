"""Self-audit (spec section 36). Every failed audit becomes a registered
issue; none of these audits are permitted to force a pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from compiler.core.status import Status
from compiler.dependencies.graph import CycleError, DependencyGraph
from compiler.falsification.target_independence import scan_registries
from compiler.ir.registry import MDCLRegistries


@dataclass
class AuditResult:
    name: str
    passed: bool
    issues: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "issues": self.issues, "details": self.details}


def build_dependency_graph(registries: MDCLRegistries) -> DependencyGraph:
    g = DependencyGraph()
    all_ids = set(registries.objects.ids()) | set(registries.transformations.ids()) | set(registries.equations.ids())
    for node in registries.all_nodes():
        g.add_node(node.id)
        for dep in node.dependencies:
            if dep not in all_ids:
                g.add_node(dep)  # register as a dangling stub; flagged by dependency_audit
            g.add_dependency(node.id, dep)
    return g


def dependency_audit(registries: MDCLRegistries, graph: DependencyGraph) -> AuditResult:
    issues = []
    all_ids = set(registries.objects.ids()) | set(registries.transformations.ids()) | set(registries.equations.ids())
    try:
        order = graph.topological_order()
    except CycleError as e:
        return AuditResult("dependency_audit", False, [f"cycle detected: {e}"])
    for node in registries.all_nodes():
        for dep in node.dependencies:
            if dep not in all_ids:
                issues.append(f"{node.id}: dependency '{dep}' is not a registered node (dangling reference)")
    return AuditResult("dependency_audit", len(issues) == 0, issues,
                        {"n_nodes": len(order), "topological_order_len": len(order)})


def circularity_audit() -> AuditResult:
    """Audits the cycle-rejection mechanism itself by attempting to build
    a known 3-cycle on a scratch graph and confirming it is rejected."""
    scratch = DependencyGraph()
    scratch.add_dependency("X", "Y")
    scratch.add_dependency("Y", "Z")
    try:
        scratch.add_dependency("Z", "X")
    except CycleError:
        return AuditResult("circularity_audit", True, [],
                            {"note": "3-cycle X->Y->Z->X correctly rejected"})
    return AuditResult("circularity_audit", False,
                        ["dependency engine FAILED to reject a known 3-cycle"])


def type_audit(registries: MDCLRegistries) -> AuditResult:
    issues = []
    known_types = set(registries.types.ids())
    for obj in registries.objects:
        if obj.type not in known_types:
            issues.append(f"{obj.id}: type '{obj.type}' not present in type_registry")
    return AuditResult("type_audit", len(issues) == 0, issues, {"n_types": len(known_types)})


def provenance_audit(registries: MDCLRegistries) -> AuditResult:
    issues = []
    for node in registries.all_nodes():
        if node.provenance is None:
            issues.append(f"{node.id}: missing provenance record")
            continue
        p = node.provenance
        if not p.source:
            issues.append(f"{node.id}: provenance.source is empty")
        if not p.execution_timestamp:
            issues.append(f"{node.id}: provenance.execution_timestamp is empty")
        if not p.git_commit:
            issues.append(f"{node.id}: provenance.git_commit is empty")
    return AuditResult("provenance_audit", len(issues) == 0, issues)


def target_independence_audit(registries: MDCLRegistries) -> AuditResult:
    findings = scan_registries(registries)
    bad = [f for f in findings if not f.allowed]
    issues = [f"{f.node_id}: forbidden term '{f.term}' appears with role '{f.role}'" for f in bad]
    return AuditResult("target_independence_audit", len(issues) == 0, issues,
                        {"n_findings": len(findings), "n_flagged": len(bad)})


LEAKAGE_FORBIDDEN_ANCESTOR_STATUSES = {Status.FALSIFIED, Status.FAIL}
LEAKAGE_ACTIVE_STATUSES = {Status.VERIFIED, Status.DERIVED, Status.CALCULATED}


def leakage_control_audit(registries: MDCLRegistries, graph: DependencyGraph) -> AuditResult:
    """No FALSIFIED or FAIL node may be a transitive ancestor of any
    active (VERIFIED/DERIVED/CALCULATED) node -- a rejected hypothesis
    must never silently re-enter the active DAG (FC-005 build command
    section 4: leakage control)."""
    issues = []
    status_by_id = {n.id: n.status for n in registries.all_nodes()}
    for node in registries.all_nodes():
        if node.status not in LEAKAGE_ACTIVE_STATUSES:
            continue
        for ancestor_id in graph.ancestors(node.id):
            ancestor_status = status_by_id.get(ancestor_id)
            if ancestor_status in LEAKAGE_FORBIDDEN_ANCESTOR_STATUSES:
                issues.append(
                    f"{node.id} (status {node.status.value}) has ancestor {ancestor_id} "
                    f"(status {ancestor_status.value}) -- a rejected/failed result must not "
                    f"propagate into an active calculation"
                )
    return AuditResult("leakage_control_audit", len(issues) == 0, issues,
                        {"n_active_nodes_checked": sum(1 for n in registries.all_nodes()
                                                        if n.status in LEAKAGE_ACTIVE_STATUSES)})


def status_audit(registries: MDCLRegistries) -> AuditResult:
    issues = []
    for node in registries.all_nodes():
        if node.status == Status.VERIFIED:
            v = node.provenance.verification if node.provenance else {}
            if not v:
                issues.append(f"{node.id}: status VERIFIED but provenance.verification is empty")
    return AuditResult("status_audit", len(issues) == 0, issues)


def numerical_reproducibility_audit() -> AuditResult:
    from compiler.backends.pipeline_graph_heatflow import run_case
    issues = []
    for topology, n in [("cycle", 12), ("path", 10), ("complete", 6)]:
        r1 = run_case(topology, n)
        r2 = run_case(topology, n)
        import numpy as np
        diff = float(np.max(np.abs(np.array(r1.eigenvalues) - np.array(r2.eigenvalues))))
        if diff > 1e-10:
            issues.append(f"{topology}(n={n}): repeated runs disagree by {diff}")
    return AuditResult("numerical_reproducibility_audit", len(issues) == 0, issues)


def artifact_completeness_audit(required_paths: list[Path]) -> AuditResult:
    issues = [f"missing artifact: {p}" for p in required_paths if not p.exists()]
    return AuditResult("artifact_completeness_audit", len(issues) == 0, issues,
                        {"n_required": len(required_paths)})


def spectral_validation_audit(calculations: list[dict]) -> AuditResult:
    """Enforces the standing spectral-validation rule established during the
    FC-005 CONTINUUM-LIMIT-L-DESI investigation (see FC005_N_SCALING_REPORT.md
    section 5, FC005_CHECKPOINT.md): eigenvalue convergence alone is never
    sufficient grounds for a "converged" verdict wherever eigenvector/
    invariant-subspace comparison data is available -- a scalar
    eigenvalue-only relative-change metric can report a false positive from
    an eigenvalue-crossing artifact (numerically close eigenvalues that
    belong to physically different, unstable eigenvectors). Fails the build
    if any stored "converged" value in a sparse-spectral-comparison
    calculation disagrees with its own recorded "joint_spectral_converged"
    field (compiler/backends/desi_sparse.py::joint_spectral_convergence) --
    i.e. catches any future code path that promotes the superseded
    "eigenvalue_only_converged" value into the canonical "converged" field
    instead of the joint-validated one."""
    issues = []
    n_checked = 0
    for calc in calculations:
        if calc.get("kind") != "desi_sparse_n_scaling_point_process_separation":
            continue
        for name, res in calc.get("results", {}).items():
            if "joint_spectral_converged" not in res:
                continue  # older/other calculation shape without subspace data
            n_checked += 1
            if res["converged"] != res["joint_spectral_converged"]:
                issues.append(
                    f"{calc['id']}/{name}: canonical 'converged'={res['converged']} disagrees "
                    f"with the joint-validated 'joint_spectral_converged'="
                    f"{res['joint_spectral_converged']} -- the eigenvalue-only result must never "
                    f"be promoted over the joint (eigenvalue+eigenvector) verdict"
                )
    return AuditResult("spectral_validation_audit", len(issues) == 0, issues,
                        {"n_datasets_checked": n_checked})


def run_self_audit(registries: MDCLRegistries, required_paths: list[Path] | None = None,
                    calculations: list[dict] | None = None) -> list[AuditResult]:
    graph = build_dependency_graph(registries)
    results = [
        dependency_audit(registries, graph),
        circularity_audit(),
        type_audit(registries),
        provenance_audit(registries),
        target_independence_audit(registries),
        status_audit(registries),
        leakage_control_audit(registries, graph),
        numerical_reproducibility_audit(),
    ]
    if required_paths is not None:
        results.append(artifact_completeness_audit(required_paths))
    if calculations is not None:
        results.append(spectral_validation_audit(calculations))
    return results
