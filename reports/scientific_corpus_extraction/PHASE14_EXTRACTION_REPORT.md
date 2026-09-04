# Phase 14: Mathematical Extraction Layer

Governing principle enforced throughout: EXTRACT FIRST, INTERPRET SECOND, VALIDATE THIRD, PROMOTE LAST. Nothing in this phase performs semantic equivalence, canonicalization, cross-domain unification, UOC translation, theorem promotion, or physical validation.

## Counts

- Sources processed: 2 literature sources (LIT-TONG-ST, LIT-KIRITSIS-SST) + 10 acquired PDF documents
- Documents processed: 12
- Equations extracted: 25 (all from the literature registry -- PDF text extraction produced review-queue candidates only, never structured equation records; see below)
- Variables extracted: 285
- Operators extracted: 54
- Relations extracted: 4
- Structures extracted: 16
- Review queue total: 1086 (0 literature-side ambiguities, 1086 PDF-text candidate equation lines not promoted to structured records)
- Requiring human review: 1086 (100% of review-queue items -- none were auto-resolved)

## Extraction methods used

- LATEX_SOURCE: 25

## Extraction quality

- EXACT_LATEX: 25

## PDF extraction (real pypdf text extraction against the 10 real Phase 13 C/D PDFs)

- Pages processed per document (capped): 10 or fewer (min of 10-page cap and actual page count)
- Candidate equation-bearing lines found: 1086
- None of these were converted into equation_registry.jsonl records: rendered PDF text has no reliable LaTeX/MathML structure, so promoting them would mean fabricating confidence this phase does not have (brief section VII). All are in EXTRACTION_REVIEW_QUEUE.csv.

## UOC chain literature crosswalk

- COMPILER_ONLY: 7 rows
- OPEN: 4 rows
- SOURCE_SUPPORT: 39 rows
- UNRESOLVED: 6 rows

Full detail in UOC_CHAIN_LITERATURE_CROSSWALK.csv/.xlsx. Summary: of the chain's 11 positions, this repository's compiler directly implements 6 as real IR nodes (Delta, G, L, Spec(L), a metric CANDIDATE, and a discrete curvature analogue); Gamma, nabla, S, and delta S = 0 have no direct compiler node. The 25-equation string-theory literature corpus supports the action-functional position (S) directly (Nambu-Goto/Polyakov actions) but its worldsheet metric is explicitly NOT claimed equivalent to the chain's spacetime g_{mu nu}, and its discrete curvature analogue is explicitly NOT claimed equivalent to Riemannian scalar curvature R -- both flagged in the crosswalk's own provenance field rather than silently conflated.

## Canonical compiler status

UNCHANGED. This phase reads status_matrix.json read-only for the UOC chain crosswalk and writes nothing to any canonical registry (see brief section XXVIII; verified by a real subprocess test comparing every canonical file's bytes before and after a full extraction run).

## Test status

- scientific_corpus/tests: 80/80 passed (16 Phase A/B + 29 Phase 13 C/D source-discovery + 35 new
  this phase: 13 tokenizer, 18 extraction-pipeline including two real canonical-isolation subprocess
  tests, 4 audit-script tests including a regression test for a real bug found in the audit itself)
- compiler/tests: 114/114 passed, unaffected (this phase adds no compiler code and reads only
  status_matrix.json, read-only, for the UOC chain crosswalk)

## Audit status

- 10/10 audits passed (source_provenance, extraction_completeness, extraction_determinism,
  duplicate, symbol_collision, operator, relation, dimensional_metadata, canonical_isolation,
  uoc_chain_crosswalk) -- see PHASE14_EXTRACTION_AUDIT.json for the full machine-readable result.
- One real audit failure was found and fixed during this phase: the source_provenance_audit's
  first version assumed every record type carries a `provenance` field, but SymbolOccurrence/
  OperatorOccurrence carry their provenance in `source_location`/`extraction_method` instead by
  schema design -- the bug produced 54 false-positive failures against every real, correctly-
  provenanced operator record. Fixed in the audit script itself (not the extraction data, which
  was correct), with a regression test.

## What this phase does NOT claim

- It does not claim these are "all equations in physics" or even all equations in the acquired PDFs -- see brief section II/XXVII. Coverage is exactly: the 25 literature equations already transcribed in a prior phase, plus PDF-text candidate lines from the first 10 pages of 10 real acquired papers.
- Source occurrence is not mathematical derivation, formal proof, or empirical validation (brief section XXXIV). Every equation record's source_status is SOURCE_EXTRACTED, never VERIFIED.
- A repeated equation is not a theorem; a mathematically-plausible equivalence is not a canonical identity -- no equivalence analysis was attempted (Phase 15+, not started).
