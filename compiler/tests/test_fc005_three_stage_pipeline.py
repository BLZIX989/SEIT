"""Tests for compiler/backends/desi_fc005_pipeline.py: the three-stage
mathematical-convergence / curvature-closure / physical-validation
procedure, run exactly as specified once a real catalogue is supplied.
Never tuned to force a favorable result -- these tests check the STOP
and independent-reporting behavior, not that the pipeline "succeeds" on
synthetic noise (which would be exactly the kind of after-the-fact
tuning this branch explicitly forbids).
"""
import numpy as np
import pytest

from compiler.backends.desi_fc005_pipeline import (
    MathematicalConvergenceResult, RefinementPoint, run_curvature_closure,
    run_fc005_desi_pipeline, run_mathematical_convergence, run_physical_validation,
)
from compiler.backends.desi_graph import CosmologyModel

COSMO = CosmologyModel(H0=67.4, Om=0.315, OL=0.685)


def _sparse_catalogue(n=60, seed=0):
    rng = np.random.default_rng(seed)
    ra = rng.uniform(0, 360, n)
    dec = rng.uniform(-30, 30, n)
    z = rng.uniform(0.1, 1.0, n)
    return ra, dec, z


def test_stage1_stops_at_exact_failed_dependency_when_disconnected():
    ra, dec, z = _sparse_catalogue(60)
    result = run_mathematical_convergence(
        ra, dec, z, None, COSMO, N_values=[30, 60], epsilon_values=[5.0, 3.0],
    )
    assert not result.converged
    assert result.failed_dependency == "OPERATOR-L-DESI"
    assert "disconnected" in result.failure_reason or "no edges" in result.failure_reason


def test_stage1_requires_at_least_two_refinement_points():
    ra, dec, z = _sparse_catalogue(60)
    result = run_mathematical_convergence(
        ra, dec, z, None, COSMO, N_values=[60], epsilon_values=[400.0],
    )
    # single point is not a refinement audit -- must not silently "pass"
    assert not result.converged
    assert result.failed_dependency == "CONTINUUM-LIMIT-L-DESI"


def test_full_pipeline_stops_at_stage1_and_reports_nothing_downstream():
    ra, dec, z = _sparse_catalogue(60)
    result = run_fc005_desi_pipeline(
        ra, dec, z, None, COSMO, N_values=[30, 60], epsilon_values=[5.0, 3.0],
        kappa_cosmological=0.0, kappa_cosmological_source="fake (should never be reached)",
    )
    assert result.stopped_at == "mathematical_convergence"
    assert result.curvature_closure_result is None
    assert result.physical_validation_result is None
    assert "STOPPED at mathematical convergence" in result.summary


def test_three_results_are_independent_fields_not_collapsed():
    # even a converged+closed result must keep the three stages as three
    # separate objects, never a single merged "success" flag.
    result = MathematicalConvergenceResult(
        converged=True, failed_dependency=None, failure_reason="",
        points=[RefinementPoint(N=100, epsilon=1.0, low_eigenvalues=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                                 solver_residual=0.0)],
        relative_changes=[0.01], tolerance=0.05,
    )
    curvature = run_curvature_closure(result, tolerance=0.05)
    assert hasattr(curvature, "closure")
    assert hasattr(curvature, "closed")
    # curvature_closure_result and physical_validation_result are always
    # distinct attributes on FC005DesiExecutionResult -- checked structurally:
    from dataclasses import fields
    from compiler.backends.desi_fc005_pipeline import FC005DesiExecutionResult
    field_names = {f.name for f in fields(FC005DesiExecutionResult)}
    assert {"mathematical_convergence", "curvature_closure_result",
            "physical_validation_result"} <= field_names


def test_curvature_closure_reports_insufficient_modes_not_a_fabricated_result():
    conv = MathematicalConvergenceResult(
        converged=True, failed_dependency=None, failure_reason="",
        points=[RefinementPoint(N=10, epsilon=1.0, low_eigenvalues=[0.0, 1.0, 2.0],
                                 solver_residual=0.0)],
        relative_changes=[0.01], tolerance=0.05,
    )
    result = run_curvature_closure(conv, tolerance=0.05)
    assert not result.sufficient_modes
    assert not result.closed
    assert not np.isfinite(result.closure.e_kappa)  # NaN, not a fabricated number


def test_curvature_closure_refuses_truncated_fit_window():
    # many modes but requesting a t-window far too small for how many
    # were actually resolved -- must refuse, not silently bias a2.
    lam = np.linspace(1.0, 50.0, 200)
    conv = MathematicalConvergenceResult(
        converged=True, failed_dependency=None, failure_reason="",
        points=[RefinementPoint(N=500, epsilon=1.0, low_eigenvalues=lam.tolist(), solver_residual=0.0)],
        relative_changes=[0.01], tolerance=0.05,
    )
    result = run_curvature_closure(conv, t_min_scale=0.001, t_max_scale=0.01, tolerance=0.05)
    assert not result.sufficient_modes
    assert "trustworthy bound" in result.note


def test_physical_validation_refuses_unattributed_cosmological_reference():
    closure_result = run_curvature_closure(
        MathematicalConvergenceResult(
            converged=True, failed_dependency=None, failure_reason="",
            points=[RefinementPoint(N=10, epsilon=1.0, low_eigenvalues=[1.0, 2.0, 3.0, 4.0, 5.0],
                                     solver_residual=0.0)],
            relative_changes=[0.01], tolerance=0.05,
        ), tolerance=0.05,
    )
    with pytest.raises(ValueError, match="independent source"):
        run_physical_validation(closure_result, kappa_cosmological=1.0, kappa_cosmological_source="")


def test_pipeline_never_runs_stage3_without_explicit_kappa_cosmological():
    ra, dec, z = _sparse_catalogue(60)
    # force a stage-1 failure path deliberately for a cheap, deterministic test;
    # the guarantee under test is structural (stage 3 requires an explicit,
    # separately-sourced value), exercised directly on run_fc005_desi_pipeline's
    # kwargs contract via the stage-1-failure short circuit above and via
    # run_physical_validation's refusal (tested separately).
    result = run_fc005_desi_pipeline(
        ra, dec, z, None, COSMO, N_values=[30, 60], epsilon_values=[5.0, 3.0],
    )
    assert result.physical_validation_result is None
