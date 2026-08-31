"""Phase 11: EquivalenceEngine. Confirms the discipline required by
DERIVATION_ENGINE_SPEC.md section 8 -- a classification stronger than
'unknown' is returned ONLY when an explicit, checked equivalence witness
actually verifies, never inferred from matching numeric output alone.
"""
from __future__ import annotations

import numpy as np

from compiler.derivation.equivalence import EquivalenceEngine
from compiler.derivation.types import EpistemicKind, MathObject, MathType


def _random_unitary(n, seed):
    rng = np.random.default_rng(seed)
    z = (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diagonal(r)
    return q * (d / np.abs(d))


def test_verified_change_of_basis_classifies_as_basis_transformation():
    rng = np.random.default_rng(0)
    A = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    H = (A + A.conj().T) / 2
    U = _random_unitary(3, seed=1)
    H_prime = U @ H @ U.conj().T

    a = MathObject(id="H", math_type=MathType.SELF_ADJOINT_OPERATOR,
                    epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=H)
    b = MathObject(id="H-prime", math_type=MathType.SELF_ADJOINT_OPERATOR,
                    epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=H_prime)

    engine = EquivalenceEngine()
    assert engine.classify(a, b, witness={"basis_change": U}) == "basis_transformation"


def test_no_witness_defaults_to_unknown_even_with_identical_spectrum():
    """The eigenvalue-uniqueness counterexample's own lesson: two operators
    with an IDENTICAL spectrum must never be classified as equivalent absent
    an actual, checked witness -- 'unknown' is the honest default."""
    rng = np.random.default_rng(2)
    A = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    H = (A + A.conj().T) / 2
    U = _random_unitary(3, seed=3)
    H_prime = U @ H @ U.conj().T
    assert not np.allclose(H, H_prime)
    assert np.allclose(sorted(np.linalg.eigvalsh(H)), sorted(np.linalg.eigvalsh(H_prime)))

    a = MathObject(id="H2", math_type=MathType.SELF_ADJOINT_OPERATOR,
                    epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=H)
    b = MathObject(id="H2-prime", math_type=MathType.SELF_ADJOINT_OPERATOR,
                    epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=H_prime)

    engine = EquivalenceEngine()
    assert engine.classify(a, b) == "unknown"


def test_false_witness_is_independently_checked_not_trusted():
    """A witness matrix that is NOT actually unitary, or does not actually
    intertwine a and b, must not be able to force a false classification."""
    a = MathObject(id="M1", math_type=MathType.MATRIX, epistemic_kind=EpistemicKind.DERIVED_RESULT,
                    carrier=np.eye(2))
    b = MathObject(id="M2", math_type=MathType.MATRIX, epistemic_kind=EpistemicKind.DERIVED_RESULT,
                    carrier=np.array([[2.0, 0.0], [0.0, 2.0]]))
    engine = EquivalenceEngine()
    fake_witness = {"basis_change": np.array([[1.0, 1.0], [0.0, 1.0]])}  # not unitary
    assert engine.classify(a, b, witness=fake_witness) == "unknown"
