# L0 Literature Acquisition Report

Part X of the L0-A specification. Answers the 15 required questions directly.

**1. Which PDFs were successfully acquired?**
Two: David Tong's *String Theory* (Cambridge Part III notes) and Elias Kiritsis's *Introduction
to Superstring Theory*.

**2. Which authoritative sources were used?**
Both from arXiv (`arxiv.org/pdf/0908.0333` for Tong; `arxiv.org/pdf/hep-th/9709062` for
Kiritsis) — arXiv is the author-deposited preprint server for both, an authoritative source for
each.

**3. Which sources failed?**
Three attempted `damtp.cam.ac.uk` (Cambridge) URLs all failed with the same root cause: Tong's
*String Theory* PDF, Tong's *Standard Model* PDF, and Tong's *Lectures on Gauge Theory* course
index page.

**4. Which mirrors were required?**
One: `arxiv.org/pdf/0908.0333` as the archival mirror for Tong's *String Theory*, explicitly
pre-authorized by the instructing message. No mirror was available or attempted for the *Standard
Model* or *Gauge Theory* documents — none was supplied.

**5. What versions were acquired?**
`arXiv:0908.0333v3` (Tong, revised 23 Feb 2012) and `arXiv:hep-th/9709062v2` (Kiritsis, 30 Mar
1998).

**6. What are their SHA256 hashes?**
Tong: `b267b9d7bb717e8e7765b202910cd464e86de290489b5a70dc27d25e07fc848c`.
Kiritsis: `7f7c2e4665c5b6148b5d3718e843aefddcbf219ce33ebba1db0264fe5dd9f4ea`.
(Full manifest: `literature/manifests/LITERATURE_DOWNLOAD_MANIFEST.json`.)

**7. How many pages does each contain?**
Tong: 218 pages. Kiritsis: 249 pages. (Verified via `pypdf.PdfReader`, not estimated.)

**8. Which mathematical subjects does each contain?**
Per each document's own Table of Contents (fully captured): Tong covers the relativistic string
(Nambu-Goto/Polyakov actions, quantization, D-branes, CFT, path-integral quantization, string
interactions, low-energy effective actions, compactification/T-duality). Kiritsis covers
classical string theory, bosonic-string quantization (covariant, light-cone, path-integral),
interactions, CFT (including superconformal N=1,2,4), CFT on the torus, superstrings and
supersymmetry, anomalies, compactification and SUSY breaking, loop corrections to couplings, and
non-perturbative dualities. **Only a fraction of each (Tong Ch.1; Kiritsis §3) was actually read
this phase** — see `literature/STRING_THEORY_INGESTION_REPORT.md` for the exact scope.

**9. Which existing MDCL branches do they map onto?**
Based on content actually read: Variational (strong), Symmetry/Conservation (strong, via the
explicit Noether-current construction), Geometry (present but explicitly the wrong
dimensionality — 2D worldsheet, not 4D spacetime), Quantum (weak/precursor only), Spectral
(present but confirmed mathematically independent of the existing graph-Laplacian branch). Full
detail: `literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv`.

**10. Which currently unimplemented branches receive useful external mathematical support?**
Variational and Symmetry/Conservation receive genuine, twice-cross-source-confirmed support (a
complete action→EOM→symmetry→Noether-current template). See
`literature/recovery/PROPOSED_STRING_VARIATIONAL_RECOVERY.md` and the two proposed recovery
records in `literature/recovery/STRING_THEORY_PROPOSED_RECOVERIES/`.

**11. Which branches remain unsupported?**
Geometry/GR (wrong-dimensionality-only support in pages read; the likely real support, Tong
§7.1, was not read), Thermodynamics (no support found anywhere in pages read or TOC), Gauge/
Standard Model (relevant chapters not read; the dedicated Cambridge documents failed to
download), Cosmology (single passing prose mention only), Quantum/Gravity interface (prose
motivation only, no derived bridge in pages read).

**12. Which proposed recoveries require independent derivation?**
Both `RECOVERY-STR-001` (Variational) and `RECOVERY-STR-002` (Symmetry/Conservation) — each
explicitly requires choosing a UOC-specific field content and Lagrangian not supplied by any
source, which is new, independent derivation work, not a literature lookup.

**13. Which require numerical validation?**
Both, per their own `UNIT_TEST_PLAN`/`NUMERICAL_TEST_PLAN` fields — neither can be numerically
tested until the independent derivation step (12) resolves.

**14. Which require observational validation?**
Neither, currently — both are purely mathematical/structural recovery targets with no
observational claim attached.

**15. Which remain genuinely open?**
Everything downstream of the unresolved `SPECTRUM-NODE`/`SELECTION-SIGMA` dependency (both
proposed recoveries are blocked on it), plus every branch listed under question 11, plus the
entire unread remainder of both source documents (189 pages of Tong, 226 pages of Kiritsis).

## Closure discipline

No claim of closure is made anywhere in this report merely because a standard result exists in
the literature. Every branch this report touches is characterized by what was actually read and
actually crosswalked, per `literature/STRING_THEORY_INGESTION_REPORT.md`'s explicit
`STATUS = INGESTION_INCOMPLETE` finding — a status honestly reported rather than upgraded to
success.
