"""Symbolic representation adapter (Phase 2). Deliberately thin: factors the
sympy pattern already used ad hoc in compiler/backends/finite_spectral_triple_
candidate.py, _recovery.py, and _recovery_coupled.py (build a symbolic matrix,
simplify a difference, compare to the zero matrix) into one function, so future
derivation modules call one place instead of re-deriving the pattern per file.
Never reimplements sympy itself.
"""
from __future__ import annotations

import numpy as np
import sympy as sp


def numpy_to_sympy(arr: np.ndarray) -> sp.Matrix:
    return sp.Matrix(arr.tolist())


def symbolic_equal(a: sp.Matrix, b: sp.Matrix) -> bool:
    """True iff sympy can simplify a-b to the exact zero matrix. Same pattern
    already used independently across the finite-spectral-triple modules."""
    if a.shape != b.shape:
        return False
    diff = sp.simplify(a - b)
    return diff == sp.zeros(*a.shape)


def symbolic_symmetric(a: sp.Matrix) -> bool:
    """Exact symbolic symmetry check: simplify(A - A^T) == 0."""
    return symbolic_equal(a, a.T)
