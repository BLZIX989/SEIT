"""Integration test for the first executable test (spec section 31):
Ø -> graph G -> L=D-A -> Spec(L) -> e^{-tL} -> P_ker(L).
"""
import pytest

from compiler.backends.pipeline_graph_heatflow import DEFAULT_SWEEP, run_case, run_sweep


@pytest.mark.parametrize("topology,n", DEFAULT_SWEEP)
def test_sweep_case_passes(topology, n):
    seed = 42 if topology == "erdos_renyi" else None
    r = run_case(topology, n, seed=seed)
    assert r.eigen_equation_residual < 1e-6, "L phi_n = lambda_n phi_n must hold numerically"
    assert r.heat_eigen_action_residual < 1e-6, "R(t) phi_n = e^{-t lambda_n} phi_n must hold"
    assert r.kernel_convergence["hypotheses"]["symmetric"]
    assert r.kernel_convergence["hypotheses"]["positive_semidefinite"]
    assert r.kernel_convergence["converges"], (
        "e^{-tL} must converge to P_ker(L) once hypotheses hold and t is scaled to 1/gap"
    )
    assert r.passed


def test_connected_graph_has_one_dimensional_kernel():
    for topology, n in [("path", 6), ("cycle", 6), ("complete", 6), ("star", 6)]:
        r = run_case(topology, n)
        assert r.zero_modes == [0], f"{topology}(n={n}) should have a 1-dim kernel (connected graph)"


def test_exact_vs_numeric_cross_check_present_for_small_graphs():
    r = run_case("cycle", 5)
    assert r.exact_cross_check is not None
    assert r.exact_cross_check.passed
    assert r.exact_cross_check.precision == "numeric"  # residual comparison, exact eigs as reference


def test_complete_graph_spectral_gap_equals_n():
    # Well-known closed form: Spec(L_{K_n}) = {0, n (multiplicity n-1)}
    r = run_case("complete", 7)
    assert abs(r.spectral_gap - 7.0) < 1e-6


def test_full_default_sweep_all_pass():
    results = run_sweep()
    failed = [r.label for r in results if not r.passed]
    assert not failed, f"sweep cases failed: {failed}"
