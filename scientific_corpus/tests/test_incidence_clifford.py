"""Tests for the incidence/Clifford/persistence follow-up
(scientific_corpus/derivation/persistence.py, ko_dimension.py,
clifford_derivation.py, kc003_vr001.py). Real computation against real
compiler backends and a known-answer manifold control -- no mocks for the
objects under test.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import clifford_derivation, kc003_vr001, ko_dimension, persistence


# --- persistence -----------------------------------------------------------

def test_persistence_projection_is_idempotent_and_self_adjoint():
    r = persistence.persistent_sector_report(topology="cycle", n=30, lambda_c_fractions=(0.3,))
    for v in r["by_lambda_c"].values():
        assert v["P_idempotent"] is True
        assert v["P_self_adjoint"] is True
        assert v["L_Pi_equals_P_L_P_reconstruction"] is True


def test_persistence_heat_trace_monotone_nonincreasing():
    r = persistence.persistent_sector_report(topology="path", n=30, lambda_c_fractions=(0.5,))
    for v in r["by_lambda_c"].values():
        assert v["K_Pi_monotone_nonincreasing_in_beta"] is True


def test_persistent_distance_beta_zero_limit_and_monotonicity():
    r = persistence.persistent_distance_beta_limits_check(topology="cycle", n=20)
    assert r["beta_near_0_matches_unweighted_persistent_distance"] is True
    assert r["monotone_nonincreasing_in_beta"] is True


# --- KO dimension / intersection form --------------------------------------

def test_odd_skew_symmetric_determinant_always_zero_symbolic():
    r = ko_dimension.skew_symmetric_odd_determinant_check(n_values=(3, 5))
    assert r["all_odd_n_confirm_identically_zero"] is True


def test_even_skew_symmetric_determinant_not_forced_zero():
    """Negative control: EVEN-dimensional skew-symmetric matrices are NOT
    forced to have zero determinant (the (-1)^n=+1 case) -- proves the
    odd-n mechanism is specific to odd n, not a universal property of all
    skew-symmetric matrices."""
    A = sp.Matrix([[0, 1], [-1, 0]])
    assert A.T == -A
    assert A.det() == 1  # nonzero for n=2


def test_symmetric_3x3_example_has_nonzero_determinant():
    r = ko_dimension.symmetric_3x3_nonzero_determinant_example()
    assert r["nonzero"] is True
    assert r["determinant"] != 0


def test_ko_parameter_scan_covers_0_2_4_6():
    rows = ko_dimension.ko_dimension_parameter_scan()
    ko_values = {row["KO_mod_8"] for row in rows}
    assert {0, 2, 4, 6} <= ko_values
    by_ko = {row["KO_mod_8"]: row for row in rows}
    assert by_ko[6]["odd_dim_determinant_forced_zero"] is True
    assert by_ko[0]["odd_dim_determinant_forced_zero"] is False
    assert by_ko[4]["odd_dim_determinant_forced_zero"] is False


# --- Clifford rank ------------------------------------------------------

def test_clifford_rank_not_forced_by_project_construction():
    r = clifford_derivation.clifford_rank_forcing_check()
    assert r["status"].startswith("NOT COMPUTABLE")


def test_spin6_su4_dim_rank_consistent():
    r = ko_dimension.spin6_su4_isomorphism_check()
    assert r["dim_match"] is True
    assert r["rank_match"] is True


# --- KC-003 / VR-001 --------------------------------------------------------

def test_kc003_has_all_four_subclaims_independently_tracked():
    r = kc003_vr001.kc003_decomposition()
    assert set(r.keys()) == {
        "KC-003a_measure_convergence", "KC-003b_operator_convergence",
        "KC-003c_spectral_convergence", "KC-003d_geometric_convergence",
    }


def test_vr001_uniform_sampling_converges_on_known_manifold():
    r = kc003_vr001.vr001_known_manifold_control(n_values=(200, 500))
    for res in r["results"]["uniform"].values():
        assert res["converged_close_to_1"] is True


def test_vr001_nonuniform_sampling_does_not_converge_same_construction():
    """This is the real, load-bearing negative control: the SAME test on
    the SAME manifold with density-biased sampling must NOT spuriously
    pass -- proves vr001_known_manifold_control can actually detect
    failure, not just always report success."""
    r = kc003_vr001.vr001_known_manifold_control(n_values=(200, 500))
    failures = [res["converged_close_to_1"] for res in r["results"]["nonuniform"].values()]
    assert not all(failures), "expected at least one nonuniform-sampling case to fail to converge"


# --- canonical isolation ----------------------------------------------------

CANONICAL_FILES = [
    "equation_registry.json", "object_registry.json", "transformation_registry.json",
    "master_mdcl.json", "chainlink_registry.json", "protocol_registry.json",
]


def test_run_incidence_clifford_never_touches_canonical_registries():
    before = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    subprocess.run([sys.executable, str(ROOT / "scientific_corpus" / "derivation" / "run_incidence_clifford.py")],
                    cwd=ROOT, check=True, capture_output=True, timeout=120)
    after = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES if (ROOT / f).exists()}
    assert before == after, "run_incidence_clifford.py modified a canonical registry file"
