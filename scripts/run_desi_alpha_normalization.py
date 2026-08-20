#!/usr/bin/env python3
"""FC-005 diagnostic: tests the Coifman-Lafon alpha-normalized ("density
normalized") graph Laplacian as a STANDARD, PRE-EXISTING, mathematically
justified correction for sampling-density nonuniformity.

Motivation (from FC005_CONTINUUM_FAILURE_MATRIX.csv / diagnostic_full_
results.json, this investigation): the "nonuniform clustered" synthetic
control reproduced a failure of the same character as real DESI (large,
non-improving relative changes across N), while a uniform-density control
was merely borderline and a matched radial-selection-only control
CONVERGED. This isolates density nonuniformity (not boundary, not the
1D radial selection function) as the leading candidate mechanism.

The standard construction for removing density-dependence from the graph
Laplacian limit (Coifman & Lafon 2006, "Diffusion maps"; Singer 2006,
"From graph to manifold Laplacian conversion"; Hein, Audibert & von
Luxburg 2007) is:

    W_ij            = exp(-d_ij^2 / eps^2)              (raw kernel)
    D_i              = sum_j W_ij                         (raw degree)
    W'_ij            = W_ij / (D_i^alpha * D_j^alpha)      (density normalization)
    D'_i             = sum_j W'_ij
    L_alpha          = D' - W'                             (renormalized graph Laplacian)

With alpha=1, the density dependence in the generator's limit cancels to
leading order and L_alpha converges (under the same N->infinity, eps->0
regime as the unnormalized construction) to a PURE Laplace-Beltrami
operator, independent of the sampling density p(x) -- whereas the
unnormalized (alpha=0) construction converges instead to a density-
weighted operator Delta + 2*(1-alpha)*grad(log p).grad, which can behave
very differently at finite N when p(x) is strongly nonuniform (as in our
clustered control, and as in true galaxy large-scale structure).

This is NOT an invented formula -- it is the standard, published
correction for exactly this situation, applied here without modification.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compiler.backends.desi_diagnostics import _connected_components, median_nn_distance
from compiler.backends.desi_fc005_pipeline import _low_eigen
from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, catalogue_to_points, gaussian_kernel_C_K,
)
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi
from run_desi_diagnostics import (
    N_VALUES, SEED, TOLERANCE, make_nonuniform_clustered, make_uniform_box,
    relative_changes_fixed,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"


def alpha_normalize(W: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    D = W.sum(axis=1)
    D_safe = np.maximum(D, 1e-300)
    scale = D_safe ** (-alpha)
    return W * scale[:, None] * scale[None, :]


def run_sequence_alpha(points_source, weights_source, N_values, *, exponent: float,
                        alpha: float, bandwidth_mult: float = 1.0, n_modes: int = 40,
                        nested: bool = True, seed: int = SEED) -> dict:
    rows = []
    low_eigs = []
    rng = np.random.default_rng(seed)

    if nested:
        pts_max, w_max = points_source, weights_source
        idx_order = rng.permutation(len(pts_max))

    C_K = gaussian_kernel_C_K(3)

    for N in N_values:
        if nested:
            idx = idx_order[:N]
            pts = pts_max[idx]
            w = w_max[idx] if w_max is not None else None
        else:
            pts, w = points_source(N, rng)

        eps = bandwidth_mult * median_nn_distance(pts)
        W_raw = build_kernel_graph(pts, epsilon=eps, weights=w)
        W = alpha_normalize(W_raw, alpha=alpha) if alpha > 0 else W_raw

        n_comp, _ = _connected_components(W)
        row = {"N": N, "epsilon": eps, "connected": n_comp == 1}
        if n_comp != 1:
            row["status"] = "DISCONNECTED"
            rows.append(row)
            low_eigs.append(None)
            continue

        D = np.diag(W.sum(axis=1))
        L = D - W
        L_tilde = -L / (C_K * N * eps ** exponent)
        low_vals, _, residual = _low_eigen(-L_tilde, n_modes)
        row["solver_residual"] = residual
        row["status"] = "OK"
        rows.append(row)
        low_eigs.append(low_vals)

    valid_eigs = [e for e in low_eigs if e is not None]
    rel_changes = relative_changes_fixed(valid_eigs) if len(valid_eigs) >= 2 else []
    converged = bool(len(rel_changes) > 0 and rel_changes[-1] < TOLERANCE and all(
        rel_changes[i + 1] <= rel_changes[i] * 1.5 for i in range(len(rel_changes) - 1)
    ))
    return {"rows": rows, "relative_changes": rel_changes, "converged": converged,
            "alpha": alpha, "exponent": exponent}


def main():
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    desi_pts = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                                    binned.canonical["Z"], cosmo)
    desi_w = binned.canonical["WEIGHT"]

    N_max = max(N_VALUES)
    box = 200.0
    uniform_pts = make_uniform_box(N_max, box, SEED)
    clustered_pts = make_nonuniform_clustered(N_max, box, SEED)

    all_results = {}
    for alpha in (0.0, 1.0):
        label = f"alpha={alpha}"
        print(f"=== {label}: DESI real ===")
        r = run_sequence_alpha(desi_pts, desi_w, N_VALUES, exponent=5.0, alpha=alpha)
        all_results[f"desi_{label}"] = r
        print(f"  converged={r['converged']} rel_changes={r['relative_changes']}")

        print(f"=== {label}: uniform box ===")
        r = run_sequence_alpha(uniform_pts, None, N_VALUES, exponent=5.0, alpha=alpha)
        all_results[f"uniform_{label}"] = r
        print(f"  converged={r['converged']} rel_changes={r['relative_changes']}")

        print(f"=== {label}: nonuniform clustered ===")
        r = run_sequence_alpha(clustered_pts, None, N_VALUES, exponent=5.0, alpha=alpha)
        all_results[f"clustered_{label}"] = r
        print(f"  converged={r['converged']} rel_changes={r['relative_changes']}")

    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "alpha_normalization_results.json"

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


if __name__ == "__main__":
    main()
