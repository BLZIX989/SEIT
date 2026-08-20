# L0 Provenance Report

Part XII deliverable (companion to Part XI's provenance requirement). Every extracted equation,
derivation, definition, or validation claim used anywhere in the L0 artifacts retains complete
provenance back to its source. This report is the audit trail confirming that discipline was
followed, and states its limits honestly.

## Provenance fields carried by every extraction record

Every one of the 13 records in `LITERATURE_EXTRACTION_REGISTRY.json` carries, at minimum:
`SOURCE_ID`, `SOURCE_TITLE`, `AUTHOR`, `EDITION_OR_VERSION`, `PAGE`, `SECTION`,
`EXTRACTION_TIMESTAMP`, and a `REFERENCE_METADATA` block with `source_type`,
`extraction_coverage`, and `source_vetting`. Fields that genuinely don't apply to a given item
(`EQUATION_NUMBER`, `TABLE_NUMBER`, `FIGURE_NUMBER` — none of the 3 source documents number their
equations, tables, or figures in a way visible in the delivered pages) are recorded as `null`,
not omitted or fabricated.

## Source hash limitation (honest, not hidden)

Per Part XI's `SOURCE_HASH_IF_AVAILABLE` field: **no persistent content hash was computed for any
of the 3 source PDFs.** They were supplied as chat attachments at
`/root/.claude/uploads/e0123d40-d566-5190-a8f1-83c08a21f858/...` — ephemeral session storage, not
a permanent, independently re-fetchable location. Every extraction record's
`REFERENCE_METADATA.source_hash_if_available` explicitly says so rather than inventing a hash
value. This is a real, disclosed limitation of this reproduction chain: a future re-ingestion of
"the same" documents would need to re-verify title/author/edition/page-range identity by hand,
not by hash comparison.

## Notation preservation (Part III requirement)

Every extraction record preserves the source's own notation as written in that document — e.g.
`M^{mu nu}`, `P^mu` for Tong's Poincaré generators; `V_eff(phi)` for Ellis/Gaillard/Nanopoulos's
effective potential — rather than being silently rewritten into this project's own conventions
(compare `SIGN_CONVENTION_REGISTRY.md`, which is this project's *own* independent convention
register, built from live code, not from any external source). Notation mapping between a
source's convention and this project's is deliberately deferred to a later, separate stage (any
actual recovery-record implementation), never performed silently during extraction.

## Chain-of-custody for every downstream artifact

Per Part XIV's required arrow-chain (LITERATURE → EXTERNAL MATHEMATICS → MDCL CORRESPONDENCE →
IMPLEMENTATION GAP → PROPOSED RECOVERY → INDEPENDENT DERIVATION → TEST → VALIDATION → CANONICAL
PROMOTION), this L0 phase traverses exactly the first four arrows and stops:

1. **LITERATURE** — `LITERATURE_EXTRACTION_REGISTRY.json` (13 items, `LIT-001`..`LIT-013`).
2. **EXTERNAL MATHEMATICS → MDCL CORRESPONDENCE** — `LITERATURE_MDCL_CROSSWALK.csv` (Part IV,
   EXACT/PARTIAL/ANALOGOUS/NONE/UNDETERMINED classification against MDCL nodes) and
   `LITERATURE_IMPLEMENTATION_CROSSWALK.csv` (Part V, definition/derivation/code/test/validation
   presence check against the live repository).
3. **IMPLEMENTATION GAP** — `L0_BRANCH_BACKEND_GAP_MATRIX.csv` (Part II) and
   `BRANCH_RECOVERY_MAP.csv` (Part VI).
4. **PROPOSED RECOVERY** — `L0_PROPOSED_RECOVERY_RECORDS/RECOVERY-001.json`,
   `RECOVERY-002.json`, `RECOVERY-003.json` (Part VII), every one carrying
   `CANONICAL_STATUS: "PROPOSED"` and a `SOURCE_REFERENCE` pointing back to specific
   `LIT-###` items.

**Arrows 5–9 (INDEPENDENT DERIVATION → TEST → VALIDATION → CANONICAL PROMOTION) are explicitly
NOT taken in this phase.** No proposed recovery record's content has been independently derived,
tested, numerically validated, or promoted into `object_registry.json`,
`transformation_registry.json`, `equation_registry.json`, or `calculation_registry.json`. Every
`L0_PROPOSED_RECOVERY_RECORDS/*.json` file is, and remains, external/proposed material outside
the canonical registries.

## Rejected-source provenance (Part XI applied to a disqualified source)

`LIT-013` (Hashimoto, "Theory of Everything") retains full provenance despite being rejected —
its `REFERENCE_METADATA.source_vetting` field records the complete disqualification rationale
in-line, rather than deleting the record or silently excluding it from the registry. This
satisfies both halves of the requirement simultaneously: the instruction to read and record
*every* supplied document, and the instruction to never let a disqualified source silently
influence any downstream crosswalk or recovery artifact — verified directly: `LIT-013` does not
appear as a `SOURCE_ID` in `LITERATURE_IMPLEMENTATION_CROSSWALK.csv`, `BRANCH_RECOVERY_MAP.csv`,
or any `RECOVERY_ID` record's `SOURCE_REFERENCE` field.

## Canonical-registry non-interference (Part I / Part X cross-check)

Confirmed by direct diff: this L0 phase's file writes are additive only — new files
(`L0_BASELINE_MANIFEST.json`, `L0_BRANCH_BACKEND_GAP_MATRIX.csv`,
`LITERATURE_EXTRACTION_REGISTRY.json`, `LITERATURE_MDCL_CROSSWALK.csv`,
`LITERATURE_IMPLEMENTATION_CROSSWALK.csv`, `BRANCH_RECOVERY_MAP.csv`,
`L0_RECOVERY_PRIORITY_MATRIX.csv`, `L0_PROPOSED_RECOVERY_RECORDS/*.json`, this file, and the
sibling `L0_LITERATURE_INDEX.md` / `L0_GAP_REPORT.md` / `L0_SUMMARY.md`) plus the generation
script `generate_l0_literature_ingestion.py`. Zero existing files were modified — verified via
`git status`/`git diff` before this report's own creation (see `L0_BASELINE_MANIFEST.json`'s
`git_commit` field, which records the exact pre-L0 commit hash this phase started from, and the
final commit/push step of this phase, which re-confirms no canonical registry entry changed).
`compiler.run_compiler` was not invoked to regenerate any registry as part of producing these L0
artifacts, and FC-005's frozen status was not touched.
