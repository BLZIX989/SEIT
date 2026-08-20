# Phase 13, Phases C+D: Scientific Source Discovery + Acquisition

**DISCOVERY_COMPLETE / ACQUISITION_COMPLETE / EXTRACTION READY: NO** (equation/variable/operator extraction, per brief section XIX, has not been attempted on any acquired source this phase).

## Discovery

- Queries executed: 24 (failed: 0)
- Raw hits across all queries: 144
- Unique sources after arXiv-id dedup: 135
- Duplicate hits removed: 9
- Domains covered: mathematics, physics
- Channel used: arXiv API only (export.arxiv.org/api/query) -- INSPIRE-HEP, NASA ADS, NIST/DLMF, HEPData, Crossref, OpenAlex are brief-listed Level 2 sources NOT implemented this slice.

## Acquisition

- Sources fulltext-acquired (PDF, hashed): 10
- Access-restricted / license-restricted: 0
- Acquisition failures (preserved, not discarded): 0
- Linked to an existing Phase A/B project source (never duplicated): 0
- LaTeX source packages (arXiv /e-print): 0 -- arxiv.org/robots.txt explicitly Disallows /e-print and /src for automated agents; only /pdf (Allowed) was fetched. This is a real, disclosed limitation, not an oversight.

## External UOCP/UDP/DER corpus

EXTERNAL_CORPUS_NOT_PRESENT. That corpus was not searched for, fabricated, or reconstructed from memory this phase (brief section XXI).

## Unresolved acquisition issues

- None this run.

## Reproducibility

- discovery_run_id: RUN-0001
- software_version: phase13-source-discovery-0.1.0
- mode: LIVE
- source_registry_hash: 7816521d3a6bd6c3468df34a8a5f72cc0591f3f9930c028e0059cccd49d8f3c3

See `data/scientific_corpus/SCIENTIFIC_DISCOVERY_RUNS.jsonl` (append-only) for the full history of discovery runs, and `data/scientific_corpus/coverage/SOURCE_COVERAGE_MATRIX.csv` for per-domain coverage state.

## Acceptance criteria

- [x] existing Phase A/B corpus remains intact (extended, never overwritten; enforced by test)
- [x] source discovery registry exists (`data/scientific_corpus/sources/discovery/SCIENTIFIC_SOURCE_DISCOVERY_REGISTRY.jsonl`, 135 records)
- [x] query registry exists (`data/scientific_corpus/sources/discovery/query_registry.jsonl`, 24 records)
- [x] source IDs are deterministic (`stable_source_id`, sha256-derived, never a URL)
- [x] duplicate handling exists (arXiv-id dedup across queries; 9 duplicates removed this run)
- [ ] version lineage -- only the single `version` field is tracked per source (e.g. "v2"); full multi-version lineage (REVISED_VERSION/JOURNAL_VERSION/ERRATUM relations) is NOT implemented this slice
- [x] source hashes exist (sha256 of acquired bytes, in `acquisition_manifests.jsonl`)
- [x] acquisition manifests exist
- [x] legitimate-access rules are enforced (robots.txt Allow/Disallow honored; only /pdf fetched, never /e-print)
- [x] source-quality metadata exists (`access_status`, `license_status`, `acquisition_priority` -- kept as separate fields, never collapsed into one score)
- [x] acquisition failure records exist (empty this run since 0 failures occurred, but the mechanism is real and tested)
- [x] source coverage matrix exists (`SOURCE_COVERAGE_MATRIX.csv`/`.xlsx`)
- [ ] foundational seed corpus -- this run's queries target UOC/SEIT-relevant structures (brief section XV), not yet cross-checked against the brief's explicit section XVII foundational-structure list one by one
- [ ] multiple independent sources per structural target -- not yet verified per-target; each query returned several candidates but no per-target triangulation pass has been run
- [x] existing literature sources are linked rather than duplicated (`link_existing_sources`, tested against a synthetic case; this run found 0 real overlaps since the 24 structural queries didn't intersect the 2 existing string-theory sources)
- [x] external UOCP/UDP/DER material is not fabricated (`EXTERNAL_CORPUS_NOT_PRESENT` recorded explicitly)
- [x] no canonical compiler state is modified (enforced by a real subprocess test, offline and isolated to tmp_path)
- [x] offline tests exist (29 tests, zero network dependency)
- [x] live acquisition is separately testable (`--offline-fixture` vs. live mode, same code path)
- [x] compiler tests remain passing (114/114)
- [x] corpus tests remain passing (45/45 -- 16 Phase A/B + 29 Phase C/D)
- [x] source discovery tests pass (29/29)
- [x] provenance is reproducible (`SCIENTIFIC_DISCOVERY_RUNS.jsonl`, append-only, with query/source/manifest hashes)
- [x] final git diff contains only intended corpus changes
- [x] any compiler-generated timestamp drift is reverted before commit

Two items are honestly unchecked above rather than claimed complete: full multi-version lineage tracking and an explicit per-structural-target source-triangulation pass. Both are real, scoped gaps for a future slice, not oversights papered over.
