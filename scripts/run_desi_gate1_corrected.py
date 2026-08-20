#!/usr/bin/env python3
"""Re-runs Gate 1 with a corrected, mathematically-justified bandwidth
rule after the bandwidth/k sweep diagnostic (FC005_CONTINUUM_DIAGNOSTIC_
REPORT.md) found the original epsilon = 3 x median_NN heuristic produces
a near-complete graph (sparsity 34-65%, avg neighbors in the hundreds
out of a few thousand nodes) -- not a local graph appropriate for
approximating a differential operator.

Correction: epsilon = 1.0 x median_NN(N), the standard "median
heuristic" bandwidth (Gretton et al.; widely used in spectral
clustering/kernel methods), measured DIRECTLY within each subsample at
each N (never extrapolated from a single reference point -- this
removes the extrapolation-vs-direct-measurement question entirely).
This is a mathematically justified, established, pre-existing rule, not
tuned to this dataset to force a particular outcome.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compiler.backends.desi_diagnostics import median_nn_distance, _connected_components
from compiler.backends.desi_fc005_pipeline import (
    MathematicalConvergenceResult, RefinementPoint, _low_eigen,
)
from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, catalogue_to_points, comoving_distance,
    graph_laplacian_from_weights, normalize_continuum_limit,
)
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
Z_MIN, Z_MAX = 0.4, 0.6
N_VALUES = [800, 1500, 2500, 4000]
BANDWIDTH_MULTIPLIER = 1.0  # median heuristic; see module docstring
N_MODES = 60
SEED = 20250819


def run_corrected_convergence(ra, dec, z, weights, cosmo, N_values, *,
                               bandwidth_multiplier=1.0, n_modes=60, tolerance=0.15,
                               solver_tolerance=1e-6, seed=20250819) -> MathematicalConvergenceResult:
    pts_full = catalogue_to_points(ra, dec, z, cosmo)
    w_full = weights if weights is not None else np.ones(len(ra))
    rng = np.random.default_rng(seed)

    points_out = []
    epsilons_used = []
    for N in N_values:
        idx = rng.choice(len(pts_full), size=N, replace=False)
        pts, w = pts_full[idx], w_full[idx]
        eps = bandwidth_multiplier * median_nn_distance(pts)
        epsilons_used.append(eps)
        W = build_kernel_graph(pts, epsilon=eps, weights=w)
        n_components, _ = _connected_components(W)
        if n_components > 1:
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="OPERATOR-L-DESI",
                failure_reason=f"graph disconnected ({n_components} components) at N={N}, eps={eps:.2f}",
                points=points_out, relative_changes=[], tolerance=tolerance,
            ), epsilons_used
        _, L = graph_laplacian_from_weights(W)
        L_tilde = normalize_continuum_limit(L, N=N, epsilon=eps)
        low_vals, _, residual = _low_eigen(-L_tilde, n_modes)
        if residual > solver_tolerance:
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="DESI-SPECTRUM",
                failure_reason=f"eigensolver residual {residual:.3e} at N={N}",
                points=points_out, relative_changes=[], tolerance=tolerance,
            ), epsilons_used
        points_out.append(RefinementPoint(N=N, epsilon=eps, low_eigenvalues=low_vals.tolist(),
                                           solver_residual=residual))

    relative_changes = []
    for i in range(len(points_out) - 1):
        prev = np.array(points_out[i].low_eigenvalues)
        curr = np.array(points_out[i + 1].low_eigenvalues)
        denom = np.maximum(np.abs(prev), 1e-12)
        relative_changes.append(float(np.max(np.abs(curr - prev) / denom)))

    converged = bool(relative_changes[-1] < tolerance and all(
        relative_changes[i + 1] <= relative_changes[i] * 1.5 for i in range(len(relative_changes) - 1)
    ))
    return MathematicalConvergenceResult(
        converged=converged, failed_dependency=None if converged else "CONTINUUM-LIMIT-L-DESI",
        failure_reason="" if converged else
        f"relative change {relative_changes[-1]:.4f} did not fall below tolerance {tolerance} "
        f"even with corrected median-heuristic bandwidth",
        points=points_out, relative_changes=relative_changes, tolerance=tolerance,
    ), epsilons_used


def main():
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, Z_MIN, Z_MAX)
    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")

    result, epsilons = run_corrected_convergence(
        binned.canonical["RA"], binned.canonical["DEC"], binned.canonical["Z"],
        binned.canonical["WEIGHT"], cosmo, N_VALUES,
        bandwidth_multiplier=BANDWIDTH_MULTIPLIER, n_modes=N_MODES, seed=SEED,
    )
    print(f"epsilons used (median heuristic, mult={BANDWIDTH_MULTIPLIER}): "
          f"{[round(e,2) for e in epsilons]}")
    print(f"converged: {result.converged}")
    print(f"relative_changes: {result.relative_changes}")
    print(f"failed_dependency: {result.failed_dependency}")
    print(f"failure_reason: {result.failure_reason}")

    out = {
        "bandwidth_multiplier": BANDWIDTH_MULTIPLIER, "N_values": N_VALUES,
        "epsilons_used": epsilons, "n_modes": N_MODES,
        "converged": result.converged, "relative_changes": result.relative_changes,
        "failed_dependency": result.failed_dependency, "failure_reason": result.failure_reason,
        "points": [p.__dict__ for p in result.points],
    }
    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "gate1_corrected_run_result.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
