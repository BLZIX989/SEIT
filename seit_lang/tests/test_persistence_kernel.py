"""Tests for seit_lang.persistence_kernel (Phase 7)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends import graph_laplacian, spectral
from scientific_corpus.derivation import persistence

from seit_lang.dag import compile_dag
from seit_lang.evaluate import evaluate_program
from seit_lang.parser import parse
from seit_lang.persistence_kernel import (
    PERSISTENCE_KERNEL_BINDINGS,
    PERSISTENCE_KERNEL_TRANSFORMATIONS,
    persistence_projector,
    persistent_distance_pair,
    persistent_heat_operator,
    persistent_heat_trace,
    restricted_laplacian,
)
from seit_lang.primitives import PHYSICS_KERNEL_BINDINGS, PHYSICS_KERNEL_TRANSFORMATIONS
from seit_lang.semantic import check_program


def _real_spec(topology="cycle", n=20, seed=0):
    A = graph_laplacian.build_graph(topology, n, seed=seed).adjacency()
    L = graph_laplacian.laplacian(A)
    return L, spectral.spectrum(L)


# --- P_lambda_c --------------------------------------------------------

def test_persistence_projector_is_idempotent_and_self_adjoint():
    L, spec = _real_spec()
    lambda_c = 0.5 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    assert np.allclose(P @ P, P, atol=1e-9)
    assert np.allclose(P, P.T, atol=1e-9)


def test_persistence_projector_matches_real_persistence_module():
    L, spec = _real_spec()
    lambda_c = 0.3 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    expected, _idx, _idemp, _self_adj = persistence.persistence_projection(
        spec.eigenvalues, spec.eigenvectors, lambda_c)
    assert np.allclose(P, expected)


# --- L_Pi ----------------------------------------------------------------

def test_restricted_laplacian_matches_direct_sandwich():
    L, spec = _real_spec()
    lambda_c = 0.5 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    L_pi = restricted_laplacian(L, P)
    assert np.allclose(L_pi, P @ L @ P)


def test_restricted_laplacian_is_symmetric_psd():
    L, spec = _real_spec()
    lambda_c = 0.5 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    L_pi = restricted_laplacian(L, P)
    assert np.allclose(L_pi, L_pi.T)
    assert np.all(np.linalg.eigvalsh(L_pi) >= -1e-8)


# --- H_Pi(beta), K_Pi(beta) ------------------------------------------------

def test_persistent_heat_operator_trace_matches_persistence_module_eigenvalue_shortcut():
    """The real cross-check this module's docstring promises: K_Pi(beta)
    computed as Tr(H_Pi(beta)) from the actual restricted heat OPERATOR
    must agree with persistence.py's own eigenvalue-sum shortcut, not
    just be trusted as equivalent."""
    L, spec = _real_spec(n=25)
    lambda_c = 0.4 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    beta = 2.0
    H_pi = persistent_heat_operator(L, P, beta)
    K_pi_from_trace = persistent_heat_trace(H_pi)

    idx = persistence.persistence_projection(spec.eigenvalues, spec.eigenvectors, lambda_c)[1]
    vals_pi = spec.eigenvalues[idx]
    K_pi_shortcut = float(np.sum(np.exp(-beta * vals_pi))) if len(vals_pi) else 0.0

    assert K_pi_from_trace == pytest.approx(K_pi_shortcut, abs=1e-8)


def test_persistent_heat_trace_is_literally_the_matrix_trace():
    H = np.diag([0.5, 0.25, 0.1])
    assert persistent_heat_trace(H) == pytest.approx(0.85)


def test_persistent_heat_operator_is_symmetric():
    L, spec = _real_spec()
    lambda_c = 0.5 * float(spec.eigenvalues.max())
    P = persistence_projector(spec, lambda_c)
    H_pi = persistent_heat_operator(L, P, 1.0)
    assert np.allclose(H_pi, H_pi.T)


# --- d_{Pi,beta} -----------------------------------------------------------

def test_persistent_distance_pair_matches_real_persistence_module():
    L, spec = _real_spec(n=20)
    lambda_c = 0.5 * float(spec.eigenvalues.max())
    beta = 1.0
    result = persistent_distance_pair(spec, lambda_c, beta, 0.0, 5.0)
    idx = persistence.persistence_projection(spec.eigenvalues, spec.eigenvectors, lambda_c)[1]
    expected = persistence.persistent_distance(spec.eigenvalues, spec.eigenvectors, idx, beta, 0, 5)
    assert result == pytest.approx(expected)


# --- .seit type checking --------------------------------------------------

def test_h_pi_and_k_pi_are_typed_as_two_separate_objects():
    assert PERSISTENCE_KERNEL_TRANSFORMATIONS["persistent_heat_operator"].return_type == "Operator"
    assert PERSISTENCE_KERNEL_TRANSFORMATIONS["persistent_heat_trace"].return_type == "Scalar"


# --- full-stack integration: Phases 1-7 together, zero external inputs -----

def test_full_persistence_pipeline_computes_end_to_end():
    src = (
        'derive G = build_graph("cycle", 16); '
        "derive A = graph_adjacency(G); "
        "derive L = graph_laplacian(A); "
        "derive S = spectrum(L); "
        "derive P = persistence_projector(S, 2.0); "
        "derive L_pi = restricted_laplacian(L, P); "
        "derive H_pi = persistent_heat_operator(L, P, 1.0); "
        "derive K_pi = persistent_heat_trace(H_pi); "
        "verify symmetric(L_pi);"
    )
    program = parse(src)
    extra = {**PHYSICS_KERNEL_TRANSFORMATIONS, **PERSISTENCE_KERNEL_TRANSFORMATIONS}
    bindings = {**PHYSICS_KERNEL_BINDINGS, **PERSISTENCE_KERNEL_BINDINGS}
    check_result = check_program(program, extra_transformations=extra)
    assert check_result.unresolved_calls == []
    dag = compile_dag(program, check_result)
    assert dag.blocked == {}

    env = evaluate_program(dag, program, inputs={}, bindings=bindings)
    assert np.allclose(env["L_pi"], env["P"] @ env["L"] @ env["P"])
    assert env["K_pi"] == pytest.approx(float(np.trace(env["H_pi"])))
    assert env["K_pi"] >= 0.0
