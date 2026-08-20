#!/usr/bin/env python3
"""FC-005: separate finite-resolution failure from point-process failure
in the CONTINUUM-LIMIT-L-DESI investigation, per the follow-up
instruction after FC005_CONTINUUM_DIAGNOSTIC_REPORT.md.

Sparse eigensolves (never densified), nested N-refinement up to N=64000
(DESI, bounded by the real 160,150-object pilot-bin catalogue) / up to
N=128000 for the synthetic controls (unbounded), and the CORRECTED
epsilon-scaling rate eps_N ~ N^{-1/(d+4)} (see compiler/backends/
desi_sparse.py module docstring for the derivation of why the previous
N^{-1/d} rate was asymptotically wrong).

Three point processes x two normalizations (alpha=0 plain, alpha=1
Coifman-Lafon density-normalized) = 6 configurations, all run through
the identical procedure for direct comparison.

Writes:
  FC005_SPARSE_SPECTRAL_RESULTS.csv
  FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv
  FC005_POINT_PROCESS_COMPARISON.csv
  data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import connected_components

from compiler.backends.desi_diagnostics import median_nn_distance
from compiler.backends.desi_graph import CosmologyModel, catalogue_to_points, gaussian_kernel_C_K
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi
from compiler.backends.desi_sparse import (
    alpha_normalize_sparse, build_sparse_kernel_graph, eigenvector_subspace_comparison,
    epsilon_scaling_sequence, operator_identification, relative_changes_scaled,
    sparse_graph_laplacian, sparse_low_eigen, verify_asymptotic_conditions,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
D = 3
N_REF = 4000
N_VALUES_DESI = [4000, 8000, 16000, 32000, 64000]
# N=128000 was attempted for the synthetic controls and timed out after
# 300s in a standalone eigsh(which='SA') timing test (never completed) --
# with 6 total (process, alpha) configurations this is not feasible
# within this session's compute budget, so 64000 is the shared ceiling.
# This is the computational-feasibility boundary named in the spec
# (section 7/15), recorded rather than silently dropped.
N_VALUES_SYNTH = [4000, 8000, 16000, 32000, 64000]
N_MODES = 15
SEED = 20250819
TOLERANCE = 0.15


def run_process(label: str, pts_full: np.ndarray, w_full: np.ndarray | None,
                 N_values: list[int], *, alpha: float, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    idx_order = rng.permutation(len(pts_full))
    C_K = gaussian_kernel_C_K(D)

    pts_ref = pts_full[idx_order[:N_REF]]
    eps_ref = median_nn_distance(pts_ref)
    eps_values = epsilon_scaling_sequence(eps_ref, N_REF, N_values, d=D)
    asymptotic_check = verify_asymptotic_conditions(N_values, eps_values, d=D)

    t0 = time.time()
    per_N = []
    low_eigs_seq = []
    eigvecs_seq = []
    for N, eps in zip(N_values, eps_values):
        if N > len(pts_full):
            per_N.append({"N": N, "status": "SKIPPED_EXCEEDS_CATALOGUE"})
            low_eigs_seq.append(None)
            eigvecs_seq.append(None)
            continue
        idx = idx_order[:N]
        pts = pts_full[idx]
        w = w_full[idx] if w_full is not None else None
        t_n0 = time.time()
        W = build_sparse_kernel_graph(pts, epsilon=eps, weights=w)

        n_comp, labels = connected_components(W, directed=False)
        largest_fraction = 1.0
        restricted = False
        if n_comp > 1:
            sizes = np.bincount(labels)
            keep_label = int(np.argmax(sizes))
            largest_fraction = float(sizes.max() / N)
            keep_mask = labels == keep_label
            W = W[keep_mask][:, keep_mask]
            restricted = True
            N_eff = int(keep_mask.sum())
        else:
            N_eff = N

        W = alpha_normalize_sparse(W, alpha=alpha)
        _, L = sparse_graph_laplacian(W)
        norm_const = C_K * N_eff * eps ** (D + 2)
        neg_L_tilde = (1.0 / norm_const) * L  # Spec(-L_tilde) = Spec(L)/norm_const
        # maxiter bounded to a practical budget (500 ARPACK restarts):
        # the clustered-control graph was measured directly to induce
        # severe ARPACK ill-conditioning (near-decoupled density clumps
        # produce a cluster of near-zero eigenvalues), taking >500s at
        # N=8000 with the unbounded default. A tight, uniformly-applied
        # budget means a genuinely stuck case fails fast and honestly
        # (recorded as arpack_converged=False) rather than consuming the
        # whole session's compute -- non-convergence itself is a valid,
        # disclosed diagnostic result per the spec ("record ... maximum
        # iterations, convergence residuals"), not a suppressed failure.
        result = sparse_low_eigen(neg_L_tilde, N_MODES, maxiter=500)
        elapsed = time.time() - t_n0
        avg_degree = float(W.sum() / N_eff)
        n_converged_modes = len(result.eigenvalues)
        status = "OK" if n_converged_modes >= 2 else "ARPACK_INSUFFICIENT_CONVERGED_MODES"
        per_N.append({
            "N": N, "N_effective": N_eff, "n_connected_components": int(n_comp),
            "largest_component_fraction": largest_fraction, "restricted_to_largest": restricted,
            "epsilon": eps, "avg_degree": avg_degree, "nnz": int(W.nnz),
            "solver": result.solver, "sigma": result.sigma, "tol": result.tol,
            "maxiter": result.maxiter, "n_modes_requested": result.n_modes_requested,
            "n_modes_converged": n_converged_modes,
            "max_residual": result.max_residual, "arpack_converged": result.converged,
            "elapsed_seconds": elapsed, "status": status,
            "low_eigenvalues": result.eigenvalues.tolist(),
        })
        if status == "OK":
            low_eigs_seq.append(result.eigenvalues)
            eigvecs_seq.append(result.eigenvectors)
        else:
            low_eigs_seq.append(None)
            eigvecs_seq.append(None)
        lambda1_str = f"{result.eigenvalues[1]:.4e}" if n_converged_modes >= 2 else "N/A"
        print(f"    [{label} alpha={alpha}] N={N} eps={eps:.4f} avg_deg={avg_degree:.1f} "
              f"nnz={W.nnz} n_comp={n_comp} largest_frac={largest_fraction:.4f} "
              f"resid={result.max_residual:.2e} t={elapsed:.1f}s "
              f"n_conv_modes={n_converged_modes} lambda1={lambda1_str}")

    valid_pairs = [(i, e) for i, e in enumerate(low_eigs_seq) if e is not None]
    valid_eigs = [e for _, e in valid_pairs]
    rel_changes = relative_changes_scaled(valid_eigs) if len(valid_eigs) >= 2 else []
    converged = bool(len(rel_changes) > 0 and rel_changes[-1] < TOLERANCE and all(
        rel_changes[i + 1] <= rel_changes[i] * 1.5 for i in range(len(rel_changes) - 1)
    ))

    # eigenvector / subspace comparison between consecutive valid N (relies on the
    # nested-prefix property: D_small's points are exactly the first N_small rows
    # of D_large -- true only when neither N was restricted to a largest connected
    # component, since restriction can drop different points at different N and
    # breaks the row-correspondence).
    subspace_rows = []
    for j in range(len(valid_pairs) - 1):
        i_small, e_small = valid_pairs[j]
        i_large, e_large = valid_pairs[j + 1]
        if per_N[i_small].get("restricted_to_largest") or per_N[i_large].get("restricted_to_largest"):
            subspace_rows.append({"N_small": N_values[i_small], "N_large": N_values[i_large],
                                  "skipped": "one or both N restricted to largest connected "
                                             "component -- nested prefix correspondence broken"})
            continue
        n_small = N_values[i_small]
        vs, vl = eigvecs_seq[i_small], eigvecs_seq[i_large]
        comp = eigenvector_subspace_comparison(vs, vl, n_small, e_small, e_large)
        subspace_rows.append({"N_small": N_values[i_small], "N_large": N_values[i_large],
                              "clusters": comp})

    total_elapsed = time.time() - t0
    return {
        "label": label, "alpha": alpha, "N_ref": N_REF, "eps_ref": eps_ref, "seed": seed,
        "selection_rule": "nested prefixes of a single rng.permutation over the full point set",
        "epsilon_scaling_rule": "eps_N = eps_ref * (N_ref/N)^(1/(d+4)), d=3 -> exponent 1/7 "
                                 "(bias-variance-optimal rate; NOT the previous N^(-1/d) rate)",
        "asymptotic_condition_check": asymptotic_check,
        "per_N": per_N, "relative_changes": rel_changes, "converged": converged,
        "eigenvector_subspace_comparison": subspace_rows,
        "total_elapsed_seconds": total_elapsed,
    }


def make_uniform_box(N_max: int, box: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(0, box, size=(N_max, 3))


def make_nonuniform_clustered(N_max: int, box: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n_clumps = 12
    centers = rng.uniform(box * 0.15, box * 0.85, size=(n_clumps, 3))
    clump_id = rng.integers(0, n_clumps, size=N_max)
    pts = centers[clump_id] + rng.normal(scale=box * 0.06, size=(N_max, 3))
    return np.clip(pts, 0, box)


def main():
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    desi_pts = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                                    binned.canonical["Z"], cosmo)
    desi_w = binned.canonical["WEIGHT"]
    print(f"DESI pilot bin: {len(desi_pts)} objects available")

    box = 400.0
    uniform_pts = make_uniform_box(max(N_VALUES_SYNTH), box, SEED)
    clustered_pts = make_nonuniform_clustered(max(N_VALUES_SYNTH), box, SEED)

    all_results = {}
    for alpha in (0.0, 1.0):
        print(f"\n=== alpha={alpha}: uniform IID ===")
        all_results[f"uniform_alpha{alpha}"] = run_process(
            "uniform", uniform_pts, None, N_VALUES_SYNTH, alpha=alpha)

        print(f"\n=== alpha={alpha}: clustered non-IID ===")
        all_results[f"clustered_alpha{alpha}"] = run_process(
            "clustered", clustered_pts, None, N_VALUES_SYNTH, alpha=alpha)

        print(f"\n=== alpha={alpha}: DESI real ===")
        all_results[f"desi_alpha{alpha}"] = run_process(
            "desi", desi_pts, desi_w, N_VALUES_DESI, alpha=alpha)

    for name, res in all_results.items():
        print(f"{name}: converged={res['converged']} rel_changes={res['relative_changes']}")

    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "sparse_n_scaling_full_results.json"

    def _clean(o):
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.bool_):
            return bool(o)
        return o

    out_path.write_text(json.dumps(_clean(all_results), indent=2))
    print(f"\nwrote {out_path}")

    # ---- FC005_SPARSE_SPECTRAL_RESULTS.csv ----
    with open(ROOT / "reports/fc005/FC005_SPARSE_SPECTRAL_RESULTS.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "alpha", "N", "epsilon", "avg_degree", "nnz", "solver",
                    "sigma", "tol", "maxiter", "n_modes_requested", "max_residual",
                    "arpack_converged", "elapsed_seconds", "lambda_1", "lambda_2",
                    "relative_change_from_prev_N", "status"])
        for name, res in all_results.items():
            rel = res["relative_changes"]
            j = 0
            for row in res["per_N"]:
                if row["status"] != "OK":
                    w.writerow([name, res["alpha"], row["N"], "", "", "", "", "", "", "",
                                "", "", "", "", "", "", "", row["status"]])
                    continue
                fit = rel[j - 1] if 0 < j <= len(rel) else ""
                eig = row["low_eigenvalues"]
                w.writerow([name, res["alpha"], row["N"], f"{row['epsilon']:.5f}",
                            f"{row['avg_degree']:.2f}", row["nnz"], row["solver"],
                            row["sigma"], row["tol"], row["maxiter"], row["n_modes_requested"],
                            f"{row['max_residual']:.3e}", row["arpack_converged"],
                            f"{row['elapsed_seconds']:.2f}",
                            f"{eig[1]:.6e}" if len(eig) > 1 else "",
                            f"{eig[2]:.6e}" if len(eig) > 2 else "", fit, "OK"])
                j += 1
    print(f"wrote {ROOT / 'reports/fc005/FC005_SPARSE_SPECTRAL_RESULTS.csv'}")

    # ---- FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv ----
    with open(ROOT / "reports/fc005/FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "n_modes_compared", "relative_spectral_difference_alpha0_vs_alpha1",
                    "interpretation"])
        for label in ("uniform", "clustered", "desi"):
            r0 = all_results[f"{label}_alpha0.0"]
            r1 = all_results[f"{label}_alpha1.0"]
            eig0 = [row["low_eigenvalues"] for row in r0["per_N"] if row["status"] == "OK"]
            eig1 = [row["low_eigenvalues"] for row in r1["per_N"] if row["status"] == "OK"]
            if eig0 and eig1:
                comp = operator_identification(np.array(eig0[-1]), np.array(eig1[-1]))
                w.writerow([label, comp["n_modes_compared"],
                            f"{comp['relative_spectral_difference_alpha0_vs_alpha1']:.4f}",
                            comp["interpretation"]])
    print(f"wrote {ROOT / 'reports/fc005/FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv'}")

    # ---- FC005_POINT_PROCESS_COMPARISON.csv ----
    with open(ROOT / "reports/fc005/FC005_POINT_PROCESS_COMPARISON.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "alpha", "N_sequence", "epsilon_sequence",
                    "N_eps_pow_d_increasing", "N_eps_pow_d_plus_2_increasing",
                    "relative_changes", "converged", "final_relative_change"])
        for name, res in all_results.items():
            Ns = [r["N"] for r in res["per_N"] if r["status"] == "OK"]
            eps = [r["epsilon"] for r in res["per_N"] if r["status"] == "OK"]
            ac = res["asymptotic_condition_check"]
            w.writerow([name, res["alpha"], Ns, [round(e, 4) for e in eps],
                        ac[0]["N_eps_d_increasing_overall"] if ac else "",
                        ac[0]["N_eps_d_plus_2_increasing_overall"] if ac else "",
                        res["relative_changes"], res["converged"],
                        res["relative_changes"][-1] if res["relative_changes"] else ""])
    print(f"wrote {ROOT / 'reports/fc005/FC005_POINT_PROCESS_COMPARISON.csv'}")


if __name__ == "__main__":
    main()
