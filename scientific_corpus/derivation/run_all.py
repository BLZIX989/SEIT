"""Phase 14 (active derivation) orchestrator. Runs every real computation
in scientific_corpus/derivation/, then writes the 16 required deliverable
files at the repository root. Read-only against all canonical compiler
state; the only files this script writes are the ones listed in
REQUIRED_DELIVERABLES below plus scientific_corpus/derivation/DERIVATION_RESULTS.json
(the raw machine-readable dump everything else is generated from).
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import (  # noqa: E402
    categorical, convergence, dimensional_audit, dirac_candidates, gauge_rank,
    mass_spectrum, operator_algebra, simplicial,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_all() -> dict:
    # --- simplicial / Dirac squaring (TFT-001, TFT-002, TFT-002B) ---
    K_triangle = simplicial.SimplicialComplex(3, [(0, 1), (0, 2), (1, 2)], [(0, 1, 2)])
    K_tetra_boundary = simplicial.SimplicialComplex(
        4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
    )
    simplicial_results = {
        "filled_triangle": {
            "chain_complex_identity": simplicial.check_chain_complex_identity(K_triangle),
            "two_block_dirac_squaring_TFT-002": simplicial.check_two_block_dirac_squaring(K_triangle),
            "three_block_hodge_dirac_squaring_TFT-002B": simplicial.check_three_block_hodge_dirac_squaring(K_triangle),
        },
        "tetrahedron_boundary_S2": {
            "chain_complex_identity": simplicial.check_chain_complex_identity(K_tetra_boundary),
            "two_block_dirac_squaring_TFT-002": simplicial.check_two_block_dirac_squaring(K_tetra_boundary),
            "three_block_hodge_dirac_squaring_TFT-002B": simplicial.check_three_block_hodge_dirac_squaring(K_tetra_boundary),
        },
        "weitzenbock_curvature_term_TFT-003": simplicial.WEITZENBOCK_CURVATURE_TERM,
    }

    # --- Dirac locality (H2B) ---
    h2b = dirac_candidates.build_block_dirac_locality_test(n=200, k_neighbors=3)

    # --- mass spectrum ---
    mass_results = {
        "dimensional_analysis": mass_spectrum.dimensional_analysis(),
        "structural_test": mass_spectrum.structural_test(),
        "degrees_of_freedom_analysis": mass_spectrum.degrees_of_freedom_analysis(),
    }

    # --- gauge structure (H4B, H4C) ---
    gauge_results = {
        "su3_in_g2": gauge_rank.su3_in_g2_check(),
        "su2xu1_in_spin8": gauge_rank.su2xu1_in_spin8_check(),
        "missing_link_to_compiler_spectrum_H4C": gauge_rank.missing_link_to_compiler_spectrum(),
    }

    # --- convergence (CONV-001) ---
    conv_results = convergence.run_full_convergence_audit()

    # --- operator algebra ---
    op_algebra_results = {
        "clifford_algebra": operator_algebra.clifford_algebra_check(),
        "su2_jacobi_identity": operator_algebra.su2_jacobi_identity_check(),
        "gauge_covariant_derivative_dimensions": operator_algebra.gauge_covariant_derivative_dimensional_check(),
    }

    # --- categorical / translation audit ---
    categorical_results = {
        "faithful_edge_preservation": categorical.check_faithful_edge_preservation(),
        "composability": categorical.check_composability(),
    }

    # --- dimensional audit ---
    dim_audit = dimensional_audit.run_audit()

    return {
        "run_timestamp": _now_iso(),
        "simplicial_dirac": simplicial_results,
        "h2b_block_dirac_locality": h2b,
        "mass_spectrum": mass_results,
        "gauge_structure": gauge_results,
        "convergence": conv_results,
        "operator_algebra": op_algebra_results,
        "categorical": categorical_results,
        "dimensional_audit": dim_audit,
    }


def _git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                               text=True, check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def _hash_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


if __name__ == "__main__":
    results = run_all()
    out_dir = ROOT / "scientific_corpus" / "derivation"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "DERIVATION_RESULTS.json").write_text(json.dumps(results, indent=2, default=str))
    print("Wrote scientific_corpus/derivation/DERIVATION_RESULTS.json")
    print(f"git_commit={_git_commit()}")
    print(f"result_hash={_hash_json(results)}")
