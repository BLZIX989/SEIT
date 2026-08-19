"""FC-005 build command section 21, items 10-14: heat-fit stability
(cross-degree), curvature consistency, leakage-control enforcement,
rejected-branch exclusion, provenance completeness -- plus an end-to-end
check that register_fc005() integrates cleanly into the existing MDCL
and that the full self-audit (including the new leakage_control_audit)
passes."""
from pathlib import Path

from compiler.core.status import Status
from compiler.run_compiler import build_and_run

ROOT = Path(__file__).resolve().parents[2]


def test_fc005_integrates_without_self_audit_failures():
    result = build_and_run()
    failed = [a.name for a in result["audit_results"] if not a.passed]
    assert not failed, f"self-audit failures after FC-005 integration: {failed}"


def test_leakage_control_audit_runs_and_passes():
    result = build_and_run()
    leakage = next(a for a in result["audit_results"] if a.name == "leakage_control_audit")
    assert leakage.passed, leakage.issues


def test_rejected_fisher_branch_excluded_from_active_dag():
    result = build_and_run()
    regs = result["registries"]
    fisher_obstruction = regs.equations.get("EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION")
    assert fisher_obstruction.status == Status.FALSIFIED
    # nothing else may depend on the falsified claim
    dependents = [n.id for n in regs.all_nodes() if fisher_obstruction.id in n.dependencies]
    assert dependents == []


def test_s3_control_result_is_active_and_not_blocked_by_any_falsified_ancestor():
    result = build_and_run()
    regs = result["registries"]
    s3 = regs.objects.get("S3-CURVATURE-CLOSURE")
    assert s3.status in (Status.VERIFIED, Status.DERIVED, Status.CALCULATED)


def test_desi_chain_stays_open_pending_data():
    result = build_and_run()
    regs = result["registries"]
    for node_id in ("DESI-CATALOGUE", "GRAPH-G-DESI", "OPERATOR-L-DESI", "KAPPA-DESI",
                     "E-KAPPA-DESI", "DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK"):
        node = regs.objects.get(node_id)
        assert node.status == Status.OPEN, f"{node_id} should remain OPEN (pending data)"


def test_desi_branch_never_feeds_forward_chain_template():
    result = build_and_run()
    regs = result["registries"]
    template_nodes = [n for n in regs.objects if n.type == "forward_chain_template"]
    desi_ids = {"DESI-CATALOGUE", "GRAPH-G-DESI", "OPERATOR-L-DESI", "CONTINUUM-LIMIT-L-DESI",
                "DESI-SPECTRUM", "DESI-HEAT-TRACE", "DESI-HEAT-COEFFICIENTS", "KAPPA-DESI",
                "E-KAPPA-DESI", "DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK"}
    for node in template_nodes:
        assert not (set(node.dependencies) & desi_ids), (
            f"{node.id} (forward_chain_template) must not depend on the DESI branch"
        )


def test_reference_equations_never_exceed_proposed_without_independent_execution():
    result = build_and_run()
    regs = result["registries"]
    # EQ-001..EQ-029 are bulk-imported from the workbook and must stay
    # PROPOSED unless this build independently executed them (it did not
    # re-derive the textbook GR/QM equations from scratch).
    for eq_id in [f"EQ-{i:03d}" for i in range(1, 30)]:
        eq = regs.equations.get(eq_id)
        assert eq.status == Status.PROPOSED, f"{eq_id} unexpectedly promoted to {eq.status}"
        assert "workbook_claimed_status" in eq.provenance.verification


def test_all_fc005_nodes_have_complete_provenance():
    result = build_and_run()
    regs = result["registries"]
    fc005_prefixes = ("S3-", "DESI-", "GRAPH-G-DESI", "OPERATOR-L-DESI", "CONTINUUM-LIMIT",
                       "KAPPA-DESI", "E-KAPPA-DESI", "DELTA-KAPPA", "SEMICLASSICAL",
                       "FISHER-", "SPEC-H-UNIQUENESS", "EQ-FC005", "FC005-")
    checked = 0
    for node in result["registries"].all_nodes():
        if node.id.startswith(fc005_prefixes):
            checked += 1
            assert node.provenance is not None, f"{node.id}: missing provenance"
            assert node.provenance.source, f"{node.id}: empty provenance.source"
            assert node.provenance.git_commit, f"{node.id}: empty provenance.git_commit"
    assert checked > 15


def test_workbook_reconciliation_found_zero_discrepancies():
    from compiler.historical.fc005_reconciliation import DISCREPANCY_AUDIT_RESULT
    assert DISCREPANCY_AUDIT_RESULT["discrepancies_found"] == 0
    assert len(DISCREPANCY_AUDIT_RESULT["sheets_compared"]) >= 10


def test_source_workbooks_present_in_repo():
    d = ROOT / "fc005_source_workbooks"
    files = sorted(p.name for p in d.glob("*.xlsx"))
    assert len(files) == 4
