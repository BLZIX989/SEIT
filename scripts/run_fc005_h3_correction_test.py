#!/usr/bin/env python3
"""Master SEIT Theory Derivation Campaign, Hypothesis H3: genuine attempt
to test whether a non-circular correction to the sparse discrete-to-
continuum pipeline changes the already-established finding that modes
5-15 fail joint eigenvalue+eigenvector convergence (FC005_N_SCALING_REPORT.md
section 5).

This is a REAL numerical experiment against the REAL DESI DR1 LRG SGC
pilot catalogue already present in this repository (data/desi/dr1/fc005/
raw/LRG_SGC_clustering.dat.fits), reusing the actual pipeline code
(compiler/backends/desi_sparse.py, desi_graph.py, desi_schema.py) --
not a simulation and not a re-assertion of the prior finding.

Two non-circular candidate corrections are tested (a third, the
curvature-dependent kernel correction floated in the counterfactual
manuscript, is analytically ruled out below as CIRCULAR and is NOT
attempted numerically -- see the docstring note before CANDIDATE C):

  CANDIDATE A: tighter ARPACK tolerance / more iterations -- tests
  whether the mode 5-15 instability is a solver-precision artifact
  rather than a genuine statistical non-convergence.

  CANDIDATE B: a bandwidth (epsilon) sweep at fixed N -- tests whether
  a different, still data-independent choice of epsilon (not requiring
  any external geometric information) stabilizes the higher modes.

Writes FC005_H3_CORRECTION_TEST_RESULTS.json with the full, honest
result of both tests.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from compiler.backends.desi_graph import CosmologyModel, catalogue_to_points, gaussian_kernel_C_K
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi
from compiler.backends.desi_sparse import (
    alpha_normalize_sparse, build_sparse_kernel_graph, eigenvector_subspace_comparison,
    joint_spectral_convergence, sparse_graph_laplacian, sparse_low_eigen,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
D = 3
N_SMALL, N_LARGE = 4000, 8000
N_MODES = 15
SEED = 20250819


def load_desi_points():
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmology = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    pts = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                               binned.canonical["Z"], cosmology)
    w = np.asarray(binned.canonical["WEIGHT"], dtype=np.float64)
    return pts, w


def subsample_nested(pts, w, n_small, n_large, seed):
    rng = np.random.default_rng(seed)
    idx_large = rng.choice(len(pts), size=n_large, replace=False)
    idx_small = idx_large[:n_small]  # nested prefix, per pipeline convention
    return (pts[idx_small], w[idx_small] if w is not None else None,
            pts[idx_large], w[idx_large] if w is not None else None)


def solve_and_classify(pts_s, w_s, pts_l, w_l, epsilon_s, epsilon_l, *, alpha=0.0,
                        tol=1e-8, maxiter=500, cutoff_multiplier=6.0):
    Ws = build_sparse_kernel_graph(pts_s, epsilon_s, weights=w_s, cutoff_multiplier=cutoff_multiplier)
    Ws = alpha_normalize_sparse(Ws, alpha=alpha)
    _, Ls = sparse_graph_laplacian(Ws)
    C_K = gaussian_kernel_C_K(D)
    neg_Lt_s = Ls / (C_K * len(pts_s) * epsilon_s ** (D + 2))

    Wl = build_sparse_kernel_graph(pts_l, epsilon_l, weights=w_l, cutoff_multiplier=cutoff_multiplier)
    Wl = alpha_normalize_sparse(Wl, alpha=alpha)
    _, Ll = sparse_graph_laplacian(Wl)
    neg_Lt_l = Ll / (C_K * len(pts_l) * epsilon_l ** (D + 2))

    res_s = sparse_low_eigen(neg_Lt_s, N_MODES, tol=tol, maxiter=maxiter)
    res_l = sparse_low_eigen(neg_Lt_l, N_MODES, tol=tol, maxiter=maxiter)

    k = min(len(res_s.eigenvalues), len(res_l.eigenvalues))
    clusters = eigenvector_subspace_comparison(
        res_s.eigenvectors[:, :k], res_l.eigenvectors[:, :k], len(pts_s),
        res_s.eigenvalues[:k], res_l.eigenvalues[:k],
    )
    verdict = joint_spectral_convergence(clusters)
    return {
        "n_modes_small": len(res_s.eigenvalues), "n_modes_large": len(res_l.eigenvalues),
        "arpack_converged_small": res_s.converged, "arpack_converged_large": res_l.converged,
        "max_residual_small": res_s.max_residual, "max_residual_large": res_l.max_residual,
        "clusters": clusters, "verdict": verdict,
    }


def main():
    t0 = time.time()
    print("Loading real DESI DR1 LRG SGC catalogue...")
    pts, w = load_desi_points()
    print(f"  loaded {len(pts)} points in {time.time()-t0:.1f}s")

    pts_s, w_s, pts_l, w_l = subsample_nested(pts, w, N_SMALL, N_LARGE, SEED)

    # baseline epsilon: median-nearest-neighbour-style heuristic already
    # used by the real pipeline's epsilon_scaling_sequence anchored at the
    # same eps_ref/N_ref recorded in the existing derived results.
    prior = json.loads((ROOT / "data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json").read_text())
    eps_ref = prior["desi_alpha0.0"]["eps_ref"]
    N_ref = prior["desi_alpha0.0"]["N_ref"]
    eps_small_baseline = eps_ref * (N_ref / N_SMALL) ** (1.0 / (D + 4))
    eps_large_baseline = eps_ref * (N_ref / N_LARGE) ** (1.0 / (D + 4))

    results = {"n_small": N_SMALL, "n_large": N_LARGE, "seed": SEED,
               "eps_small_baseline": eps_small_baseline, "eps_large_baseline": eps_large_baseline}

    print("\n[SANITY CHECK] Reproducing baseline (uncorrected) behaviour at this N pair...")
    baseline = solve_and_classify(pts_s, w_s, pts_l, w_l, eps_small_baseline, eps_large_baseline)
    results["baseline"] = baseline
    print(f"  baseline verdict: joint_converged={baseline['verdict']['joint_converged']}, "
          f"{baseline['verdict']['reason']}")

    print("\n[CANDIDATE A] Tighter ARPACK tolerance (tol=1e-12, maxiter=3000)...")
    t1 = time.time()
    candA = solve_and_classify(pts_s, w_s, pts_l, w_l, eps_small_baseline, eps_large_baseline,
                                tol=1e-12, maxiter=3000)
    results["candidate_A_tighter_tolerance"] = candA
    print(f"  ({time.time()-t1:.1f}s) verdict: joint_converged={candA['verdict']['joint_converged']}, "
          f"{candA['verdict']['reason']}")

    print("\n[CANDIDATE B] Bandwidth sweep at fixed N (0.5x, 1x, 2x baseline epsilon)...")
    sweep = {}
    for mult in [0.5, 1.0, 2.0]:
        t1 = time.time()
        r = solve_and_classify(pts_s, w_s, pts_l, w_l,
                                eps_small_baseline * mult, eps_large_baseline * mult)
        sweep[str(mult)] = r
        print(f"  eps x{mult} ({time.time()-t1:.1f}s): joint_converged={r['verdict']['joint_converged']}, "
              f"{r['verdict']['reason']}")
    results["candidate_B_bandwidth_sweep"] = sweep

    results["candidate_C_curvature_kernel_correction"] = {
        "attempted_numerically": False,
        "reason": (
            "CIRCULAR AS STATED, ruled out analytically before any computation: the "
            "counterfactual manuscript's proposed K_corrected = K_Gaussian * (1 + c2*eps^2*R(x) "
            "+ O(eps^4)) requires R(x), the target-space Ricci scalar curvature, as an INPUT to "
            "the kernel used to construct the very operator whose spectrum is meant to DERIVE "
            "R(x) in the first place (per the master equation's own a2 heat-kernel term, Sec. 5 "
            "of the counterfactual manuscript). No independent, non-circular source for R(x) "
            "exists anywhere in this pipeline prior to the continuum limit this correction is "
            "supposed to help achieve. This is exactly the target-conditioned-input failure mode "
            "Section XI/XVII of the campaign instruction requires flagging, not attempting to "
            "route around by inventing a value for R(x)."
        ),
    }

    results["total_elapsed_seconds"] = time.time() - t0
    out_path = ROOT / "FC005_H3_CORRECTION_TEST_RESULTS.json"
    out_path.write_text(json.dumps(results, indent=2, default=lambda o: float(o) if isinstance(o, np.floating) else o))
    print(f"\nWrote {out_path} ({time.time()-t0:.1f}s total)")


if __name__ == "__main__":
    main()
