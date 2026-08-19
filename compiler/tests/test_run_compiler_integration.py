"""End-to-end integration test: build the full MDCL, run both executable
tests, run the self-audit, and check the terminal status is never forced
to CLOSED (spec section 5: never force CLOSED)."""
from compiler.core.status import TerminalStatus
from compiler.run_compiler import build_and_run


def test_full_build_self_audit_passes():
    result = build_and_run()
    failed = [a.name for a in result["audit_results"] if not a.passed]
    assert not failed, f"self-audit failures: {failed}"


def test_terminal_status_never_forced_closed():
    result = build_and_run()
    assert result["terminal_status"] != TerminalStatus.CLOSED


def test_selection_sigma_remains_open():
    result = build_and_run()
    sigma = result["registries"].transformations.get("SELECTION-SIGMA")
    from compiler.core.status import Status
    assert sigma.status == Status.OPEN, "Sigma must stay an unresolved compiler component (spec section 10)"


def test_historical_claims_not_wired_as_upstream_dependencies_of_gauge_node():
    result = build_and_run()
    gauge = result["registries"].objects.get("GAUGE-NODE")
    assert "T2-HISTORICAL" not in gauge.dependencies, (
        "spec section 33: historical claims must never be upstream selectors"
    )


def test_diffusion_metric_never_reaches_exact_classification():
    result = build_and_run()
    for report in result["test_results"]["test2_reports"]:
        assert report.classification != "exact"


def test_falsification_records_are_nonempty():
    result = build_and_run()
    assert len(result["falsifications"]) >= 1
