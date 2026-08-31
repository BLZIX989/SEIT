"""Equivalence engine (Phase 11 of the implementation plan). `classify()`
only ever returns a classification stronger than "unknown" when a
registered, implemented equivalence CHECK actually ran and was verified --
it never infers equivalence from two outputs merely having matching values,
which is exactly the mistake the task warns against (section 14) and the
mistake this project's own eigenvalue-uniqueness counterexample
(compiler/falsification/eigen_uniqueness.py) demonstrates is unsound in
general: H and H' = U H U^dagger can share an identical spectrum while being
different matrices, so "same output" is never, by itself, evidence of
"same underlying construction."

Exactly one real check is registered for Slice 1 (DERIVATION_ENGINE_SPEC.md
section 8): verified similarity via an explicitly supplied change-of-basis
witness. Every other case -- including two candidates with no witness at
all -- returns "unknown".
"""
from __future__ import annotations

from typing import Literal

import numpy as np

from compiler.derivation.types import MathObject

Classification = Literal[
    "distinct_theory", "same_theory_different_representation",
    "equivalent_parameterization", "gauge_equivalent",
    "coordinate_transformation", "basis_transformation",
    "numerical_approximation", "distinct_candidate", "unknown",
]


class EquivalenceEngine:
    def classify(self, a: MathObject, b: MathObject, *, witness: dict | None = None) -> Classification:
        """`witness`, when given, may carry a "basis_change" key: a unitary
        (or orthogonal) matrix U claimed to intertwine a and b's carriers via
        b = U a U^dagger. The claim is independently CHECKED here (both that
        U is actually unitary and that the intertwining relation actually
        holds to numerical tolerance) -- a witness that fails either check
        does not get to relabel the result as equivalent; it falls through to
        "unknown", same as no witness at all."""
        if witness and "basis_change" in witness:
            try:
                U = np.asarray(witness["basis_change"])
                A, B = np.asarray(a.carrier), np.asarray(b.carrier)
                unitary_ok = np.allclose(U @ U.conj().T, np.eye(U.shape[0]), atol=1e-8)
                similarity_ok = np.allclose(U @ A @ U.conj().T, B, atol=1e-8)
            except Exception:
                return "unknown"
            if unitary_ok and similarity_ok:
                return "basis_transformation"
        return "unknown"
