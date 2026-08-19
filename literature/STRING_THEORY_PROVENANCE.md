# String Theory Provenance Report

Part XI of the L0-ST specification (companion to the root-level `L0_PROVENANCE_REPORT.md` from
the prior L0 phase, scoped to this phase's string-theory corpus only).

## Source identity, independently verified

Both acquired PDFs were opened and their title pages read directly (not assumed from filename or
URL) before any extraction began:

- `tong_string_theory_arxiv.pdf` — first page reads "arXiv:0908.0333v3 [hep-th] 23 Feb 2012 /
  String Theory / University of Cambridge Part III Mathematical Tripos / David Tong". 218 pages
  confirmed via `pypdf.PdfReader`.
- `kiritsis_intro_superstring_arxiv.pdf` — first page reads "CERN-TH/97-218 / hep-th/9709062 /
  INTRODUCTION TO SUPERSTRING THEORY / Elias Kiritsis / Theory Division, CERN". 249 pages
  confirmed via `pypdf.PdfReader`.

## Hash provenance

Both `SHA256` values in `literature/manifests/LITERATURE_DOWNLOAD_MANIFEST.json` and
`STRING_THEORY_CORPUS_MANIFEST.json` were computed directly from the downloaded bytes
(`hashlib.sha256`) immediately after download, before any further processing — not estimated,
not copied from any external listing.

## Extraction provenance

Every one of the 25 records in `literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json`
carries `SOURCE_ID`, `PAGE`, `CHAPTER`, `SECTION`, `SUBSECTION` (where applicable), and
`EQUATION_NUMBER` fields taken directly from the equation numbering printed in the source PDF
itself (Tong's `(1.1)`-style numbering; Kiritsis's `(3.1.1)`-style numbering) — never
renumbered, paraphrased into a different numbering scheme, or inferred. Where a formula in the
source is unnumbered (e.g. Tong's oscillator mode-expansion formulas, p.25-27), the record says
so explicitly (`"unnumbered (~p.25-27)"`) rather than inventing an equation number.

## Notation preservation

Per Part IV of the specification, every `SOURCE_NOTATION` field preserves the source's own
symbols exactly as printed (`X^\mu`, `g_{\alpha\beta}`, `\alpha'`, `T_{\alpha\beta}`, `L_m`,
etc.) — no translation into project notation was performed during extraction. Notation mapping,
if ever needed, is a deliberately separate, later stage, consistent with this project's existing
`SIGN_CONVENTION_REGISTRY.md` discipline (that document independently records this project's own
conventions from live code, never by importing an external source's convention silently).

## Coverage honesty (the central provenance discipline of this phase)

Every extraction record and every crosswalk row is scoped to material **actually read**:
Tong pp.1-29 (title/TOC/Introduction + full Chapter 1) and Kiritsis pp.1-23 (title/TOC/Intro +
§1-§3.3). Nothing beyond those page ranges is cited as a source for any equation, derivation, or
crosswalk classification. Where the specification's 52-item structure index (Part V) or the
branch-recovery matrix (Part VII) needed to report on unread material, the disposition is always
one of: `TOC-ONLY, not extracted`, `NOT READ THIS PHASE`, `UNDETERMINED`, or `NONE FOUND` — never
a fabricated claim of coverage. `STRING_THEORY_STRUCTURE_INDEX.csv` records 21 of 52 topics as
genuinely `PRESENT` (with equation-level backing), 4 as present only via a single passing prose
mention (not a derivation — explicitly marked as such), 1 as `NONE FOUND`, and the remaining 26
as `TOC-ONLY, not extracted`.

## No canonical interference

Confirmed via `git status`: every file this phase wrote is new (the `literature/` tree and its
subdirectories, plus `L0_LITERATURE_RECOVERY_MATRIX.csv` and this report's siblings at the repo
root). No existing `object_registry.json`, `transformation_registry.json`,
`equation_registry.json`, `calculation_registry.json`, `falsification_registry.json`,
`status_matrix.json`, or FC-005 file was modified. `compiler.run_compiler` was run once, purely
as a verification step, and its resulting timestamp-only diff was reverted before commit (same
discipline as the prior L0 phase) — see `STRING_THEORY_INGESTION_REPORT.md`'s completeness audit.

## Rejected-source cross-reference

No rejected source was ingested this phase (unlike the prior L0 phase's Hashimoto document). Both
Tong and Kiritsis are established, mainstream physics sources (Cambridge Part III lecture notes;
CERN preprint later published by Leuven University Press) with no fabricated units, no reverse-
fitted free parameters, and no rejection of established physics without rigorous derivation —
none of the disqualifying red flags from the prior phase's vetting discipline apply here.
