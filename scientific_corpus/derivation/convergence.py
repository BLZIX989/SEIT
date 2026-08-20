"""CONV-001 -- Mosco-type convergence audit using the REAL graph sequence
already in this repository: the DESI sparse N-scaling data
(data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json,
N=4000->8000->16000->32000->64000), rather than a synthetic graph
sequence invented for this phase. This is the only place in the entire
corpus where an actual increasing-N graph sequence built from a fixed
underlying point set exists with recorded low-eigenvalue trajectories --
exactly the object Mosco convergence questions are about.

Full analytic Mosco-condition proof (M1 liminf, M2 recovery sequence) is
NOT attempted here: the fixed-Hilbert-space formulation does not apply
because H_n varies with n (different numbers of points), and the
corpus/compiler defines no identification/embedding map H_n -> H
anywhere -- so a rigorous M1/M2 check is NOT COMPUTABLE FROM AVAILABLE
DEFINITIONS (see missing_object below). What IS computed is the honest,
explicitly-labeled substitute the brief permits: numerical convergence
evidence on the quantities that ARE already recorded (lambda_1, lambda_2,
relative_change_from_prev_N), extended here with an explicit geometric-
decay-rate fit, which the existing FC005_N_SCALING_REPORT.md did not
perform.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESI_SPARSE_JSON = ROOT / "data" / "desi" / "dr1" / "fc005" / "derived" / "sparse_n_scaling_full_results.json"


def load_real_sequences() -> dict:
    if not DESI_SPARSE_JSON.exists():
        return {}
    return json.loads(DESI_SPARSE_JSON.read_text())


def _fit_geometric_decay_rate(relative_changes: list[float]) -> dict:
    """If relative_change_from_prev_N ~ C * r^k for successive refinements
    k=1,2,3,..., a convergent (Cauchy) sequence has r<1; fit r via the
    ratio of successive log|relative_change| values (a real, if crude,
    convergence-rate estimator -- not claimed to be a rigorous rate
    theorem)."""
    vals = [v for v in relative_changes if v is not None and v > 0]
    if len(vals) < 2:
        return {"fit_possible": False, "reason": "fewer than 2 nonzero relative-change points"}
    ratios = [vals[i + 1] / vals[i] for i in range(len(vals) - 1)]
    mean_ratio = sum(ratios) / len(ratios)
    monotone_decreasing = all(vals[i + 1] < vals[i] for i in range(len(vals) - 1))
    if mean_ratio < 1:
        verdict = "< 1 -- consistent with geometric convergence (Cauchy-like behavior)"
    else:
        verdict = ">= 1 -- NOT decaying, inconsistent with convergence at the N range tested"
    return {
        "fit_possible": True,
        "relative_change_sequence": vals,
        "successive_ratios": ratios,
        "mean_successive_ratio": mean_ratio,
        "monotone_decreasing": monotone_decreasing,
        "interpretation": f"mean successive ratio {mean_ratio:.3f} {verdict}",
    }


def audit_dataset(name: str, series: dict) -> dict:
    """series: one top-level entry of sparse_n_scaling_full_results.json,
    with real fields 'per_N' (list of per-N result dicts, each carrying
    'status' and 'low_eigenvalues') and 'relative_changes' (already
    precomputed by scripts/run_desi_sparse_n_scaling.py) -- read-only
    reuse, no recomputation of the spectra themselves (that would
    duplicate real, already-expensive ARPACK work for no new information)."""
    per_N = series.get("per_N", [])
    ok_records = [r for r in per_N if r.get("status") == "OK"]
    if not ok_records:
        return {
            "dataset": name, "status": "NO_CONVERGED_MODES_AT_ANY_N",
            "n_failed_of_total": f"{len(per_N) - len(ok_records)}/{len(per_N)}",
            "interpretation": (
                "ARPACK failed to produce converged low modes at every N tested "
                "(ARPACK_INSUFFICIENT_CONVERGED_MODES) -- this is a STRONGER form of "
                "non-convergence evidence than a slowly-decaying relative change: the "
                "solver could not even resolve stable low eigenmodes to compare across N, "
                "consistent with the existing CONTINUUM-LIMIT-L-DESI=FAIL finding for this "
                "class of geometry."
            ),
        }
    relative_changes = series.get("relative_changes", [])
    fit = _fit_geometric_decay_rate(relative_changes)
    lambda_1_seq = [r["low_eigenvalues"][1] for r in ok_records if len(r.get("low_eigenvalues", [])) > 1]
    lambda_2_seq = [r["low_eigenvalues"][2] for r in ok_records if len(r.get("low_eigenvalues", [])) > 2]
    return {
        "dataset": name,
        "N_values": [r["N"] for r in ok_records],
        "lambda_1_sequence": lambda_1_seq,
        "lambda_2_sequence": lambda_2_seq,
        "convergence_rate_fit": fit,
        "status": (
            "NUMERICAL_EVIDENCE_FOR_CONVERGENCE" if fit.get("fit_possible") and fit.get("monotone_decreasing")
            and fit.get("mean_successive_ratio", 1.0) < 0.9
            else "NUMERICAL_EVIDENCE_AGAINST_CONVERGENCE_AT_TESTED_N"
        ),
    }


def run_full_convergence_audit() -> dict:
    data = load_real_sequences()
    if not data:
        return {
            "status": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS",
            "missing_object": f"{DESI_SPARSE_JSON} not found in this checkout.",
        }
    results = {name: audit_dataset(name, series) for name, series in data.items()}
    mosco_note = {
        "rigorous_mosco_M1_M2_check": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS",
        "missing_object": (
            "A stated identification/embedding map iota_n: H_n -> H (or a common ambient "
            "Hilbert space with fixed inner product that all H_n, of varying dimension N, "
            "embed into) is required before the quadratic-form liminf/recovery-sequence "
            "conditions (M1/M2) are even well-posed questions. Neither the This-from-That "
            "whitepaper nor any compiler module (compiler/backends/desi_sparse.py, "
            "desi_graph.py, desi_fc005_pipeline.py) defines such a map -- each N is treated "
            "as an independent finite-dimensional problem with its own R^N, not as a term "
            "in a sequence embedded in a fixed limiting space. This is the exact, precise "
            "dependency gap the brief's section V asks to be identified rather than "
            "hand-waved past."
        ),
        "what_WAS_computed_instead": (
            "Numerical convergence/divergence evidence on the low-eigenvalue trajectories "
            "actually recorded for each real dataset (uniform/clustered/desi, "
            "alpha in {0.0, 1.0}) across the real N=4000->64000 sequence already run by "
            "scripts/run_desi_sparse_n_scaling.py -- see per-dataset results above."
        ),
    }
    return {"per_dataset_results": results, "mosco_condition_note": mosco_note}
