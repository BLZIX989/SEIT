"""Phase 14 (master brief): the mathematical extraction layer.

    SOURCE -> DOCUMENT STRUCTURE -> EQUATION EXTRACTION -> VARIABLE
    EXTRACTION -> OPERATOR EXTRACTION -> STRUCTURE EXTRACTION ->
    PROVENANCE-LINKED MATHEMATICAL CORPUS

Governing principle (brief section I): EXTRACT FIRST, INTERPRET SECOND,
VALIDATE THIRD, PROMOTE LAST. Nothing in this package performs semantic
equivalence, canonicalization, cross-domain unification, UOC
translation, theorem promotion, or physical validation -- those are
later phases (brief section XXXVII, explicit stop condition).

Relationship to Phase 13's scientific_corpus/schema.py (CorpusEquation/
CorpusOperator, data/scientific_corpus/equations/equations.jsonl and
operators/operators.jsonl): that layer is REGISTRY INGESTION -- a
narrow, already-tested contract that copies what already existed in
equation_registry.json / STRING_THEORY_LITERATURE_REGISTRY.json /
transformation_registry.json verbatim into the corpus, one record per
existing registry entry, no decomposition. This package is genuinely
different in kind: it DECOMPOSES equations into their constituent
variable/operator/relation occurrences, with a much richer schema
(brief section IV/IX/XI/XII), and it is the only layer in the corpus
that reads raw acquired source bytes (PDF text) rather than already-
structured registry data. Per brief section II ("do not create
duplicate registries merely because an old registry exists ... extend
only if doing so preserves its existing contract"), this is kept as a
separate, new registry family (data/scientific_corpus/{equations,
variables,operators,relations,structures}/*_registry.jsonl) rather than
mutating Phase 13's equations.jsonl/operators.jsonl, whose existing
contract (and the tests depending on it) this package leaves untouched.

Extraction status vocabulary actually used this phase (brief section
III), kept intentionally smaller than the brief's full list -- only
statuses this phase's real extraction methods can honestly assign:
    SOURCE_EXTRACTED  -- a symbol/equation/relation occurrence read
                         directly off a real acquired or existing
                         source, not independently derived by anything
                         in this repository.
    COMPILER_DERIVED  -- carried over unchanged from Phase 13's
                         ingestion of the compiler's own equation/
                         transformation registries.
    UNRESOLVED        -- extraction attempted but the result is
                         ambiguous, low-confidence, or PDF-text noise;
                         routed to the review queue, never silently
                         upgraded to SOURCE_EXTRACTED.
Never VERIFIED: verification is a compiler-side status this layer never
assigns to anything (brief section III: "established physics" is not a
compiler verification status).
"""
