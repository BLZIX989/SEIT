#!/usr/bin/env python3
"""FC-005 checkpoint freeze: applies the spectral-validation rule
(compiler/backends/desi_sparse.py::joint_spectral_convergence) to the
ALREADY-COMPUTED sparse N-scaling results -- does NOT re-run any
eigensolves. Per instruction, the naive scalar eigenvalue-only
"converged" result (e.g. DESI's apparent 0.127 < 0.15) must not be
promoted into the canonical state; this script corrects the stored
"converged" field to the joint (eigenvalue+eigenvector) verdict,
preserving the original naive value under a new explicit field for
transparency, and regenerates the three summary CSVs from the corrected
data.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from compiler.backends.desi_sparse import joint_spectral_convergence

ROOT = Path(__file__).resolve().parent.parent
RESULTS_PATH = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "sparse_n_scaling_full_results.json"


def main():
    data = json.loads(RESULTS_PATH.read_text())

    for name, res in data.items():
        naive_converged = res["converged"]
        comparisons = res.get("eigenvector_subspace_comparison", [])
        final_clusters = None
        for entry in reversed(comparisons):
            if "clusters" in entry:
                final_clusters = entry["clusters"]
                break
        verdict = joint_spectral_convergence(final_clusters or [])
        res["eigenvalue_only_converged"] = naive_converged
        res["joint_spectral_converged"] = verdict["joint_converged"]
        res["joint_spectral_convergence_reason"] = verdict["reason"]
        # The canonical "converged" field is now the joint-validated one --
        # per instruction, the scalar-only result is never promoted into
        # the active canonical state on its own.
        res["converged"] = verdict["joint_converged"]
        flag = "" if naive_converged == verdict["joint_converged"] else "  <-- CORRECTED"
        print(f"{name}: eigenvalue_only={naive_converged} joint={verdict['joint_converged']}{flag}")
        print(f"    {verdict['reason']}")

    RESULTS_PATH.write_text(json.dumps(data, indent=2))
    print(f"\nrewrote {RESULTS_PATH} (converged field now = joint_spectral_converged)")

    # ---- Regenerate FC005_POINT_PROCESS_COMPARISON.csv ----
    with open(ROOT / "reports/fc005/FC005_POINT_PROCESS_COMPARISON.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "alpha", "N_sequence", "epsilon_sequence",
                    "N_eps_pow_d_increasing", "N_eps_pow_d_plus_2_increasing",
                    "relative_changes", "eigenvalue_only_converged",
                    "joint_spectral_converged", "converged", "final_relative_change"])
        for name, res in data.items():
            Ns = [r["N"] for r in res["per_N"] if r["status"] == "OK"]
            eps = [r["epsilon"] for r in res["per_N"] if r["status"] == "OK"]
            ac = res["asymptotic_condition_check"]
            w.writerow([name, res["alpha"], Ns, [round(e, 4) for e in eps],
                        ac[0]["N_eps_d_increasing_overall"] if ac else "",
                        ac[0]["N_eps_d_plus_2_increasing_overall"] if ac else "",
                        res["relative_changes"], res["eigenvalue_only_converged"],
                        res["joint_spectral_converged"], res["converged"],
                        res["relative_changes"][-1] if res["relative_changes"] else ""])
    print(f"wrote {ROOT / 'reports/fc005/FC005_POINT_PROCESS_COMPARISON.csv'}")

    # ---- Regenerate FC005_SPARSE_SPECTRAL_RESULTS.csv (unchanged data, same as before) ----
    with open(ROOT / "reports/fc005/FC005_SPARSE_SPECTRAL_RESULTS.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "alpha", "N", "epsilon", "avg_degree", "nnz", "solver",
                    "sigma", "tol", "maxiter", "n_modes_requested", "max_residual",
                    "arpack_converged", "elapsed_seconds", "lambda_1", "lambda_2",
                    "relative_change_from_prev_N", "status"])
        for name, res in data.items():
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


if __name__ == "__main__":
    main()
