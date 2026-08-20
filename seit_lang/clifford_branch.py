"""Clifford derivation branch as executable `.seit` primitives
(Phase 10): represents Cl(n) parametrically, calculates a minimal n
satisfying a well-defined condition (demonstrating the search
MECHANISM the brief asks for), and verifies
{gamma_a,gamma_b}=2*eta_ab*I exactly rather than assuming it -- building
on, not modifying, scientific_corpus/derivation/clifford_derivation.py.

NEW MATH IN THIS MODULE, AND WHY IT IS SAFE TO ADD:
clifford_derivation.py never constructs actual gamma matrices -- its
existing clifford_rank_forcing_check() only established that this
project's OWN incidence/Dirac construction (B, D_B, L; see Phase 6)
does not force any specific Clifford-algebra dimension n (status: "NOT
COMPUTABLE FROM AVAILABLE DEFINITIONS -- dimension is UNFORCED"). The
brief's Phase 10 asks for an actual parametric Cl(n) representation and
a verified anticommutation check, which requires new code -- but this
is STANDARD, EXTERNAL, well-established mathematics (the Jordan-Wigner
/ Pauli-tensor-product construction of Clifford-algebra generators,
the same recursive pattern used to build multi-qubit Pauli-string
operators), not a new physics claim about this project's own
construction. Per this whole project's discipline (see e.g.
ko_dimension.py's own caution against citing a classification table
from memory), the construction is not merely asserted correct: it is
VERIFIED numerically for every generator pair, for n up to 8, in this
phase's own tests -- if the tensor-product formula were misremembered,
those tests would fail, exactly the same "verify computed results
rather than assume" discipline that caught the KO-dimension example
matrix bug earlier in this project.

Restricted to the EUCLIDEAN signature (eta_ab = delta_ab, all +1) with
COMPLEX gamma matrices -- the general Lorentzian-signature / real
(as opposed to complex) representation theory of Clifford algebras
follows an 8-fold Bott-periodic dimension table that this module does
NOT attempt to reproduce from memory, to avoid exactly the kind of
unverified-classification-table risk ko_dimension.py's own docstring
warns about.

"CALCULATE MINIMAL FORCED n": clifford_rank_forcing_report() exposes
clifford_derivation.py's own existing, already-verified finding
UNCHANGED -- there is no forcing condition from this project's own
construction, so there is no "minimal forced n" to report for the real
physics question. minimal_n_for_representation_dimension_at_least()
demonstrates the general SEARCH mechanism the brief's phrase asks for,
applied to a well-defined MATHEMATICAL condition (representation
dimension) instead -- it is not a substitute answer to the physics
question, and this module never conflates the two.

"ONLY PROMOTE Cl(6) TO DERIVED IF ACTUALLY FORCED, ELSE PROPOSED/OPEN":
generate_clifford_status_declaration() emits `.seit` source using
`variable` + `status` (the same OPEN-preserving pattern Phase 8
established for KC-003, reusing its exact classifier function,
seit_lang.continuum_bridge._seit_status_label, rather than a second,
possibly-diverging implementation) -- since
clifford_rank_forcing_check()'s status text starts with "NOT
COMPUTABLE", Cl(6) is labeled OPEN, never DERIVED.
"""
from __future__ import annotations

import numpy as np

from scientific_corpus.derivation import clifford_derivation

from .continuum_bridge import _seit_status_label
from .primitives import PrimitiveBinding
from .semantic import TransformationSignature

_PAULI = {
    1: np.array([[0, 1], [1, 0]], dtype=complex),
    2: np.array([[0, -1j], [1j, 0]], dtype=complex),
    3: np.array([[1, 0], [0, -1]], dtype=complex),
}
_I2 = np.eye(2, dtype=complex)


def _kron_chain(mats: list[np.ndarray]) -> np.ndarray:
    result = mats[0]
    for m in mats[1:]:
        result = np.kron(result, m)
    return result


def euclidean_gamma_matrices(n: int) -> list[np.ndarray]:
    """Standard complex representation of the Euclidean Clifford algebra
    Cl(n,0): n gamma matrices of size 2^ceil(n/2) x 2^ceil(n/2)
    satisfying {gamma_a, gamma_b} = 2 delta_ab I (verified numerically
    in this phase's tests, not merely asserted). Standard
    Jordan-Wigner-style tensor-product construction (external,
    well-established), not a novel claim."""
    k = n // 2
    gammas: list[np.ndarray] = []
    for j in range(k):
        for pauli_idx in (1, 2):
            factors = [_PAULI[3]] * j + [_PAULI[pauli_idx]] + [_I2] * (k - j - 1)
            gammas.append(_kron_chain(factors))
    if n % 2 == 1:
        factors = [_PAULI[3]] * k
        gammas.append(_kron_chain(factors) if factors else np.array([[1.0]], dtype=complex))
    return gammas


