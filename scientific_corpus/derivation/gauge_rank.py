"""H4B -- extends (does not overwrite) the existing H4 result
(compiler/backends/toe_closure_hypotheses.py::h4_g2_spin8_construction_check).

H4 already established, via rank counting:
  - G2 (intersection-via-triality claim) CANNOT contain SU(3)xSU(2)xU(1): FALSIFIED.
  - Aut(octonions) x Spin(8) (direct-product claim, the repository's own
    original formulation, and the same one the Spectral Codex Eq.21
    states) has enough RANK (2+4=6 >= 4) to potentially contain it:
    UNCONSTRUCTED, not falsified, not proven.

This module goes one step further per the brief's section VIII instruction
("does not stop after falsifying one candidate... what is the SMALLEST
algebraic structure already present in the framework from which the
observed gauge symmetry could potentially emerge?") by checking the two
specific standard embeddings the direct-product route would need:
  SU(3) subset G2        (real, standard, well-known fact)
  SU(2)xU(1) subset Spin(8)   (rank/dimension feasibility, not full construction)
"""
from __future__ import annotations

LIE_GROUP_FACTS = {
    "G2": {"dim": 14, "rank": 2},
    "Spin(8)": {"dim": 28, "rank": 4},
    "SU(3)": {"dim": 8, "rank": 2},
    "SU(2)": {"dim": 3, "rank": 1},
    "U(1)": {"dim": 1, "rank": 1},
}


def su3_in_g2_check() -> dict:
    """SU(3) is a maximal subgroup of G2 -- this is standard, established
    Lie theory (see e.g. Fulton & Harris, "Representation Theory", or any
    exceptional-group reference table), not a project-specific claim.
    Verified here by the one arithmetic check available without a full
    representation-theory computation: dim(G2) - dim(SU(3)) = dim(G2/SU(3)),
    and G2/SU(3) is the well-known 6-sphere S^6 (dim 6), which the
    dimension count below reproduces exactly."""
    g2, su3 = LIE_GROUP_FACTS["G2"], LIE_GROUP_FACTS["SU(3)"]
    coset_dim = g2["dim"] - su3["dim"]
    return {
        "claim": "SU(3) subset G2 (maximal subgroup, standard external Lie theory)",
        "external_established_mathematics": True,
        "rank_check": f"rank(SU(3))={su3['rank']} <= rank(G2)={g2['rank']}: "
                      f"{'CONSISTENT' if su3['rank'] <= g2['rank'] else 'VIOLATED'}",
        "dimension_check": f"dim(G2)-dim(SU(3)) = {g2['dim']}-{su3['dim']} = {coset_dim}, "
                            "matching the known dimension of the coset space G2/SU(3) = S^6 "
                            "(the 6-sphere) -- consistent with the standard fact, not an "
                            "independent proof of it (that requires the actual root-system "
                            "embedding, which is standard but not reproduced here).",
        "status": "CONDITIONALLY SUPPORTED -- real, standard mathematics; NOT independently "
                  "re-derived by this project, cited as established external fact.",
    }


def su2xu1_in_spin8_check() -> dict:
    """Rank/dimension FEASIBILITY only -- not a full embedding construction.
    A necessary (not sufficient) condition for H subset G is rank(H) <=
    rank(G) and dim(H) <= dim(G). Both are checked; neither, alone or
    together, constitutes a proof of embedding, and no explicit embedding
    map is constructed here."""
    spin8 = LIE_GROUP_FACTS["Spin(8)"]
    su2, u1 = LIE_GROUP_FACTS["SU(2)"], LIE_GROUP_FACTS["U(1)"]
    h_dim, h_rank = su2["dim"] + u1["dim"], su2["rank"] + u1["rank"]
    return {
        "claim": "SU(2)xU(1) subset Spin(8)",
        "rank_check": f"rank(SU(2)xU(1))={h_rank} <= rank(Spin(8))={spin8['rank']}: "
                      f"{'NECESSARY CONDITION SATISFIED' if h_rank <= spin8['rank'] else 'VIOLATED'}",
        "dimension_check": f"dim(SU(2)xU(1))={h_dim} <= dim(Spin(8))={spin8['dim']}: "
                            f"{'NECESSARY CONDITION SATISFIED' if h_dim <= spin8['dim'] else 'VIOLATED'}",
        "status": "UNRESOLVED -- rank and dimension are NECESSARY, not sufficient, conditions "
                  "for subgroup embedding. Spin(8) does contain many rank-2 subgroups (e.g. "
                  "SU(2)xSU(2)xSU(2)xSU(2) is a maximal-rank-4 subgroup via the D4 root "
                  "system; SU(2)xU(1) embeds inside various of Spin(8)'s maximal subgroups by "
                  "further restriction), so infeasibility is NOT the finding here -- but no "
                  "SPECIFIC embedding tied to this project's actual spectral/graph "
                  "construction has been given anywhere in the corpus, so 'feasible in "
                  "principle' must not be read as 'constructed'.",
    }


def missing_link_to_compiler_spectrum() -> dict:
    """The gap that matters most for THIS project specifically (as opposed
    to abstract Lie theory, which is not in question): even a fully
    constructed embedding SU(3)xSU(2)xU(1) subset Aut(O)xSpin(8) would not,
    by itself, connect to anything the compiler's own graph Laplacian
    spectrum actually computes. SEIT-7 (Universal Rosetta Vol.4 Ch.23)
    proposes a DIFFERENT, spectrum-native mechanism -- the commutant
    algebra of L_Gamma via Schur's Lemma, contingent on a (3,2,1)
    eigenvalue-multiplicity degeneracy pattern -- and explicitly marks
    that mechanism [Conjecture], not [Established]. This is registered as
    its own claim, H4C, tracked separately in
    MATHEMATICAL_CLAIM_REGISTRY.json, and is NOT computed here: the corpus
    gives no rule for WHICH graph construction is supposed to produce this
    degeneracy, so there is nothing concrete to run yet."""
    return {
        "claim_id": "H4C",
        "claim": "SEIT-7: Aut(L_Gamma) = product of U(m_k) via Schur's Lemma, IF the "
                 "low-lying spectrum of L_Gamma has eigenvalue-multiplicity pattern (3,2,1)",
        "status": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS",
        "missing_object": (
            "A specific graph construction (topology, size, edge-weight rule) that the "
            "corpus asserts represents 'the physical vacuum state' or equivalent, whose "
            "low-lying Laplacian spectrum is claimed to exhibit degeneracy (3,2,1). No such "
            "construction rule exists anywhere in the accessible corpus -- Vol.4 Ch.23 "
            "itself states this is 'the central open question for SEIT's derivation of the "
            "Standard Model gauge structure' and marks it [Conjecture]. Once such a graph "
            "is specified, this IS directly computable with the compiler's existing "
            "eigh()-based spectral backend (compiler/backends/spectral.py) -- eigenvalue "
            "multiplicities are a standard, cheap linear-algebra computation, not a "
            "conceptual obstacle."
        ),
    }
