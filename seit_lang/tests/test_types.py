"""Tests for seit_lang.types (Phase 2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.types import SEIT_TYPES, ancestors, comparable, is_known_type, is_subtype, widen


_FMUTC_BRIEF_24_TYPES = {
    "Scalar", "Vector", "Matrix", "Operator", "Graph", "IncidenceMatrix",
    "Laplacian", "Spectrum", "Eigenvector", "Projector", "Metric",
    "Connection", "Curvature", "Tensor", "State", "DensityMatrix",
    "Algebra", "HilbertSpace", "CliffordAlgebra", "SpectralTriple",
    "Functional", "Equation", "Theorem", "Dataset",
}


def test_all_24_original_fmutc_brief_types_still_present_unchanged():
    assert _FMUTC_BRIEF_24_TYPES <= SEIT_TYPES


def test_exactly_one_documented_post_brief_extension_type():
    # Trajectory (seit_lang/evolution_branch.py's typed evolve/
    # trajectory abstraction) is the only addition beyond the brief's
    # original 24 -- see types.py's module docstring for why.
    extra = SEIT_TYPES - _FMUTC_BRIEF_24_TYPES
    assert extra == {"Trajectory"}
    assert len(SEIT_TYPES) == 25


def test_is_known_type():
    assert is_known_type("Matrix") is True
    assert is_known_type("NotAType") is False


def test_ancestors_of_root_type_is_empty():
    assert ancestors("Matrix") == []
    assert ancestors("Scalar") == []


def test_ancestors_of_specialized_type():
    assert ancestors("IncidenceMatrix") == ["Matrix"]
    assert ancestors("Eigenvector") == ["Vector"]
    assert ancestors("CliffordAlgebra") == ["Algebra"]


def test_ancestors_of_unknown_type_raises():
    with pytest.raises(KeyError):
        ancestors("NotAType")


def test_is_subtype_reflexive():
    assert is_subtype("Matrix", "Matrix") is True


def test_is_subtype_true_for_specialization():
    assert is_subtype("IncidenceMatrix", "Matrix") is True
    assert is_subtype("Laplacian", "Matrix") is True


def test_is_subtype_false_in_reverse_direction():
    assert is_subtype("Matrix", "IncidenceMatrix") is False


def test_is_subtype_false_for_unrelated_types():
    assert is_subtype("Scalar", "Matrix") is False
    assert is_subtype("Vector", "Matrix") is False


def test_comparable_is_symmetric():
    assert comparable("IncidenceMatrix", "Matrix") is True
    assert comparable("Matrix", "IncidenceMatrix") is True


def test_comparable_false_for_unrelated_types():
    assert comparable("Scalar", "Matrix") is False
    assert comparable("Eigenvector", "IncidenceMatrix") is False


def test_widen_returns_the_more_general_type_either_direction():
    assert widen("IncidenceMatrix", "Matrix") == "Matrix"
    assert widen("Matrix", "IncidenceMatrix") == "Matrix"


def test_widen_same_type():
    assert widen("Matrix", "Matrix") == "Matrix"


def test_widen_raises_for_incomparable_types():
    with pytest.raises(ValueError):
        widen("Scalar", "Matrix")


def test_incidence_matrix_and_laplacian_are_siblings_not_comparable():
    # Both specialize Matrix but are not comparable to EACH OTHER --
    # only to their common ancestor.
    assert comparable("IncidenceMatrix", "Laplacian") is False


def test_trajectory_is_a_specialization_of_dataset():
    assert is_subtype("Trajectory", "Dataset") is True
    assert ancestors("Trajectory") == ["Dataset"]


def test_trajectory_is_not_a_vector_or_matrix():
    assert is_subtype("Trajectory", "Vector") is False
    assert is_subtype("Trajectory", "Matrix") is False
