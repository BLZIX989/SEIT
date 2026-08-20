"""Phase 14 (active derivation/verification): moves the claims audited in
the Phase 13 corpus assessment from prose-level evaluation into actual
computation, per the master brief's governing rule --

    NOT DERIVED FROM DOCUMENT   != NOT DERIVABLE
    NOT CURRENTLY COMPUTED      != FALSE
    LLM CANNOT VERIFY FROM PROSE != MATHEMATICAL CLAIM CANNOT BE VERIFIED

Every module here either (a) produces a real derivation/computation with a
concrete numeric or symbolic result, or (b) identifies the exact missing
mathematical object that prevents completion -- never "this requires peer
review" as a final answer.

Isolation (brief section XVII): nothing here imports from or writes to
compiler/core, compiler/dependencies, compiler/backends, compiler/
falsification, compiler/verification, compiler/ir, or any canonical
registry. Existing compiler results (H2 FAIL, H4 FALSIFIED, the DESI
continuum-limit FAIL) are read-only inputs, never overwritten. New claims
get new claim IDs (H2B, H4B, ...), never merged into the old ones.
"""
