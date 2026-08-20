"""Tests for seit_lang.ncg_branch (Phase 9)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import ko_dimension

from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.ncg_branch import (
    NCG_BRANCH_BINDINGS,
    NCG_BRANCH_TRANSFORMATIONS,
    construct_intersection_matrix,
    intersection_matrix_report,
    ko_dimension_scan_row,
    spin6_su4_check,
)
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program


# --- KO=6 as a falsification/audit branch when forced -----------------

def test_ko6_odd_n_forces_determinant_zero():
    report = intersection_matrix_report(6, 7, seed=1)
    assert report["intersection_form_symmetry"] == "ANTISYMMETRIC"
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is True
    assert report["determinant"] == pytest.approx(0.0, abs=1e-8)
    assert report["audit_flag"] is not None
    assert "obstruction" in report["audit_flag"]


def test_ko6_even_n_determinant_not_forced_and_no_audit_flag():
    report = intersection_matrix_report(6, 8, seed=1)
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is False
    assert report["audit_flag"] is None
    assert report["determinant"] != pytest.approx(0.0, abs=1e-6)  # generically nonzero


def test_ko2_odd_n_forces_zero_but_audit_flag_is_ko6_specific():
    # KO=2 shares the SAME antisymmetric-odd-n zero-determinant mechanism
    # as KO=6, but the brief calls out KO=6 SPECIFICALLY as the
    # falsification/audit branch -- KO=2 must not get the same flag.
    report = intersection_matrix_report(2, 7, seed=1)
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is True
    assert report["audit_flag"] is None


# --- KO=0 and KO=4 tested independently ---------------------------------

def test_ko0_symmetric_determinant_not_forced_zero_odd_n():
    report = intersection_matrix_report(0, 5, seed=2)
    assert report["intersection_form_symmetry"] == "SYMMETRIC"
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is False
    assert report["determinant"] != pytest.approx(0.0, abs=1e-6)


def test_ko0_symmetric_determinant_not_forced_zero_even_n():
    report = intersection_matrix_report(0, 6, seed=2)
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is False


def test_ko4_symmetric_determinant_not_forced_zero_odd_n():
    report = intersection_matrix_report(4, 5, seed=3)
    assert report["intersection_form_symmetry"] == "SYMMETRIC"
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is False
    assert report["determinant"] != pytest.approx(0.0, abs=1e-6)


def test_ko4_symmetric_determinant_not_forced_zero_even_n():
    report = intersection_matrix_report(4, 6, seed=3)
    assert report["determinant_forced_zero_by_symmetry_and_parity"] is False


def test_ko0_and_ko4_are_reported_as_separate_entries_not_merged():
    r0 = intersection_matrix_report(0, 5, seed=2)
    r4 = intersection_matrix_report(4, 5, seed=2)
    assert r0["KO_mod_8"] == 0
    assert r4["KO_mod_8"] == 4
    assert r0 != r4  # distinct seeds-vs-symmetry-class produce distinct matrices/results


# --- transpose relation and signature -------------------------------------

def test_transpose_relation_confirmed_for_symmetric_case():
    report = intersection_matrix_report(4, 6, seed=5)
    assert report["transpose_relation_confirmed"] is True


def test_transpose_relation_confirmed_for_antisymmetric_case():
    report = intersection_matrix_report(6, 6, seed=5)
    assert report["transpose_relation_confirmed"] is True


def test_signature_computed_for_symmetric_matches_direct_eigenvalue_count():
    mu = construct_intersection_matrix(0, 8, seed=9)
    eigvals = np.linalg.eigvalsh(mu)
    expected_signature = int(np.sum(eigvals > 1e-9) - np.sum(eigvals < -1e-9))
    report = intersection_matrix_report(0, 8, seed=9)
    assert report["signature"] == expected_signature


def test_signature_is_none_with_explicit_note_for_antisymmetric_case():
    report = intersection_matrix_report(6, 6, seed=9)
    assert report["signature"] is None
    assert report["signature_note"] is not None
    assert "not defined" in report["signature_note"]


# --- honesty: necessary-not-sufficient, no epsilon table fabricated --------

def test_report_states_necessary_not_sufficient():
    report = intersection_matrix_report(0, 5, seed=2)
    assert "necessary-but-not-sufficient" in report["what_this_does_not_show"]


def test_invalid_ko_value_raises():
    with pytest.raises(ValueError):
        intersection_matrix_report(3, 5)  # KO=3 has no symmetric/antisymmetric row


def test_module_does_not_expose_an_epsilon_prime_prime_table():
    import seit_lang.ncg_branch as mod
    assert not hasattr(mod, "EPSILON_TABLE")
    assert not hasattr(mod, "epsilon_prime_prime")


# --- spin6/su4 and scan row passthrough -----------------------------------

def test_spin6_su4_check_matches_real_module():
    assert spin6_su4_check() == ko_dimension.spin6_su4_isomorphism_check()


def test_ko_dimension_scan_row_matches_real_scan():
    real = {row["KO_mod_8"]: row for row in ko_dimension.ko_dimension_parameter_scan()}
    assert ko_dimension_scan_row(4) == real[4]


# --- .seit type checking and cross-phase composition with Phase 5 ---------

def test_construct_intersection_matrix_return_type_is_plain_matrix():
    assert NCG_BRANCH_TRANSFORMATIONS["construct_intersection_matrix"].return_type == "Matrix"


def test_full_ncg_pipeline_composes_with_phase5_generic_matrix_ops():
    src = (
        "derive mu = construct_intersection_matrix(6, 6, 7); "
        "verify symmetric(mu); "
        "derive d = det(mu);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **NCG_BRANCH_TRANSFORMATIONS}
    bindings = {**PHYSICS_KERNEL_BINDINGS, **NCG_BRANCH_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}

    env = evaluate_program(dag, program, inputs={}, bindings=bindings)
    mu = env["mu"]
    # KO=6 antisymmetric -- symmetric(mu) must genuinely evaluate False,
    # not merely type-check.
    assert bindings["symmetric"].fn(mu) is False
    assert env["d"] == pytest.approx(float(np.linalg.det(mu)))
