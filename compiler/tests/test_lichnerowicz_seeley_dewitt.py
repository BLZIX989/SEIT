"""Tests for compiler/backends/lichnerowicz_seeley_dewitt.py."""
from __future__ import annotations

from compiler.backends.lichnerowicz_seeley_dewitt import (
    verify_lichnerowicz_gauge_term,
    verify_lichnerowicz_gravity_term,
    verify_seeley_dewitt_E_dependence,
)


def test_gauge_term_residual_is_exactly_zero():
    r = verify_lichnerowicz_gauge_term()
    assert r.residual_is_zero is True
    assert r.clifford_algebra_checked is True


def test_gravity_term_coefficient_solved_matches_textbook_quarter():
    r = verify_lichnerowicz_gravity_term()
    assert r.christoffel_checked is True
    assert r.R_computed == 2.0
    assert r.matches_textbook_quarter is True


def test_gravity_term_R_is_independently_computed_not_quoted():
    # If the Christoffel/Riemann pipeline were broken, this would not
    # accidentally equal 2 (the known S^2 value) -- it is computed fresh
    # from the metric each call, not hardcoded.
    r = verify_lichnerowicz_gravity_term()
    assert abs(r.R_computed - 2.0) < 1e-12


def test_seeley_dewitt_E_dependence_all_points_pass_at_default_tolerance():
    report = verify_seeley_dewitt_E_dependence()
    assert report.all_passed is True
    assert len(report.points) == 4
    for p in report.points:
        assert p.a0_residual < report.tolerance
        assert p.a1_residual < report.tolerance
        assert p.a2_residual < report.tolerance


def test_seeley_dewitt_a0_independent_of_E():
    # a0 = tr(I)*Vol has no E-dependence in Gilkey's formula -- confirm
    # the fitted a0 is the same (S^3 volume 2*pi^2) at every E tested.
    report = verify_seeley_dewitt_E_dependence()
    a0_values = [p.a0_fit for p in report.points]
    assert max(a0_values) - min(a0_values) < 1e-6


def test_seeley_dewitt_a6_honestly_marked_open():
    report = verify_seeley_dewitt_E_dependence()
    assert report.a6_status == "OPEN"
    assert "not" in report.a6_note.lower() and "independently rederived" in report.a6_note


def test_degree_3_fit_shows_the_bias_degree_4_fixes_at_large_E():
    # Documents the real fit-window sensitivity found during verification
    # (degree=3 was insufficient at E=2.5, degree=4 is not) so a future
    # change to fit_degree default cannot silently reintroduce it unnoticed.
    biased = verify_seeley_dewitt_E_dependence(E_values=(2.5,), fit_degree=3, tolerance=1e-4)
    assert biased.all_passed is False
    fixed = verify_seeley_dewitt_E_dependence(E_values=(2.5,), fit_degree=4, tolerance=1e-4)
    assert fixed.all_passed is True