def clifford_representation_dimension(n: float) -> float:
    """dim of the representation euclidean_gamma_matrices(n) constructs:
    2^floor(n/2) -- both an odd generator count n=2k+1 and the even
    count n=2k below it share the same k pairs plus (for odd n) one
    extra chirality-type generator that does NOT increase the matrix
    size, so the dimension only grows every SECOND n, at even n. Locked
    to the actual constructed matrix size by
    test_representation_dimension_matches_actual_constructed_matrix_size,
    not merely asserted -- an earlier version of this function used
    2^ceil(n/2), which silently disagreed with the real construction at
    every odd n; caught by that cross-check test, not by inspection."""
    return float(2 ** (int(n) // 2))


def verify_clifford_anticommutation(n: float) -> dict:
    n_i = int(n)
    gammas = euclidean_gamma_matrices(n_i)
    dim = gammas[0].shape[0] if gammas else 1
    identity = np.eye(dim, dtype=complex)
    max_residual = 0.0
    all_ok = True
    for a in range(len(gammas)):
        for b in range(len(gammas)):
            anticommutator = gammas[a] @ gammas[b] + gammas[b] @ gammas[a]
            expected = 2.0 * identity if a == b else np.zeros((dim, dim), dtype=complex)
            residual = float(np.max(np.abs(anticommutator - expected))) if dim else 0.0
            max_residual = max(max_residual, residual)
            if residual > 1e-9:
                all_ok = False
    return {
        "n": n_i,
        "representation_dimension": dim,
        "n_generators": len(gammas),
        "anticommutation_relation_holds_exactly": all_ok,
        "max_residual": max_residual,
        "claim": "{gamma_a, gamma_b} = 2 delta_ab I (Euclidean signature eta_ab = delta_ab), "
                 "checked exactly for every generator pair a,b -- not assumed from the "
                 "construction formula",
    }


def minimal_n_for_representation_dimension_at_least(min_dim: float, max_n: float = 20) -> float:
    """The smallest n (0 <= n <= max_n) whose Cl(n) representation has
    dimension >= min_dim, or -1 if none exists within max_n. A genuine,
    general minimal-n SEARCH over a well-defined MATHEMATICAL condition
    -- see module docstring for why this is not a physics-forcing
    answer."""
    min_dim_i, max_n_i = int(min_dim), int(max_n)
    for n in range(max_n_i + 1):
        if clifford_representation_dimension(n) >= min_dim_i:
            return float(n)
    return -1.0


def clifford_gamma_matrix(n: float, a: float) -> np.ndarray:
    """The a-th (1-indexed) gamma matrix of euclidean_gamma_matrices(n)."""
    gammas = euclidean_gamma_matrices(int(n))
    return gammas[int(a) - 1]


def clifford_rank_forcing_report() -> dict:
    """Unchanged from scientific_corpus/derivation/clifford_derivation.py
    -- this project's own construction does not force any specific n."""
    return clifford_derivation.clifford_rank_forcing_check()


def generate_clifford_status_declaration(n: float = 6) -> str:
    """Emit .seit source for Cl(n) using `variable` + `status` (never
    `derive`), reusing Phase 8's exact status-label classifier so
    Cl(6) is never silently promoted to DERIVED: since
    clifford_rank_forcing_check()'s status text starts with "NOT
    COMPUTABLE", the emitted label is OPEN."""
    n_i = int(n)
    report = clifford_derivation.clifford_rank_forcing_check()
    label = _seit_status_label(report["status"])
    provenance_text = report["evidence"].replace('"', "'").replace("\n", " ")
    name = f"Cl_{n_i}"
    return (
        f"module clifford_branch;\n"
        f"variable {name}: Dataset;\n"
        f"status {name} = {label};\n"
        f'provenance {name} = "{provenance_text}";\n'
    )


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("clifford_gamma_matrix", ["Scalar", "Scalar"], "Operator",
                      clifford_gamma_matrix,
                      "seit_lang.clifford_branch.clifford_gamma_matrix (standard Euclidean "
                      "Clifford-algebra gamma-matrix representation)"),
    PrimitiveBinding("verify_clifford_anticommutation", ["Scalar"], "Dataset",
                      verify_clifford_anticommutation,
                      "seit_lang.clifford_branch.verify_clifford_anticommutation"),
    PrimitiveBinding("clifford_representation_dimension", ["Scalar"], "Scalar",
                      clifford_representation_dimension,
                      "seit_lang.clifford_branch.clifford_representation_dimension"),
    PrimitiveBinding("minimal_n_for_representation_dimension_at_least", ["Scalar"], "Scalar",
                      lambda min_dim: minimal_n_for_representation_dimension_at_least(min_dim),
                      "seit_lang.clifford_branch.minimal_n_for_representation_dimension_at_least "
                      "(max_n fixed at 20 for this .seit binding)"),
    PrimitiveBinding("clifford_rank_forcing_report", [], "Dataset",
                      clifford_rank_forcing_report,
                      "seit_lang.clifford_branch.clifford_rank_forcing_report (calls "
                      "scientific_corpus.derivation.clifford_derivation.clifford_rank_forcing_check)"),
]

CLIFFORD_BRANCH_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
CLIFFORD_BRANCH_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
