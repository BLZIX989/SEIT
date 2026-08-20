#!/usr/bin/env python3
"""FC-005 continuum-limit failure diagnostic investigation. Runs the
real DESI catalog and a matched set of synthetic controls through the
IDENTICAL pipeline (same bandwidth rule, same normalization, same
relative-change metric) so any difference in convergence behavior is
attributable to a genuine property of the DESI point process, not to a
different measurement procedure.

Writes FC005_CONTINUUM_FAILURE_MATRIX.csv and
data/desi/dr1/fc005/derived/diagnostic_full_results.json.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from compiler.backends.desi_diagnostics import (
    _connected_components, audit_graph, bandwidth_sweep, local_density_variation,
    median_nn_distance,
)
from compiler.backends.desi_fc005_pipeline import _low_eigen
from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, catalogue_to_points, gaussian_kernel_C_K,
    graph_laplacian_from_weights,
)
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
N_VALUES = [800, 1500, 2500, 4000]
BANDWIDTH_MULT = 1.0
N_MODES = 40
SEED = 20250819
TOLERANCE = 0.15


def normalize_L_tilde(L_N: np.ndarray, N: int, epsilon: float, *, d: int = 3,
                       exponent: float, C_K: float | None = None) -> np.ndarray:
    """Generalized normalization so both the ORIGINAL exponent (d/2+1, as
    literally taken from the workbook's eps^(5/2) without the units
    conversion) and the CORRECTED exponent (d+2, after translating the
    workbook's length^2-unit epsilon to this code's length-unit epsilon --
    see FC005_CONTINUUM_DIAGNOSTIC_REPORT.md) can be compared directly."""
    if C_K is None:
        C_K = gaussian_kernel_C_K(d)
    return -L_N / (C_K * N * epsilon ** exponent)


def relative_changes_fixed(points_low_eigs: list[np.ndarray]) -> list[float]:
    """The corrected metric: excludes the zero mode, uses a floor relative
    to this run's own eigenvalue scale (never a fixed absolute constant --
    see the bug this fixes in FC005_CONTINUUM_DIAGNOSTIC_REPORT.md)."""
    out = []
    for i in range(len(points_low_eigs) - 1):
        prev, curr = points_low_eigs[i][1:], points_low_eigs[i + 1][1:]
        scale = float(np.mean(np.abs(prev))) if len(prev) else 1e-12
        floor = max(scale * 1e-6, 1e-300)
        denom = np.maximum(np.abs(prev), floor)
        out.append(float(np.max(np.abs(curr - prev) / denom)))
    return out


def run_sequence(points_source, weights_source, N_values, *, exponent: float,
                  bandwidth_mult: float = BANDWIDTH_MULT, n_modes: int = N_MODES,
                  nested: bool = True, seed: int = SEED) -> dict:
    """points_source: either a fixed (N_max, 3) array (nested subsampling)
    or a callable N -> points (fresh draw per N, non-nested)."""
    rows = []
    low_eigs = []
    rng = np.random.default_rng(seed)

    if nested:
        pts_max = points_source
        w_max = weights_source
        idx_order = rng.permutation(len(pts_max))

    for N in N_values:
        if nested:
            idx = idx_order[:N]
            pts = pts_max[idx]
            w = w_max[idx] if w_max is not None else None
        else:
            pts, w = points_source(N, rng)

        eps = bandwidth_mult * median_nn_distance(pts)
        W = build_kernel_graph(pts, epsilon=eps, weights=w)
        audit = audit_graph(pts, W, seed=seed)
        n_comp = audit.n_connected_components

        row = {"N": N, "epsilon": eps, "connected": n_comp == 1,
               "n_connected_components": n_comp,
               "largest_component_fraction": audit.largest_component_fraction,
               "avg_neighbors": audit.avg_neighbors_above_threshold,
               "sparsity": audit.sparsity_fraction_nonzero,
               "degree_median": audit.degree_median}

        if n_comp != 1:
            row["status"] = "DISCONNECTED"
            rows.append(row)
            low_eigs.append(None)
            continue

        _, L = graph_laplacian_from_weights(W)
        L_tilde = normalize_L_tilde(L, N=N, epsilon=eps, exponent=exponent)
        low_vals, _, residual = _low_eigen(-L_tilde, n_modes)
        row["solver_residual"] = residual
        row["spectral_gap"] = float(low_vals[1]) if len(low_vals) > 1 else float("nan")
        row["status"] = "OK"
        rows.append(row)
        low_eigs.append(low_vals)

    valid_eigs = [e for e in low_eigs if e is not None]
    rel_changes = relative_changes_fixed(valid_eigs) if len(valid_eigs) >= 2 else []
    converged = bool(len(rel_changes) > 0 and rel_changes[-1] < TOLERANCE and all(
        rel_changes[i + 1] <= rel_changes[i] * 1.5 for i in range(len(rel_changes) - 1)
    ))

    return {"rows": rows, "relative_changes": rel_changes, "converged": converged,
            "exponent": exponent, "bandwidth_mult": bandwidth_mult, "nested": nested}


def make_uniform_box(N_max: int, box: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(0, box, size=(N_max, 3))


def make_nonuniform_clustered(N_max: int, box: float, seed: int) -> np.ndarray:
    """Points drawn from a mixture of Gaussian clumps within the box --
    mimics large-scale-structure clustering (galaxies are NOT a Poisson
    process; they cluster)."""
    rng = np.random.default_rng(seed)
    n_clumps = 12
    centers = rng.uniform(box * 0.15, box * 0.85, size=(n_clumps, 3))
    clump_id = rng.integers(0, n_clumps, size=N_max)
    pts = centers[clump_id] + rng.normal(scale=box * 0.06, size=(N_max, 3))
    return np.clip(pts, 0, box)


def make_masked_box(N_max: int, box: float, seed: int) -> np.ndarray:
    """Uniform points with a wedge removed -- mimics a hard survey-mask
    boundary cutting through the volume."""
    rng = np.random.default_rng(seed)
    pts = []
    batch = N_max * 3
    while sum(len(p) for p in pts) < N_max:
        cand = rng.uniform(0, box, size=(batch, 3))
        angle = np.arctan2(cand[:, 1] - box / 2, cand[:, 0] - box / 2)
        keep = angle > -2.0  # remove a wedge of the angular range
        pts.append(cand[keep])
    return np.concatenate(pts)[:N_max]


def make_desi_like_radial_selection(N_max: int, box: float, seed: int, z_like_profile) -> np.ndarray:
    """Uniform in angle, but with a radial (redshift-like) selection
    function matching DESI's own observed N(z) shape in the pilot bin --
    tests whether the RADIAL SELECTION FUNCTION alone (independent of true
    clustering) can reproduce the DESI failure mode."""
    rng = np.random.default_rng(seed)
    r = rng.choice(z_like_profile, size=N_max, replace=True) * box
    theta = np.arccos(rng.uniform(-1, 1, size=N_max))
    phi = rng.uniform(0, 2 * np.pi, size=N_max)
    x = r * np.sin(theta) * np.cos(phi) + box
    y = r * np.sin(theta) * np.sin(phi) + box
    z = r * np.cos(theta) + box
    return np.stack([x, y, z], axis=1)


def main():
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, 0.4, 0.6)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    desi_pts = catalogue_to_points(binned.canonical["RA"], binned.canonical["DEC"],
                                    binned.canonical["Z"], cosmo)
    desi_w = binned.canonical["WEIGHT"]

    all_results = {}

    print("=== DESI, exponent=5/2 (original) ===")
    all_results["desi_original_exponent"] = run_sequence(desi_pts, desi_w, N_VALUES, exponent=2.5)
    print(f"  converged={all_results['desi_original_exponent']['converged']} "
          f"rel_changes={all_results['desi_original_exponent']['relative_changes']}")

    print("=== DESI, exponent=5 (corrected) ===")
    all_results["desi_corrected_exponent"] = run_sequence(desi_pts, desi_w, N_VALUES, exponent=5.0)
    print(f"  converged={all_results['desi_corrected_exponent']['converged']} "
          f"rel_changes={all_results['desi_corrected_exponent']['relative_changes']}")

    N_max = max(N_VALUES)
    box = 200.0

    print("=== Synthetic: uniform Euclidean box ===")
    uniform_pts = make_uniform_box(N_max, box, SEED)
    all_results["synthetic_uniform_box"] = run_sequence(uniform_pts, None, N_VALUES, exponent=5.0)
    print(f"  converged={all_results['synthetic_uniform_box']['converged']} "
          f"rel_changes={all_results['synthetic_uniform_box']['relative_changes']}")

    print("=== Synthetic: nonuniform (clustered) ===")
    clustered_pts = make_nonuniform_clustered(N_max, box, SEED)
    all_results["synthetic_clustered"] = run_sequence(clustered_pts, None, N_VALUES, exponent=5.0)
    print(f"  converged={all_results['synthetic_clustered']['converged']} "
          f"rel_changes={all_results['synthetic_clustered']['relative_changes']}")

    print("=== Synthetic: masked (wedge removed) ===")
    masked_pts = make_masked_box(N_max, box, SEED)
    all_results["synthetic_masked"] = run_sequence(masked_pts, None, N_VALUES, exponent=5.0)
    print(f"  converged={all_results['synthetic_masked']['converged']} "
          f"rel_changes={all_results['synthetic_masked']['relative_changes']}")

    print("=== Synthetic: DESI-like radial selection ===")
    z = binned.canonical["Z"]
    radial_pts = make_desi_like_radial_selection(N_max, box, SEED, z)
    all_results["synthetic_desi_radial_selection"] = run_sequence(radial_pts, None, N_VALUES, exponent=5.0)
    print(f"  converged={all_results['synthetic_desi_radial_selection']['converged']} "
          f"rel_changes={all_results['synthetic_desi_radial_selection']['relative_changes']}")

    # ---- Write CSV matrix ----
    csv_path = ROOT / "reports/fc005/FC005_CONTINUUM_FAILURE_MATRIX.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "exponent", "N", "epsilon", "k_or_bandwidth_mult", "connected",
                         "spectral_residual", "operator_residual", "fit_stability",
                         "boundary_fraction", "density_variation", "status"])
        for name, res in all_results.items():
            for i, row in enumerate(res["rows"]):
                fit_stability = (res["relative_changes"][i - 1] if 0 < i <= len(res["relative_changes"])
                                 else "")
                writer.writerow([
                    name, res["exponent"], row["N"], f"{row['epsilon']:.4f}", res["bandwidth_mult"],
                    row["connected"], row.get("solver_residual", ""), "",
                    fit_stability, "", row.get("sparsity", ""), row["status"],
                ])
    print(f"\nwrote {csv_path}")

    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "diagnostic_full_results.json"

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
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
