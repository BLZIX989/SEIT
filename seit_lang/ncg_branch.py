"""NCG (KO-dimension) branch as executable `.seit` primitives (Phase 9):
a parameterized KO-dimension audit, building on -- not modifying --
scientific_corpus/derivation/ko_dimension.py. Enumerates candidates and
constructs an actual A_F = C (+) H (+) M_3(C)-style intersection matrix
mu (parameterized by KO mod 8, size n, and a seed) with rank,
determinant, transpose relation, and (where classically defined)
signature. KO=6 is treated as a falsification/audit branch specifically
when it forces det(mu)=0; KO=0 and KO=4 are tested independently (as
separate, distinctly named tests, not merged into one parameterized
assertion). A nonzero determinant is documented, at every level, as
necessary-but-not-sufficient -- never promoted to a claim about the
real fermion-representation matrix this project has not constructed.

ON epsilon/epsilon'/epsilon'': the brief asks this phase to "calculate"
them. This module deliberately does NOT state specific epsilon,
epsilon', epsilon'' sign values, for the exact reason
scientific_corpus/derivation/ko_dimension.py's own module docstring
already gives: "The mapping from KO-dimension to the symmetry signs...
is Connes' own classification table -- cited here as an external fact,
not re-derived from K-theory first principles... mis-deriving it from
memory would be exactly the kind of unverified claim this module exists
to avoid." ko_dimension.py's real code, despite its docstring mentioning
all three signs, only actually COMPUTES two derived consequences per KO
value (real_structure_commutes_with_grading, intersection_form_symmetry)
-- it never commits to the full three-way table either, for the same
reason. This module exposes exactly what ko_dimension.py's real code
computes, and states plainly that the full epsilon/epsilon'/epsilon''
table is NOT computed here -- respecting the exact discipline the
existing module already established, rather than now fabricating sign
values from memory just because the brief's prose lists them.

construct_intersection_matrix()'s return type is plain "Matrix" (not
a new subtype) specifically so a `.seit` program can also apply Phase
5's generic det()/transpose()/symmetric() primitives to it directly.
"""
from __future__ import annotations

import numpy as np

from scientific_corpus.derivation import ko_dimension

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def _scan_row(KO_mod_8: int) -> dict:
    rows = {row["KO_mod_8"]: row for row in ko_dimension.ko_dimension_parameter_scan()}
    if KO_mod_8 not in rows or rows[KO_mod_8]["intersection_form_symmetry"] not in ("SYMMETRIC", "ANTISYMMETRIC"):
        raise ValueError(
            f"KO mod 8 = {KO_mod_8} has no symmetric/antisymmetric classification in "
            f"ko_dimension.ko_dimension_parameter_scan() (only 0, 2, 4, 6 do)")
    return rows[KO_mod_8]


def ko_dimension_scan_row(KO_mod_8: float) -> dict:
    """The real scan row for one KO mod 8 value -- unchanged, from
    ko_dimension.ko_dimension_parameter_scan()."""
    return _scan_row(int(KO_mod_8))


def construct_intersection_matrix(KO_mod_8: float, n: float, seed: float = 0) -> np.ndarray:
    """A deterministic (seeded) pseudo-random real n x n matrix with the
    symmetry class ko_dimension.ko_dimension_parameter_scan() associates
    with the given KO mod 8 (ANTISYMMETRIC for KO in {2,6}, SYMMETRIC
    for KO in {0,4}) -- NOT a claim about any specific physical
    fermion-representation multiplicity matrix. See module docstring."""
    KO_mod_8_i, n_i, seed_i = int(KO_mod_8), int(n), int(seed)
    row = _scan_row(KO_mod_8_i)
    rng = np.random.default_rng(seed_i)
    raw = rng.standard_normal((n_i, n_i))
    if row["intersection_form_symmetry"] == "ANTISYMMETRIC":
        return raw - raw.T
    return raw + raw.T


