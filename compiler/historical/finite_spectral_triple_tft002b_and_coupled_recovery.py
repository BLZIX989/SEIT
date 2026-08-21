"""Provenance record for Phase 1 (TFT-002B evaluation/promotion) and
Phase 2 (nontrivially-coupled doubled recovery) and Phase 3 (honest
sign scan) -- same convention as every other historical/*.py module.

Phase 3 is deliberately NOT a "drive to KO=6" procedure: this project's
own established policy (scientific_corpus/derivation/ko_dimension.py's
module docstring) is to never restate Connes' full KO-dimension sign
table from memory, since a misremembered entry would itself be exactly
the kind of unverified claim this project exists to avoid. This record
reports the signs the coupled construction actually produces, honestly,
without asserting a match to an external target this project cannot
independently verify.
"""
from __future__ import annotations

PHASE1_SUMMARY = (
    "TFT-002B (the standard 3-graded Hodge-Dirac operator D=[[0,d1,0],[d1^T,0,d2],[0,d2^T,0]] "
    "on C0 (+) C1 (+) C2, scientific_corpus/derivation/simplicial.py's own already-verified "
    "check_three_block_hodge_dirac_squaring) was built at full scale (n=200, matching D_B's own "
    "graph) and independently confirmed there: self-adjoint, both grading axioms hold, and "
    "D3^2 = diag(L0,L1,L2) exactly (the FULL graded Hodge Laplacian, L1=d1^Td1+d2d2^T). The edge "
    "block L1 genuinely differs from D_B's restricted up_term=d1^Td1 (max abs difference 4.0 -- "
    "not a rounding artifact), confirming the AUDIT-1 finding was real: 600 triangles were "
    "available and unused. All required invariants hold and D_B is not modified or removed (new "
    "claim id, not an overwrite) -- TFT-002B is PROMOTED as an additional, independent candidate."
)

PHASE2_SUMMARY = (
    "The verified Hilbert-doubling mechanism was re-applied over TFT-002B, this time with a "
    "genuinely nonzero, non-proportional Hermitian inter-copy coupling C = i*mu*(independently-"
    "weighted copy of the same (d1,d2) incidence pattern) -- the natural minimal choice "
    "satisfying the grading constraint {C,gamma3}=0 (itself required for {D_F'',gamma_F''}=0 to "
    "hold at all; derived, not assumed). Self-adjointness, both grading axioms, and the "
    "first-order condition ALL hold exactly (residual 0.0, not merely < 1e-15) at n=200 with "
    "genuine complex random test vectors, and symbolically in general form (n=4, f, g, AND the "
    "coupling weights w all left as free symbols). The mechanism differs from Phase 2's original "
    "(uncoupled) recovery: [D_F'',pi'(f)] now has a genuinely nonzero copy1-to-copy2 output block "
    "once C is nonzero (the 'zero output on copy 2' fact no longer holds), so the original proof "
    "does not apply unchanged. The correct, independently-derived reason instead is that the "
    "condition reduces to pi(f)*C*pi(g) (and its adjoint), which vanishes IDENTICALLY because "
    "C's own support (vertex-edge, edge-triangle only, zero vertex-vertex) is disjoint from where "
    "pi(f),pi(g) (vertex-vertex-diagonal only) can produce a nonzero product composed on both "
    "sides -- a general fact about ANY coupling sharing D3's grading-odd block support, "
    "independent of the specific weights."
)

PHASE3_SUMMARY = (
    "Scanned (epsilon,epsilon',epsilon'') for four sign conventions of J' (symmetric +1/+1, "
    "symmetric -1/-1, and the two asymmetric mixed conventions). RESULT: the two symmetric "
    "conventions both give (+1,+1,+1) exactly (residual 0.0, first-order condition holds). The "
    "two ASYMMETRIC conventions give epsilon=epsilon''=-1 but epsilon' UNDETERMINED (JD_ppJ^-1 "
    "is neither +D_pp nor -D_pp exactly) -- because C is genuinely complex (carries the i*mu "
    "factor) while D3 is real, so C and D3 transform differently under an asymmetric J, unlike "
    "the uncoupled Phase 2 case where D_F'=D_F(+)D_F was entirely real and every sign convention "
    "gave a clean, uniform triple. This is reported as-is: only (+1,+1,+1) is a clean, "
    "fully-determined signature for this coupled construction."
)

PHASE3_EXPLICIT_LIMIT = (
    "This project does NOT attempt to 'drive the system into compliance with Connes' canonical "
    "table for the physical KO=6 sector' by further tuning J' parameters. Doing so would require "
    "either (a) restating Connes' full (epsilon,epsilon',epsilon'') -> KO-mod-8 classification "
    "table from memory to know what target to fit to -- explicitly refused by this project's own "
    "established policy (ko_dimension.py's module docstring: 'mis-deriving it from memory would "
    "be exactly the kind of unverified claim this module exists to avoid'), or (b) tuning "
    "parameters specifically to match a memorized/assumed target rather than reporting what the "
    "construction naturally produces -- the general failure mode this entire project's discipline "
    "exists to prevent. The honest state is: this construction's natural signs are (+1,+1,+1); "
    "whether that matches or fails to match KO=6 mod 8 remains OPEN, exactly as ncg_branch.py and "
    "h2_spectral_triple_locality_check already left it for every prior candidate in this corpus."
)
