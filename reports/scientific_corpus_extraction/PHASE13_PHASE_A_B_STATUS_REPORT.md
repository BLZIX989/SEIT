# Phase 13, Phases A+B: Scientific Corpus — Reconnaissance & Existing-Corpus Ingestion

**Status report, not a completion claim.** Phase 13's full master brief specifies 57
sections and a 15-phase execution order (Phase A through Phase O) building toward a
provenance-preserving corpus of established scientific mathematics — literature discovery
across arXiv/INSPIRE-HEP/NASA ADS/NIST, LaTeX/MathML extraction pipelines, variable/operator/
equivalence/dimensional-analysis engines, cross-domain structure detection, and a UOC
translation crosswalk, culminating in 25 final deliverables. That is a multi-week, likely
multi-person engineering effort. This report covers exactly what has actually been executed
so far: **Phase A (repository reconnaissance) and Phase B (ingestion of the project's
existing equation/operator content into the new corpus schema)** — the brief's own required
first two phases (section LII), and nothing past them.

## What was built

- `scientific_corpus/` — a new top-level package, entirely separate from `compiler/` and
  never imported by it (brief section XLVIII). `schema.py` defines `Source`, `CorpusEquation`,
  `CorpusOperator` — deliberately smaller than the brief's full ~40-field schemas (section VI/
  IX): every field present is one this slice can populate honestly from data that already
  exists in this repository; fields the brief asks for that this slice cannot yet populate
  (units, dimensions, equivalence classes, UOC translation, mathematical type) are simply
  absent rather than filled with a placeholder.
- `data/scientific_corpus/` — the directory architecture from brief section XXXVII (`sources/`,
  `equations/`, `variables/`, `constants/`, `operators/`, `functions/`, `commutators/`,
  `algebras/`, `groups/`, `representations/`, `geometries/`, `manifolds/`, `bundles/`,
  `categories/`, `functors/`, `transformations/`, `dependencies/`, `equivalence/`,
  `validation/`, `provenance/`, `coverage/`). Only `sources/`, `equations/`, `operators/`, and
  `coverage/` are populated this slice; every other subdirectory exists but is empty — see
  `SCIENTIFIC_CORPUS_MANIFEST.json`'s `not_yet_populated` list.
- `scripts/generate_scientific_corpus_phase_ab.py` — the real ingestion script. Reads (never
  writes) `equation_registry.json`, `transformation_registry.json`, and
  `literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json`, and writes the new corpus
  JSONL files plus a coverage report and manifest.
- `scientific_corpus/tests/` — 16 tests: every corpus record traces to a real registry id,
  compiler-derived vs. literature-source-claim status is never conflated, no duplicate ids,
  deterministic hashing, the generator never touches a canonical registry file, and the
  coverage report never claims completeness.

## Real, measured numbers (from `data/scientific_corpus/coverage/coverage_report.json`)

| | |
|---|---|
| Sources | 4 (this repo's own compiler; the FC-005 historical workbook `04_fc005_primary_full_execution.xlsx`; Tong's *String Theory*, arXiv:0908.0333v3; Kiritsis's *Introduction to Superstring Theory*, arXiv:hep-th/9709062v2) |
| Equations ingested | 60 (35 from `equation_registry.json`, 25 from the existing string-theory literature extraction) |
| — compiler-derived (real `Status`, this compiler's own execution) | 6 |
| — source claims (historical workbook, PROPOSED, explicitly not trusted at face value) | 29 |
| — source claims (string theory literature, "textbook-established" per the source) | 25 |
| Operators ingested | 9 (`transformation_registry.json`, includes the Phase 12 Ollivier-Ricci curvature transformation) |
| Variables / constants / functions / groups / geometries / categories extracted | **0** |

This corpus does **not** contain "every equation in science," nor even every equation in this
repository's own `source_material/` (39 documents, none of which have been equation-extracted
yet). It contains exactly the equations already transcribed into the two registries above.

## Provenance discipline actually enforced

- A compiler-executed equation (e.g. `EQ-LAPLACIAN-ROW-SUM-ZERO`, real `Status.DERIVED` from a
  symbolic sympy proof) is tagged `COMPILER_DERIVED`.
- A historical-workbook-imported equation (`EQ-001`..`EQ-029`) is tagged `SOURCE_CLAIM` and
  carries forward the compiler's own existing skepticism verbatim — `equation_registry.json`
  already annotates these `"workbook_claimed_status='CLOSED' -- NOT trusted at face value"`;
  this corpus preserves that annotation rather than upgrading it.
- A string-theory literature equation is tagged `SOURCE_CLAIM` with the source's own
  characterization (e.g. `"textbook-established (standard relativistic mechanics)"`) stored
  verbatim, never converted into this corpus's own truth claim.
- These two categories are never merged (`scientific_corpus/tests/test_ingestion.py::
  test_source_isolation_compiler_vs_workbook_never_conflated`).

## What has explicitly NOT been done (Phases C through O)

- No external literature acquisition (arXiv/INSPIRE-HEP/NASA ADS/NIST-CODATA API queries) —
  brief Phase C/D.
- No variable/operator/structure extraction from equation text (symbol tokenization,
  disambiguation) — brief Phase F.
- No normalization pipeline (alpha-normalization, index-normalization, algebraic
  canonicalization) — brief Phase G.
- No dimensional analysis or mathematical-type inference — brief Phase H.
- No equivalence engine (any of the 12 equivalence classes in section XXIX) — brief Phase I.
- No equation dependency graph beyond what each source registry already recorded — brief
  Phase J.
- No cross-domain structure detection — brief Phase K.
- No UOC translation crosswalk — brief Phase L.
- No falsification/counterexample search over corpus structures — brief Phase M.
- None of the 25 final deliverables in section LI, and none of the 11 required spreadsheets
  in section XXXVIII, have been generated — those depend on the phases above.

## Verification

`python3 -m pytest scientific_corpus/tests -q` → 16 passed. `git diff` on every canonical
registry file (`equation_registry.json`, `transformation_registry.json`,
`object_registry.json`, `master_mdcl.json`, `self_audit_report.json`,
`chainlink_registry.json`, `protocol_registry.json`) confirmed empty before and after running
the generator — enforced by its own test, not just manual inspection.