def intersection_matrix_report(KO_mod_8: float, n: float, seed: float = 0) -> dict:
    KO_mod_8_i, n_i, seed_i = int(KO_mod_8), int(n), int(seed)
    row = _scan_row(KO_mod_8_i)
    symmetry = row["intersection_form_symmetry"]
    mu = construct_intersection_matrix(KO_mod_8_i, n_i, seed_i)

    det = float(np.linalg.det(mu))
    rank = int(np.linalg.matrix_rank(mu))
    odd_n = bool(n_i % 2 == 1)
    determinant_forced_zero = bool(symmetry == "ANTISYMMETRIC" and odd_n)

    if symmetry == "SYMMETRIC":
        transpose_relation = "mu.T == mu (symmetric)"
        transpose_confirmed = bool(np.allclose(mu.T, mu))
        eigvals = np.linalg.eigvalsh(mu)
        signature = int(np.sum(eigvals > 1e-9) - np.sum(eigvals < -1e-9))
        signature_note = None
    else:
        transpose_relation = "mu.T == -mu (antisymmetric)"
        transpose_confirmed = bool(np.allclose(mu.T, -mu))
        signature = None
        signature_note = (
            "classical eigenvalue-sign signature is not defined for a real "
            "antisymmetric matrix (its eigenvalues are non-real) -- NOT computed, "
            "not approximated")

    audit_flag = None
    if KO_mod_8_i == 6 and determinant_forced_zero:
        audit_flag = (
            "KO=6 with odd n forces det(mu)=0 (algebraic certainty, per "
            "ko_dimension.skew_symmetric_odd_determinant_check). IF the REAL "
            "finite-algebra intersection matrix for this project's own construction "
            "is confirmed odd-dimensional, this would be a genuine obstruction "
            "requiring further audit (analogous in kind to H4's rank obstruction) -- "
            "NOT YET established, since no real fermion-representation multiplicity "
            "matrix has been constructed anywhere in this corpus.")

    return {
        "KO_mod_8": KO_mod_8_i, "n": n_i, "seed": seed_i,
        "intersection_form_symmetry": symmetry,
        "determinant": det,
        "determinant_forced_zero_by_symmetry_and_parity": determinant_forced_zero,
        "rank": rank,
        "transpose_relation": transpose_relation,
        "transpose_relation_confirmed": transpose_confirmed,
        "signature": signature,
        "signature_note": signature_note,
        "audit_flag": audit_flag,
        "what_this_does_not_show": (
            f"This is a pseudo-random (seeded) instance of the symmetry class KO mod 8 "
            f"= {KO_mod_8_i} implies, per ko_dimension.ko_dimension_parameter_scan()'s "
            f"external, established classification -- NOT the SPECIFIC multiplicity "
            f"matrix this project's own A_F = C (+) H (+) M_3(C) construction would "
            f"produce (which requires an actual fermion-representation assignment not "
            f"present anywhere in this repository, exactly as "
            f"ko_dimension.symmetric_3x3_nonzero_determinant_example() already states). "
            f"A nonzero determinant here is necessary-but-not-sufficient evidence for "
            f"the corresponding real claim; it never substitutes for constructing that "
            f"real matrix."),
    }


def spin6_su4_check() -> dict:
    return ko_dimension.spin6_su4_isomorphism_check()


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("ko_dimension_scan_row", ["Scalar"], "Dataset",
                      ko_dimension_scan_row,
                      "seit_lang.ncg_branch.ko_dimension_scan_row (calls "
                      "scientific_corpus.derivation.ko_dimension.ko_dimension_parameter_scan)"),
    PrimitiveBinding("construct_intersection_matrix", ["Scalar", "Scalar", "Scalar"], "Matrix",
                      construct_intersection_matrix,
                      "seit_lang.ncg_branch.construct_intersection_matrix (mu, parameterized by "
                      "the symmetry class ko_dimension.py associates with a given KO mod 8)"),
    PrimitiveBinding("intersection_matrix_report", ["Scalar", "Scalar", "Scalar"], "Dataset",
                      intersection_matrix_report,
                      "seit_lang.ncg_branch.intersection_matrix_report"),
    PrimitiveBinding("spin6_su4_check", [], "Dataset",
                      spin6_su4_check,
                      "seit_lang.ncg_branch.spin6_su4_check (calls "
                      "scientific_corpus.derivation.ko_dimension.spin6_su4_isomorphism_check)"),
]

NCG_BRANCH_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
NCG_BRANCH_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
