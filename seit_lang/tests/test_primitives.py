"""Tests for seit_lang.primitives (Phase 5)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian, heat_flow, spectral
from seit_lang.parser import parse
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import BUILTIN_TRANSFORMATIONS, SemanticChecker, TransformationSignature, check_program
from seit_lang.types import UNRESOLVED


# --- signature consistency with Phase 2 -------------------------------

def test_the_7_shared_signatures_match_phase_2_exactly():
    for name in BUILTIN_TRANSFORMATIONS:
        assert PHYSICS_KERNEL_TRANSFORMATIONS[name] == BUILTIN_TRANSFORMATIONS[name]


def test_conflicting_extra_transformation_raises_at_construction():
    bad = {"transpose": TransformationSignature("transpose", ["Vector"], "Vector")}
    with pytest.raises(ValueError):
        SemanticChecker(extra_transformations=bad)


def test_new_primitives_resolve_only_when_extra_transformations_supplied():
    src = 'derive G = build_graph("cycle", 5);'
    result_without = check_program(parse(src))
    assert any(c.callee == "build_graph" for c in result_without.unresolved_calls)
    assert result_without.symbols["G"] == UNRESOLVED

    result_with = check_program(parse(src), extra_transformations=PHYSICS_KERNEL_TRANSFORMATIONS)
    assert result_with.unresolved_calls == []
    assert result_with.symbols["G"] == "Graph"


# --- real execution: the 7 shared primitives --------------------------

def test_transpose_is_real_numpy_transpose():
    M = np.array([[1.0, 2.0], [3.0, 4.0]])
    result = PHYSICS_KERNEL_BINDINGS["transpose"].fn(M)
    assert np.array_equal(result, M.T)


def test_symmetric_true_for_symmetric_matrix():
    M = np.array([[2.0, 1.0], [1.0, 2.0]])
    assert PHYSICS_KERNEL_BINDINGS["symmetric"].fn(M) is True


def test_symmetric_false_for_asymmetric_matrix():
    M = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert PHYSICS_KERNEL_BINDINGS["symmetric"].fn(M) is False


def test_positive_semidefinite_true_for_real_graph_laplacian():
    A = graph_laplacian.build_graph("cycle", 5).adjacency()
    L = graph_laplacian.laplacian(A)
    assert PHYSICS_KERNEL_BINDINGS["positive_semidefinite"].fn(L) is True


def test_positive_semidefinite_false_for_negative_definite_matrix():
    M = -np.eye(3)
    assert PHYSICS_KERNEL_BINDINGS["positive_semidefinite"].fn(M) is False


def test_det_matches_numpy():
    M = np.array([[2.0, 0.0], [0.0, 3.0]])
    assert PHYSICS_KERNEL_BINDINGS["det"].fn(M) == pytest.approx(6.0)


def test_norm_matches_numpy():
    v = np.array([3.0, 4.0])
    assert PHYSICS_KERNEL_BINDINGS["norm"].fn(v) == pytest.approx(5.0)


def test_spectrum_bound_directly_to_real_compiler_backend():
    assert PHYSICS_KERNEL_BINDINGS["spectrum"].fn is spectral.spectrum


def test_heat_kernel_bound_directly_to_real_compiler_backend():
    assert PHYSICS_KERNEL_BINDINGS["heat_kernel"].fn is heat_flow.heat_operator


def test_spectrum_on_real_path_graph_matches_known_eigenvalues():
    # path graph on 2 nodes: L = [[1,-1],[-1,1]], eigenvalues 0 and 2 exactly
    A = graph_laplacian.build_graph("path", 2).adjacency()
    L = graph_laplacian.laplacian(A)
    spec = PHYSICS_KERNEL_BINDINGS["spectrum"].fn(L)
    assert sorted(np.round(spec.eigenvalues, 8)) == [0.0, 2.0]


# --- real execution: new primitives -------------------------------------

def test_build_graph_produces_real_graph_with_correct_size():
    g = PHYSICS_KERNEL_BINDINGS["build_graph"].fn("cycle", 6.0)
    assert g.n == 6
    assert g.topology == "cycle"
    assert len(g.edges) == 6  # a 6-cycle has 6 edges


def test_graph_adjacency_matches_real_graph_method():
    g = graph_laplacian.build_graph("star", 4)
    result = PHYSICS_KERNEL_BINDINGS["graph_adjacency"].fn(g)
    assert np.array_equal(result, g.adjacency())


def test_graph_laplacian_matches_real_backend_function():
    A = graph_laplacian.build_graph("complete", 4).adjacency()
    result = PHYSICS_KERNEL_BINDINGS["graph_laplacian"].fn(A)
    assert np.array_equal(result, graph_laplacian.laplacian(A))


def test_spectral_gap_matches_real_spectraldata_property():
    A = graph_laplacian.build_graph("cycle", 5).adjacency()
    L = graph_laplacian.laplacian(A)
    spec = spectral.spectrum(L)
    assert PHYSICS_KERNEL_BINDINGS["spectral_gap"].fn(spec) == pytest.approx(spec.spectral_gap)
    assert spec.spectral_gap > 0  # connected graph -> nonzero gap


def test_kernel_projector_matches_real_spectraldata_method():
    A = graph_laplacian.build_graph("path", 4).adjacency()
    L = graph_laplacian.laplacian(A)
    spec = spectral.spectrum(L)
    result = PHYSICS_KERNEL_BINDINGS["kernel_projector"].fn(spec)
    assert np.array_equal(result, spec.kernel_projector())
