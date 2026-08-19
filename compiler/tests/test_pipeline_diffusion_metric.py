"""Integration test for the second executable test (spec section 32):
Spec(L) -> diffusion distance -> metric candidate, with mandatory
exact/approximate/conditional/divergent/non_unique classification.
"""
from compiler.backends.diffusion_metric import diffusion_distance_matrix, refinement_sweep
from compiler.backends.graph_laplacian import build_graph, laplacian
from compiler.backends.spectral import spectrum


def test_diffusion_distance_matrix_is_symmetric_and_zero_diagonal():
    g = build_graph("cycle", 8)
    L = laplacian(g.adjacency())
    spec = spectrum(L)
    D = diffusion_distance_matrix(spec, t=0.5)
    assert (abs(D - D.T) < 1e-9).all()
    assert (abs(D.diagonal()) < 1e-9).all()


def test_refinement_sweep_never_claims_exact():
    # Spec section 32: do NOT infer continuum geometry from numerical
    # resemblance -- "exact" must never come out of a purely numeric
    # refinement sweep with no analytic convergence proof registered.
    for topology in ("cycle", "path"):
        report = refinement_sweep(topology, sizes=[8, 16, 32, 64])
        assert report.classification != "exact"
        assert report.classification in {"approximate", "conditional", "divergent", "non_unique"}


def test_refinement_sweep_reports_time_parameter_sensitivity():
    report = refinement_sweep("cycle", sizes=[8, 16, 32, 64], tau_multipliers=[0.5, 1.0, 2.0])
    assert report.across_time_choice_spread >= 0.0
    assert len(report.points) == 4


def test_grid2d_refinement_sweep_runs():
    report = refinement_sweep("grid2d", sizes=[3, 4, 5, 6])
    assert report.classification in {"approximate", "conditional", "divergent", "non_unique"}
    assert len(report.normalized_sequence) == 4
