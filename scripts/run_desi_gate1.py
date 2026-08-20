#!/usr/bin/env python3
"""FC-005 Gate 1 execution on REAL, validated DESI DR1 data: the
mathematical-convergence stage of compiler/backends/desi_fc005_pipeline.py,
run on the LRG SGC catalog (0.4 <= z < 0.6 bin). Per instruction: proceed
automatically through Gate 1; enter Gate 2 only if Gate 1 passes; Gate 3
only with an explicitly attributed, independently-sourced kappa_cosmological.

epsilon(N) is derived from the data (median nearest-neighbor separation
at a reference N, scaled by the standard 3D volume law N^(-1/3) for the
other N values) -- not an arbitrary constant. This is a reasonable, but
not claimed-optimal, refinement rule; see the printed/recorded caveat.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from compiler.backends.desi_fc005_pipeline import run_fc005_desi_pipeline
from compiler.backends.desi_graph import CosmologyModel, catalogue_to_points
from compiler.backends.desi_schema import apply_redshift_cut, load_d_desi

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw" / "LRG_SGC_clustering.dat.fits"
Z_MIN, Z_MAX = 0.4, 0.6
N_VALUES = [800, 1500, 2500, 4000]
REF_N = 3000
REF_EPSILON = 150.337  # Mpc; 3 x median NN separation at N=3000, from run_desi_pilot.py's pilot run
SEED = 20250819


def epsilon_for_n(n: int) -> float:
    # standard 3D volume-density scaling: typical nearest-neighbor spacing
    # ~ (V/N)^(1/3), so a fixed multiple of it scales as N^(-1/3) at fixed volume
    return REF_EPSILON * (REF_N / n) ** (1.0 / 3.0)


def main() -> dict:
    manifest = json.loads((ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json").read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")

    table = load_d_desi(RAW, source_url=primary["url"], checksum_sha256=primary["checksum_sha256"])
    binned = apply_redshift_cut(table, Z_MIN, Z_MAX)
    print(f"D_DESI bin [{Z_MIN},{Z_MAX}): {binned.n_rows} real objects available")

    epsilon_values = [epsilon_for_n(n) for n in N_VALUES]
    for n, eps in zip(N_VALUES, epsilon_values):
        print(f"  N={n}: epsilon={eps:.3f} Mpc (data-derived, N^-1/3 scaling from reference)")

    cosmo = CosmologyModel.from_yaml(ROOT / "FC005_cosmology.yaml")

    result = run_fc005_desi_pipeline(
        binned.canonical["RA"], binned.canonical["DEC"], binned.canonical["Z"],
        binned.canonical["WEIGHT"], cosmo,
        N_values=N_VALUES, epsilon_values=epsilon_values,
        kappa_cosmological=None,  # Gate 3 requires an explicitly attributed, independent value -- none supplied here
        convergence_tolerance=0.15,
    )

    out = {
        "stage": "Gate 1 (mathematical convergence) executed on real DESI DR1 LRG SGC data",
        "redshift_bin": [Z_MIN, Z_MAX], "n_objects_in_bin": binned.n_rows,
        "N_values": N_VALUES, "epsilon_values": epsilon_values,
        "epsilon_rule": "3 x median NN separation at N=3000 (measured), scaled by (3000/N)^(1/3) "
                        "for other N -- a standard but not claimed-optimal 3D volume-density scaling",
        "result": result.to_dict(),
    }
    out_path = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "gate1_run_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {out_path}")
    print(f"\nstopped_at: {result.stopped_at}")
    print(f"summary: {result.summary}")
    return out


if __name__ == "__main__":
    main()
