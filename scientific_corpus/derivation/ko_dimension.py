"""KO-dimension / Krajewski intersection-form audit (canonical_closure_report
follow-up Sec.8 -- explicitly NOT accepting the closure report's own
KO=6->0/4 "resolves it" framing; this module does exactly what the user's
own instruction block asks instead: enumerate, calculate, and keep
"necessary" separate from "sufficient").

External, established physics this module explicitly does NOT re-derive:
the Chamseddine-Connes-Marcolli real spectral triple for the Standard
Model uses the finite algebra A_F = C (+) H (+) M_3(C) (3 summands) and
KO-dimension 6 mod 8 specifically (Chamseddine, Connes, Marcolli 2007,
"Gravity and the standard model with neutrino mixing"). The mapping from
KO-dimension to the symmetry signs (epsilon, epsilon', epsilon'') of the
real structure J is Connes' own classification table -- cited here as an
external fact, not re-derived from K-theory first principles (doing so
correctly from scratch is its own substantial project, well beyond a
sign-table lookup, and mis-deriving it from memory would be exactly the
kind of unverified claim this module exists to avoid).

What IS independently, exactly verified here is the pure linear-algebra
mechanism: for odd n, ANY real skew-symmetric n x n matrix has
determinant identically zero. This is checked symbolically for n=3,5,7,
not merely asserted for the specific 3x3 case.
"""
from __future__ import annotations

import sympy as sp


def skew_symmetric_odd_determinant_check(n_values: tuple[int, ...] = (3, 5, 7)) -> dict:
    """det(A) = det(A^T) always (any square matrix). For A skew-symmetric,
    A^T = -A, so det(A) = det(-A) = (-1)^n det(A). For odd n, (-1)^n = -1,
    giving det(A) = -det(A), i.e. 2 det(A) = 0, i.e. det(A) = 0 -- for
    EVERY real skew-symmetric matrix of odd size, not just a specific one.
    Verified here symbolically (a fully general symbolic skew-symmetric
    matrix, entries left as free symbols) for each n, not just numerically
    on one example."""
    results = {}
    for n in n_values:
        entries = sp.symbols(f"a0:{n * (n - 1) // 2}", real=True)
        A = sp.zeros(n, n)
        k = 0
        for i in range(n):
            for j in range(i + 1, n):
                A[i, j] = entries[k]
                A[j, i] = -entries[k]
                k += 1
        det_A = sp.simplify(A.det())
        results[n] = {"symbolic_determinant": str(det_A), "identically_zero": det_A == 0}
    return {
        "claim": "For every odd n, det(A)=0 identically for ANY real skew-symmetric n x n "
                 "matrix A (a general algebraic identity, not a property of one example)",
        "results": results,
        "all_odd_n_confirm_identically_zero": all(r["identically_zero"] for r in results.values()),
    }


def symmetric_3x3_nonzero_determinant_example() -> dict:
    """Demonstrates the obstruction is REMOVED (not that it is resolved for
    THIS project's specific construction) for symmetric matrices: unlike
    the skew-symmetric case, real symmetric matrices are NOT forced to
    have zero determinant at any size. One concrete example with small
    nonnegative-integer entries (the kind of entries an actual multiplicity
    matrix would plausibly have) suffices to prove non-vanishing is
    possible; it does NOT prove any SPECIFIC matrix arising from this
    project's own construction has nonzero determinant, because no such
    specific matrix has been constructed anywhere in the corpus (that
    would require the actual fermion-representation multiplicities, which
    are additional physical input, not derived from B, D_B, or any other
    object already built here)."""
    M = sp.Matrix([[2, 1, 0], [1, 2, 1], [0, 1, 2]])  # plausible small-integer symmetric example (tridiagonal)
    det_M = M.det()
    return {
        "claim": "Real symmetric n x n matrices are NOT identically forced to have "
                 "determinant zero (unlike the odd-n skew-symmetric case)",
        "example_matrix": str(M.tolist()),
        "determinant": int(det_M),
        "nonzero": bool(det_M != 0),
        "what_this_DOES_NOT_show": (
            "This shows nonzero-determinant symmetric 3x3 matrices EXIST, i.e. the "
            "obstruction that makes the odd-n skew-symmetric case impossible does not apply "
            "to the symmetric case in general. It does NOT show that the SPECIFIC "
            "multiplicity matrix this project's own construction would produce (which "
            "requires an actual fermion-representation assignment for A_F = C (+) H (+) "
            "M_3(C), not present anywhere in this repository) has nonzero determinant -- "
            "that remains OPEN, exactly as the user's own instruction states."
        ),
    }


def ko_dimension_parameter_scan() -> list[dict]:
    """Enumerates KO in {0,1,...,7} with the external, established sign
    facts, WITHOUT claiming to independently re-derive Connes' KO-dimension
    classification table from K-theory (cited as external fact, sourced to
    Chamseddine-Connes-Marcolli 2007). Each row records only what
    determinant-parity consequence follows IF that KO-dimension's
    associated symmetry sign holds -- this module does not assert which
    KO-dimension is "correct" for this project, since no independent
    derivation of that exists anywhere in the corpus."""
    # (epsilon, epsilon', epsilon'') from Connes' standard table; only the
    # symmetric-vs-antisymmetric consequence for the intersection form is
    # used below, not the full physical content of the table.
    rows = [
        {"KO_mod_8": 0, "real_structure_commutes_with_grading": True,
         "intersection_form_symmetry": "SYMMETRIC", "odd_dim_determinant_forced_zero": False},
        {"KO_mod_8": 1, "real_structure_commutes_with_grading": "N/A (no grading at KO=1)",
         "intersection_form_symmetry": "N/A", "odd_dim_determinant_forced_zero": "N/A"},
        {"KO_mod_8": 2, "real_structure_commutes_with_grading": False,
         "intersection_form_symmetry": "ANTISYMMETRIC", "odd_dim_determinant_forced_zero": True},
        {"KO_mod_8": 4, "real_structure_commutes_with_grading": True,
         "intersection_form_symmetry": "SYMMETRIC", "odd_dim_determinant_forced_zero": False},
        {"KO_mod_8": 6, "real_structure_commutes_with_grading": False,
         "intersection_form_symmetry": "ANTISYMMETRIC", "odd_dim_determinant_forced_zero": True},
    ]
    for row in rows:
        row["source"] = "external, established (Connes' KO-dimension classification table, " \
                         "as used in Chamseddine-Connes-Marcolli 2007) -- NOT independently " \
                         "re-derived from K-theory first principles in this module"
    return rows


def spin6_su4_isomorphism_check() -> dict:
    """Spin(6) ~= SU(4): a real, standard, well-known low-dimensional Lie
    group isomorphism (exceptional isomorphism among the classical
    groups). Checked here by the two arithmetic invariants available
    without a full root-system construction: dimension and rank."""
    spin6 = {"dim": 15, "rank": 3}  # dim(SO(6))=15=dim(Spin(6)); rank(D3)=3
    su4 = {"dim": 15, "rank": 3}   # dim(SU(4))=4^2-1=15; rank(A3)=3
    return {
        "claim": "Spin(6) ~= SU(4) (standard exceptional isomorphism, D3 ~= A3 Dynkin diagrams)",
        "external_established_mathematics": True,
        "dim_match": spin6["dim"] == su4["dim"],
        "rank_match": spin6["rank"] == su4["rank"],
        "note": "Dimension/rank match is consistent with, but does not independently prove, "
                "the isomorphism (that requires the actual D3=A3 root-system identification, "
                "standard but not reproduced here). Cited as external established fact.",
    }
