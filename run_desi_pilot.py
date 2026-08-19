#!/usr/bin/env python3
"""FC-005 pilot: D_DESI -> G_DESI -> L_DESI on a real, documented subset
of the downloaded DESI DR1 LRG SGC catalog. Per spec section 13/14 of
the data-acquisition build command: this tests graph construction only
-- no curvature/cosmological closure is claimed here.

Writes:
  data/desi/dr1/fc005/validated/pilot_fixture/  (committed, small)
  data/desi/dr1/fc005/derived/pilot_run_result.json  (gitignored, derived)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.table import Table

from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, graph_laplacian_from_weights, radec_to_cartesian,
)
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
FIXTURE_DIR = ROOT / "data" / "desi" / "dr1" / "fc005" / "validated" / "pilot_fixture"
DERIVED_DIR = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived"

PILOT_Z_MIN, PILOT_Z_MAX = 0.4, 0.6
PILOT_N = 3000
SEED = 20250819


def count_connected_components(W: np.ndarray) -> tuple[int, np.ndarray]:
    n = W.shape[0]
    labels = -np.ones(n, dtype=int)
    comp = 0
    for start in range(n):
        if labels[start] != -1:
            continue
        stack = [start]
        labels[start] = comp
        while stack:
            i = stack.pop()
            neighbors = np.nonzero(W[i] > 0)[0]
            for j in neighbors:
                if labels[j] == -1:
                    labels[j] = comp
                    stack.append(j)
        comp += 1
    return comp, labels


def main() -> dict:
    manifest = json.loads((ROOT / "FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")

    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, PILOT_Z_MIN, PILOT_Z_MAX)
    print(f"D_DESI full: {table.n_rows} rows; bin [{PILOT_Z_MIN},{PILOT_Z_MAX}): {binned.n_rows} rows")

    rng = np.random.default_rng(SEED)
    idx = rng.choice(binned.n_rows, size=min(PILOT_N, binned.n_rows), replace=False)
    idx.sort()
    pilot = {k: v[idx] for k, v in binned.canonical.items()}
    n = len(idx)
    print(f"pilot subsample: {n} objects (seed={SEED})")

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    fixture_table = Table({k: v for k, v in pilot.items()})
    fixture_path = FIXTURE_DIR / "lrg_sgc_pilot_3000_z0.4-0.6.fits"
    fixture_table.write(fixture_path, overwrite=True)
    print(f"wrote pilot fixture: {fixture_path} ({fixture_path.stat().st_size} bytes)")

    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")
    from compiler.backends.desi_graph import comoving_distance
    chi = comoving_distance(pilot["Z"], cosmo)
    points = radec_to_cartesian(pilot["RA"], pilot["DEC"], chi)

    # epsilon chosen from the data itself (median nearest-neighbor comoving
    # separation x 3), not an arbitrary constant -- recorded explicitly.
    from scipy.spatial import cKDTree
    tree = cKDTree(points)
    nn_dist, _ = tree.query(points, k=2)  # k=1 is self (dist 0)
    median_nn = float(np.median(nn_dist[:, 1]))
    epsilon = 3.0 * median_nn
    print(f"median nearest-neighbor comoving separation: {median_nn:.3f} Mpc; epsilon = {epsilon:.3f} Mpc")

    W = build_kernel_graph(points, epsilon=epsilon, weights=pilot["WEIGHT"])
    D, L = graph_laplacian_from_weights(W)

    checks = {}
    checks["n_nodes"] = n
    checks["n_edges_nonzero_entries"] = int(np.sum(W > 1e-12)) // 2  # undirected, exclude diagonal
    checks["W_symmetric"] = bool(np.allclose(W, W.T, atol=1e-12))
    checks["W_nonnegative"] = bool(np.all(W >= 0))
    checks["W_diagonal_zero"] = bool(np.allclose(np.diagonal(W), 0.0))
    degree = W.sum(axis=1)
    checks["degree_distribution"] = {
        "min": float(degree.min()), "max": float(degree.max()),
        "mean": float(degree.mean()), "median": float(np.median(degree)),
    }
    checks["sparsity_fraction_nonzero"] = float(np.mean(W > 1e-12))

    checks["L_symmetric"] = bool(np.allclose(L, L.T, atol=1e-10))
    rng2 = np.random.default_rng(SEED + 1)
    vtLv_min = min(float(v @ L @ v) for v in (rng2.normal(size=n) for _ in range(200)))
    checks["v_T_L_v_nonnegative_over_200_random_vectors"] = bool(vtLv_min >= -1e-6)
    checks["v_T_L_v_min_observed"] = vtLv_min

    n_components, labels = count_connected_components(W)
    eigvals = np.linalg.eigvalsh(L)
    n_zero_modes = int(np.sum(np.abs(eigvals) < 1e-8))
    checks["n_connected_components"] = n_components
    checks["n_zero_eigenvalues"] = n_zero_modes
    checks["zero_mode_matches_connected_components"] = (n_components == n_zero_modes)
    checks["row_sum_max_abs"] = float(np.max(np.abs(L.sum(axis=1))))

    result = {
        "stage": "D_DESI -> G_DESI -> L_DESI pilot (spec section 13-14)",
        "not_a_closure_claim": True,
        "source_file": str(RAW), "source_url": primary["url"],
        "checksum_sha256": primary["checksum_sha256"],
        "redshift_bin": [PILOT_Z_MIN, PILOT_Z_MAX],
        "n_objects_in_bin_full": binned.n_rows,
        "pilot_subsample_size": n, "pilot_seed": SEED,
        "cosmology_source": "FC005_cosmology.yaml",
        "epsilon_mpc": epsilon, "epsilon_rule": "3 x median nearest-neighbor comoving separation",
        "checks": checks,
        "fixture_path": str(fixture_path.relative_to(ROOT)),
    }

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    (DERIVED_DIR / "pilot_run_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(checks, indent=2))
    return result


if __name__ == "__main__":
    main()
