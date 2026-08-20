"""KC-003 decomposition and VR-001 Hilbert-space-correspondence test
(canonical_closure_report follow-up Sec.6-7). Extends, does not duplicate,
convergence.py's CONV-001 finding (real DESI N-scaling spectral evidence).

KC-003 is split into 4 independently-tracked sub-claims per the user's own
instruction, rather than treated as one pass/fail. VR-001 is tested
concretely on a real, known manifold control (the circle S^1, whose
Laplacian eigenfunctions are analytically known: cos(k*theta), sin(k*theta)
with eigenvalue k^2) under uniform and nonuniform sampling -- the literal
"constant functions, low spectral modes... nonuniform sampling controls"
test the instruction asks for -- while being explicit that this validates
the TEST METHODOLOGY on a case with a known answer, not the real DESI
data's own convergence (already separately, honestly assessed as FAIL in
convergence.py/CONV-001).
"""
from __future__ import annotations

import numpy as np


def kc003_decomposition() -> dict:
    return {
        "KC-003a_measure_convergence": {
            "statement": "empirical point measure mu_N -> continuum measure mu as N->infinity",
            "status": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS",
            "missing_object": "The real DESI sparse N-scaling data "
                               "(data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json) "
                               "records only summary spectral quantities per N (epsilon, "
                               "avg_degree, nnz, low_eigenvalues) -- not the underlying point "
                               "coordinates/density weights at each N needed to directly test "
                               "empirical-measure weak convergence against a stated target "
                               "continuum measure.",
        },
        "KC-003b_operator_convergence": {
            "statement": "L_N -> L (in an appropriate operator-norm or resolvent sense) as N->infinity",
            "status": "PARTIALLY ADDRESSED via CONV-001's numerical relative-change evidence "
                      "(see convergence.py) -- NOT a rigorous operator-norm/resolvent proof, "
                      "which requires the same missing H_n->H identification map CONV-001 "
                      "already identified as absent from the corpus.",
        },
        "KC-003c_spectral_convergence": {
            "statement": "lambda_k(L_N) -> lambda_k(L) for each fixed k as N->infinity",
            "status": "COMPUTED (CONV-001) -- see convergence.py's per-dataset results: "
                      "uniform synthetic data shows decaying relative change consistent with "
                      "spectral convergence; real DESI/clustered data does not.",
        },
        "KC-003d_geometric_convergence": {
            "statement": "the reconstructed metric/geometric quantities (distance, curvature) "
                         "converge to their continuum values",
            "status": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS -- blocked by the same "
                      "d(i,j)->g_munu gap already identified in DERIVATION_FRONTIER.md "
                      "(no g_munu construction from d(i,j) exists to test convergence of).",
        },
    }


def _circle_graph(n: int, nonuniform: bool = False, seed: int = 0):
    """n points on the unit circle; k-NN graph. nonuniform=True clusters
    points in one arc (a real, controllable density-bias test case)."""
    rng = np.random.default_rng(seed)
    if nonuniform:
        # beta-like clustering: more points near theta=0
        theta = rng.beta(0.3, 3.0, size=n) * 2 * np.pi
    else:
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    theta = np.sort(theta)
    points = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    k = max(2, int(np.log(n)))
    A = np.zeros((n, n))
    for i in range(n):
        d = np.linalg.norm(points - points[i], axis=1)
        nn = np.argsort(d)[1:k + 1]
        for j in nn:
            A[i, j] = A[j, i] = 1.0
    D = np.diag(A.sum(axis=1))
    L = D - A
    return theta, L


def vr001_known_manifold_control(n_values: tuple[int, ...] = (100, 300, 800)) -> dict:
    """S^1's Laplace-Beltrami eigenfunctions are exactly cos(theta),
    sin(theta) (eigenvalue 1, up to normalization/discretization scale).
    Tests whether the graph Laplacian's low nonzero eigenvector converges
    (in normalized inner product with the true cos(theta)) as N increases,
    under uniform vs nonuniform sampling -- a real, checkable convergence
    test with a KNOWN correct answer, unlike the real DESI case."""
    results = {"uniform": {}, "nonuniform": {}}
    for label, nonuniform in (("uniform", False), ("nonuniform", True)):
        for n in n_values:
            theta, L = _circle_graph(n, nonuniform=nonuniform)
            vals, vecs = np.linalg.eigh(L)
            vals = np.clip(vals, 0.0, None)
            # first nonzero mode(s) -- circle Laplacian has a DEGENERATE
            # pair (cos,sin) at the lowest nonzero eigenvalue; compare
            # against the 2-dim span, not a single vector, to avoid a
            # meaningless single-vector-alignment artifact from the
            # arbitrary basis choice within the degenerate eigenspace.
            nonzero_idx = np.where(vals > 1e-6)[0]
            v1, v2 = vecs[:, nonzero_idx[0]], vecs[:, nonzero_idx[1]]
            true_cos, true_sin = np.cos(theta), np.sin(theta)
            true_cos, true_sin = true_cos / np.linalg.norm(true_cos), true_sin / np.linalg.norm(true_sin)
            # projection of the true functions onto the computed 2-dim
            # degenerate eigenspace -- should approach norm 1 as N grows
            # if the eigenspace converges to span{cos,sin}.
            basis = np.stack([v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2)], axis=1)
            proj_cos_norm = float(np.linalg.norm(basis.T @ true_cos))
            proj_sin_norm = float(np.linalg.norm(basis.T @ true_sin))
            results[label][n] = {
                "lambda_first_nonzero": float(vals[nonzero_idx[0]]),
                "cos_theta_projection_norm_onto_computed_eigenspace": proj_cos_norm,
                "sin_theta_projection_norm_onto_computed_eigenspace": proj_sin_norm,
                "converged_close_to_1": bool(proj_cos_norm > 0.9 and proj_sin_norm > 0.9),
            }
    return {
        "claim": "VR-001 methodology test on a KNOWN manifold (S^1) where the correct answer "
                 "is analytically known -- NOT a claim about real DESI data (see KC-003a/d "
                 "above for why that specific case remains open)",
        "results": results,
        "interpretation": (
            "Under uniform sampling, the computed low eigenspace should increasingly align "
            "with the true span{cos(theta),sin(theta)} as N grows (projection norms -> 1). "
            "Under nonuniform (clustered) sampling with the SAME unnormalized graph "
            "Laplacian, density bias is expected to degrade this convergence -- exactly the "
            "known diffusion-map-theory distinction the corpus's own FC-005 investigation "
            "already turns on (density-normalized vs raw constructions)."
        ),
    }
