"""Provenance record for the finite/discrete spectral-triple candidate
certification -- same convention as fc005_reconciliation.py,
continuum_exponent_correction.py, seeley_dewitt_verification.py: the
narrative is recorded as plain data here, then registered as real
Objects/Transformations in compiler/ir/finite_spectral_triple_certification.py.

Requested explicitly as the correct execution boundary: certify
(A_F,H_F,D_F,J_F,gamma_F) BEFORE computing D_B^2 -> (E_B,Omega_B) ->
(a0^B,a2^B,a4^B,a6^B), not after. This is the first module in the corpus
that actually constructs a concrete candidate and runs the first-order
condition [[D,a],JbJ^-1]=0 -- every prior module
(h2_spectral_triple_locality_check, dirac_candidates.py,
clifford_derivation.py, ko_dimension.py, ncg_branch.py) explicitly
states this was never attempted.
"""
from __future__ import annotations

CANDIDATE_DEFINITION = (
    "D_F = D_B, the H2B block-incidence Dirac operator (dirac_candidates.py) on the SAME H2 "
    "ring graph (n=200, k=3) used throughout this corpus, for exact comparability. H_F = "
    "R^(N0+N1) (vertex block + edge block). A_F = C(V), the algebra of real-valued functions "
    "on the graph's vertex set -- genuinely derived from the graph itself, NOT the Standard "
    "Model's A_F = C (+) H (+) M_3(C) (which nothing in this project's own construction forces "
    "or produces -- see clifford_derivation.py::clifford_rank_forcing_check). pi(f) = "
    "multiplication by f on the vertex block, zero on the edge block (the edge-block content "
    "is generated FROM this representation via [D_F,pi(f)], per Connes' own formalism, not "
    "separately assigned). gamma_F = diag(I_N0,-I_N1), the natural Z/2 grading matching D_F's "
    "block-swap structure. J_F = complex conjugation on H_F, the natural real structure (same "
    "choice H2 already used for D+=sqrt(L))."
)

WHY_THIS_CANDIDATE = (
    "Chosen to be the most honestly-derivable candidate from this project's own objects, "
    "reusing exactly what the corpus already independently identified as its best finite "
    "Dirac-operator candidate (H2B, chosen over D+=sqrt(L) specifically because H2B is local "
    "by construction while D+=sqrt(L) was found dense/non-local -- see "
    "h2_spectral_triple_locality_check). A_F=C(V) is the natural commutative algebra a graph "
    "itself provides (functions on its vertex set), avoiding the discipline "
    "clifford_derivation.py already established: never import the Standard Model's target "
    "algebra as an assumption."
)

FINDINGS = [
    {
        "check": "self-adjointness of D_F",
        "result": "HOLDS",
        "note": "Exact block-antisymmetric-transpose structure by construction; confirms "
                "dirac_candidates.py's own D_self_adjoint=True finding.",
    },
    {
        "check": "grading axioms (gamma_F^2=I, {D_F,gamma_F}=0, [pi(f),gamma_F]=0)",
        "result": "ALL HOLD",
        "note": "Mechanical consequence of the block structure (gamma_F block-diagonal, D_F "
                "block-off-diagonal, pi(f) block-diagonal) -- checked directly, not assumed.",
    },
    {
        "check": "real-structure signs (epsilon, epsilon', epsilon'')",
        "result": "(+1, +1, +1) -- degenerate/trivial",
        "note": "Complex conjugation fixes every real matrix in this construction (D_F, "
                "gamma_F, pi(f) are all real), so all three signs come out trivially +1. This "
                "is the SAME degenerate situation h2_spectral_triple_locality_check already "
                "found for D+=sqrt(L) ('J^2=+1...this corresponds to KO-dimension 0 mod 8...for "
                "a triple with no grading'). Per ko_dimension.py's own explicit policy, this "
                "record does NOT restate Connes' full (epsilon,epsilon',epsilon'')->KO-mod-8 "
                "table from memory to attach a specific integer label to the graded case here; "
                "the substantive point -- no discriminating real-structure content is produced "
                "by the natural choice -- holds regardless of the exact label.",
    },
    {
        "check": "first-order condition [[D_F,pi(f)],pi(g)]=0 for all a=pi(f),b=pi(g) in A_F",
        "result": "FAILS",
        "note": "Exact closed form (confirmed both numerically at n=200 with random f,g, and "
                "symbolically in general form at n=4 with f,g left as free symbols): "
                "[[D_F,pi(f)],pi(g)] = [[0, diag(f*g) d1],[d1^T diag(f*g), 0]], nonzero for "
                "generic f,g (verified to vanish correctly for the degenerate case f*g=0 "
                "everywhere, confirming the closed form is genuinely computed, not a stub). "
                "This is the FIRST TIME this check has been run anywhere in this corpus -- "
                "every prior module (dirac_candidates.py, clifford_derivation.py, "
                "h2_spectral_triple_locality_check) explicitly states it as not yet attempted.",
    },
]

STRUCTURAL_REASON_FOR_FAILURE = (
    "With J trivial (JbJ^-1=b for real b), the first-order condition collapses to "
    "[[D,a],b]=0 for ALL a,b in A_F. Nothing in this representation makes a and b act from "
    "'opposite sides' of D_F the way a genuine real structure is supposed to -- that mechanism "
    "is exactly what a nontrivial J swapping left/right module actions is FOR (as in the "
    "genuine Standard Model construction, where J b J^-1 acts as a right A_F-module action "
    "distinct from the left action of a). A trivial J removes that mechanism entirely, so "
    "there is no cancellation and the condition fails generically."
)

CONSEQUENCE_FOR_SPECTRAL_ACTION = (
    "Connes' inner-fluctuation formula D_A = D_F + omega + J*omega*J^-1 (omega = sum a[D_F,b]) "
    "is only guaranteed well-defined/gauge-covariant when the first-order condition holds. It "
    "does not hold here, so (E_B, Omega_B) in the physical Chamseddine-Connes sense CANNOT be "
    "certified for this candidate -- there is no well-posed fluctuated operator D_A to take a "
    "Lichnerowicz-type decomposition of. The BARE, unfluctuated D_F^2 remains exactly "
    "computable (block-diagonal, confirms dirac_candidates.py's own diag(L0,d1^T d1) result), "
    "giving E_B=0 trivially for the unfluctuated operator -- but this is a much weaker "
    "statement than a genuine NCG spectral action, and a0^B..a6^B cannot be certified as "
    "physically meaningful moments on this basis. Per the explicit instruction that certification "
    "governs whether the spectral action can be touched: it cannot, for THIS candidate, until "
    "either (a) a genuinely different (A_F,J_F,gamma_F) is found that passes the first-order "
    "condition, or (b) the corpus explicitly accepts the trivial E_B=0 bare-operator reading, "
    "which none of its existing physical claims do."
)
