#!/usr/bin/env python3
"""FC-005 diagnostics: (1) operator-action test (spec section 11) against
analytic Delta references on a uniform Euclidean control (the only case
where an independent continuum Delta_h is legitimately known -- flat
metric, polynomial test functions have EXACT closed-form Laplacians
everywhere, not merely approximations); DESI's point cloud has no
independently known metric, so for DESI we report the no-reference
self-consistency diagnostic only, as required.
(2) k-nearest-neighbour graph sweep (spec section 7) as an independent
graph-construction family (vs. the epsilon-ball kernel graph used
elsewhere), symmetrized via max(w_ij, w_ji), compared against directed
kNN (before symmetrization) for W_ij>=0 / L=L^T / connectivity effects.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from compiler.backends.desi_diagnostics import (
    _connected_components, audit_graph, median_nn_distance, operator_action_residual,
)
from compiler.backends.desi_fc005_pipeline import _low_eigen
from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, catalogue_to_points, gaussian_kernel_C_K,
    graph_laplacian_from_weights,
)
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi
from run_desi_diagnostics import SEED, make_uniform_box

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"


# ---------------------------------------------------------------------
# 1. Operator-action test
# ---------------------------------------------------------------------

def f_linear(pts):
    return pts[:, 0].copy()


def delta_linear(pts):
    return np.zeros(len(pts))


def f_quadratic(pts):
    return (pts ** 2).sum(axis=1)


def delta_quadratic(pts):
    return np.full(len(pts), 6.0)


def run_operator_action_test():
    print("=== Operator-action test (spec section 11) ===")
    box = 200.0
    N = 3000
    pts = make_uniform_box(N, box, SEED)
    eps = 1.0 * median_nn_distance(pts)
    W = build_kernel_graph(pts, epsilon=eps)
    _, L = graph_laplacian_from_weights(W)
    C_K = gaussian_kernel_C_K(3)
    L_tilde = -L / (C_K * N * eps ** 5.0)

    interior_mask = np.all((pts > box * 0.2) & (pts < box * 0.8), axis=1)
    print(f"  N={N} eps={eps:.3f} interior points={interior_mask.sum()} (excludes box boundary)")

    results = {}
    for name, f, delta_f in [("linear (Delta=0 exact)", f_linear, delta_linear),
                              ("quadratic (Delta=6 exact)", f_quadratic, delta_quadratic)]:
        full = operator_action_residual(L_tilde, pts, f, delta_f)
        f_vals = f(pts)
        Lf = L_tilde @ f_vals
        ref = delta_f(pts)
        interior_residual = float(np.linalg.norm(Lf[interior_mask] - ref[interior_mask]) /
                                   max(np.linalg.norm(ref[interior_mask]), 1e-12))
        print(f"  {name}: whole-domain relative_residual={full['relative_residual']:.4f}  "
              f"interior-only relative_residual={interior_residual:.4f}")
        results[name] = {"whole_domain": full["relative_residual"], "interior_only": interior_residual}

    manifest = json.loads((ROOT / "FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    desi_pts_full = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                                         binned.canonical["Z"], cosmo)
    rng = np.random.default_rng(SEED)
    desi_pts = desi_pts_full[rng.choice(len(desi_pts_full), size=3000, replace=False)]
    eps_d = median_nn_distance(desi_pts)
    W_d = build_kernel_graph(desi_pts, epsilon=eps_d)
    _, L_d = graph_laplacian_from_weights(W_d)
    L_tilde_d = -L_d / (C_K * 3000 * eps_d ** 5.0)
    no_ref = operator_action_residual(L_tilde_d, desi_pts, f_linear, None)
    print(f"  DESI (no independent reference available): {no_ref}")
    results["desi_no_reference"] = no_ref
    return results


# ---------------------------------------------------------------------
# 2. kNN graph sweep
# ---------------------------------------------------------------------

def build_knn_graph(points, k, sigma=None):
    tree = cKDTree(points)
    dist, idx = tree.query(points, k=k + 1)
    n = len(points)
    if sigma is None:
        sigma = float(np.median(dist[:, 1:]))
    W_directed = np.zeros((n, n))
    for i in range(n):
        for jj, d in zip(idx[i, 1:], dist[i, 1:]):
            W_directed[i, jj] = np.exp(-d ** 2 / sigma ** 2)
    W_sym = np.maximum(W_directed, W_directed.T)
    return W_directed, W_sym, sigma


def run_knn_sweep():
    print("\n=== kNN graph sweep (spec section 7) ===")
    manifest = json.loads((ROOT / "FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    desi_pts_full = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                                         binned.canonical["Z"], cosmo)
    rng = np.random.default_rng(SEED)
    N = 2000
    pts = desi_pts_full[rng.choice(len(desi_pts_full), size=N, replace=False)]

    C_K = gaussian_kernel_C_K(3)
    results = []
    for k in [8, 16, 32, 64, 128]:
        W_dir, W_sym, sigma = build_knn_graph(pts, k)
        directed_asymmetry = float(np.max(np.abs(W_dir - W_dir.T)))
        n_comp_dir, _ = _connected_components(W_dir)
        n_comp_sym, _ = _connected_components(W_sym)
        _, L_sym = graph_laplacian_from_weights(W_sym)
        L_tilde = -L_sym / (C_K * N * sigma ** 5.0)
        low_vals, _, residual = _low_eigen(-L_tilde, 20)
        row = {
            "k": k, "sigma": sigma,
            "directed_asymmetry_max_abs": directed_asymmetry,
            "n_connected_components_directed": n_comp_dir,
            "n_connected_components_symmetrized": n_comp_sym,
            "spectral_gap": float(low_vals[1]) if len(low_vals) > 1 else float("nan"),
            "solver_residual": residual,
        }
        results.append(row)
        print(f"  k={k}: sigma={sigma:.2f} directed_comp={n_comp_dir} sym_comp={n_comp_sym} "
              f"gap={row['spectral_gap']:.3e} directed_vs_sym_asymmetry={directed_asymmetry:.4f}")
    return results


def main():
    op_results = run_operator_action_test()
    knn_results = run_knn_sweep()
    out = {"operator_action_test": op_results, "knn_sweep": knn_results}
    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "operator_and_knn_results.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
