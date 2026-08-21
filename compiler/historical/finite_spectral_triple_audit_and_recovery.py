"""Audit of the finite/discrete spectral-triple architecture built in
compiler/backends/finite_spectral_triple_candidate.py, plus the
provenance record for the recovery construction in
compiler/backends/finite_spectral_triple_recovery.py -- same convention
as every other historical/*.py module: narrative recorded as data here,
registered as real Objects/Transformations in
compiler/ir/finite_spectral_triple_recovery.py.

Requested explicitly: find all and any problems within the current
architecture, audit them, then find a path to recovery.
"""
from __future__ import annotations

AUDIT_FINDINGS = [
    {
        "id": "AUDIT-1-D_B-DISCARDS-AVAILABLE-2-CELLS",
        "severity": "SUBSTANTIVE, NOT RESOLVED IN THIS PASS",
        "finding": (
            "D_F was chosen as D_B, the TWO-BLOCK incidence Dirac operator D=[[0,d1],[d1^T,0]] "
            "on C0 (+) C1 only. scientific_corpus/derivation/simplicial.py's own "
            "check_two_block_dirac_squaring (TFT-002) explicitly documents that this two-block "
            "operator's square omits the d2 d2^T ('up') term entirely, and is 'a restricted "
            "special case, not the operator whose square is the full graded Hodge Laplacian' "
            "whenever the underlying complex has nonempty 2-cells (triangles)."
        ),
        "verification": (
            "Checked directly, not assumed: the SAME H2 ring graph (n=200, k=3) used throughout "
            "this corpus for D_B has 600 triangles "
            "(scientific_corpus.derivation.dirac_candidates._extract_triangles), confirmed by "
            "direct computation. simplicial.py's own TFT-002B "
            "(check_three_block_hodge_dirac_squaring) already implements and verifies the "
            "richer, standard 3-graded Hodge-Dirac operator D=[[0,d1,0],[d1^T,0,d2],[0,d2^T,0]] "
            "on C0 (+) C1 (+) C2, whose square gives the FULL graded Hodge Laplacian "
            "diag(L0,L1,L2) with L1=d1^Td1+d2d2^T -- this is external, established discrete "
            "exterior calculus (Horak & Jost 2013), not a new claim."
        ),
        "consequence": (
            "D_B is not the richest Dirac-type candidate already available and already verified "
            "in this corpus for this exact graph. Using the 3-block Hodge-Dirac operator instead "
            "of the 2-block D_B as D_F -- combined with the recovery construction below -- is a "
            "legitimate next step, explicitly NOT attempted in this pass (kept as its own bounded "
            "piece of work per this project's 'new claim id, don't overreach in one pass' "
            "discipline, rather than folded into an already-large recovery attempt)."
        ),
    },
    {
        "id": "AUDIT-2-NO-OTHER-CANDIDATE-CONSTRUCTIONS-MISSED",
        "severity": "INFORMATIONAL",
        "finding": (
            "A systematic grep sweep across compiler/, scientific_corpus/, and seit_lang/ for "
            "Dirac/spectral-triple/real-structure/order-zero content found no additional "
            "algebra representation, real structure, or spectral-triple axiom check beyond "
            "the five modules already read before the original certification "
            "(h2_spectral_triple_locality_check, dirac_candidates.py, clifford_derivation.py, "
            "ko_dimension.py, ncg_branch.py) plus the newly-reviewed operator_algebra.py "
            "(Clifford/su(2) identities, unrelated to A_F), simplicial.py (see AUDIT-1), and "
            "seit_lang/incidence_clifford.py (a `.seit`-primitive repackaging of the SAME D_B "
            "construction, not a new one)."
        ),
        "verification": "grep -rl for Dirac/spectral triple/real_structure/order.zero across "
                         "the three top-level packages, each hit read.",
        "consequence": "The original certification's candidate scope was not missing an "
                        "already-built alternative algebra/real-structure (only the richer D_F "
                        "of AUDIT-1).",
    },
]

RECOVERY_MECHANISM = (
    "The prior candidate's first-order-condition failure had a precise structural cause: with "
    "J trivial (J b J^-1 = b for real b, since H_F was a plain real vector space), the condition "
    "collapses to [[D,a],b]=0 for ALL a,b in A_F, and nothing made a,b act from 'opposite sides' "
    "of D_F. The standard NCG fix for exactly this failure mode is Connes' own doubling "
    "construction: H_F' = H_F (+) H_F, genuinely COMPLEX (J being 'trivial conjugation on a "
    "real space' was exactly the degeneracy that broke the prior attempt, so this recovery must "
    "not repeat it); pi'(f) = pi(f) (+) 0 (A_F acts on copy 1 only -- the left action); "
    "gamma_F' = gamma_F (+) gamma_F; J'(xi,eta) = (conj(eta),conj(xi)) (swap + complex-conjugate, "
    "a genuine antilinear involution). D_F' = D_F (+) D_F (the SAME D_F content on each copy, "
    "zero coupling between copies -- the minimal extension)."
)

RECOVERY_RESULT = (
    "Self-adjointness, both grading axioms, and the first-order condition ALL hold exactly for "
    "this construction -- confirmed both numerically (n=200, genuine complex random test "
    "vectors, not real-valued stand-ins) and symbolically in general form (n=4, f left as a free "
    "symbol): [D_F',pi'(f)] has IDENTICALLY ZERO output on copy 2, for ANY f -- the exact "
    "structural fact that makes the first-order condition automatic, since J'pi'(g)J'^-1 only "
    "touches copy 2."
)

HONEST_CAVEATS = [
    "CONTENT-INDEPENDENT MECHANISM: the argument above works for ANY D_F once doubled this way "
    "with a copy-1-only algebra action -- it is a structural consequence of the block-disjoint "
    "bimodule shape, not a discovery specific to D_B. This is the same mechanism the genuine "
    "Connes construction uses (not a criticism of using it), but passing the first-order "
    "condition here is not by itself evidence that D_B is a physically distinguished choice.",
    "ZERO INTER-COPY COUPLING: D_F' = D_F (+) D_F has no off-diagonal term between the two "
    "copies. A richer choice (an off-diagonal 'Dirac mass'-type term between copies, as the "
    "genuine Standard Model construction has between particle and antiparticle sectors) is NOT "
    "explored here -- this recovery is the minimal extension that passes the axiom, not a claim "
    "that it is the most physically interesting one.",
    "KO-DIMENSION STILL OPEN: (epsilon,epsilon',epsilon'') come out as either (+1,+1,+1) "
    "(symmetric J sign convention) or (-1,-1,-1) (asymmetric convention) -- both verified, both "
    "still a uniform/symmetric triple rather than an arbitrary combination, and this project "
    "does not restate Connes' full KO-dimension classification table from memory "
    "(ko_dimension.py's own established policy) to check either against the physically required "
    "KO=6 mod 8. Fixing the first-order condition does NOT by itself resolve the separate "
    "KO-dimension gap H2/ncg_branch.py already identified.",
    "AUDIT-1 (D_B vs the richer 3-block Hodge-Dirac operator) remains unresolved: this recovery "
    "was built on the SAME D_B as the original certification, not the richer TFT-002B operator.",
]
