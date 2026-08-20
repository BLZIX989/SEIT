# L0 Literature Index

Part XII deliverable. Index of every document supplied to this L0 literature-ingestion phase,
with its vetting outcome. Full per-item extraction is in `LITERATURE_EXTRACTION_REGISTRY.json`
(13 items, `LIT-001`..`LIT-013`); this file is the human-readable index over that registry.

## Source 1 — `LIT-TONG-SM` — ACCEPTED

**"The Standard Model"** — David Tong, Part III Mathematical Tripos lecture notes, University of
Cambridge.

- **Vetting**: ACCEPTED. Established author, standard graduate-level QFT/particle-physics
  content, internally consistent with mainstream physics, no red flags.
- **Coverage delivered**: Introduction + full Chapter 1 ("Symmetries"), through section 1.4.4
  (the CPT theorem), ending page 47. The table of contents shows Chapters 2–7 exist (Broken
  Symmetries/Higgs Mechanism, The Strong Force, Anomalies, Electroweak Interactions, Flavour,
  Neutrinos) but their content was **not** included in the delivered attachment.
- **Items extracted**: `LIT-001` through `LIT-006` (6 items — Introduction/scope, Poincaré
  group, Weyl/Dirac spinors, discrete symmetries C/P/T, CPT theorem, and a table-of-contents-only
  record for the undelivered chapters).
- **Relevance**: primary candidate source for the Symmetry and Quantum branches (group-theoretic
  and spinor-representation structure); topically relevant to Gauge/SM but the delivered pages
  don't yet reach the gauge-theory chapters.

## Source 2 — `LIT-EGN-HIGGS` — ACCEPTED

**"A Historical Profile of the Higgs Boson"** — John Ellis, Mary K. Gaillard, Dimitri V.
Nanopoulos. Chapter 14 of *The Standard Theory of Particle Physics* (World Scientific, 2016),
Open Access, CC BY-NC 4.0.

- **Vetting**: ACCEPTED. Mainstream academic press, established authors, internally consistent
  historical/phenomenological review.
- **Coverage delivered**: full chapter, 20 pages (pp. 255–274 of the source book, references
  included).
- **Items extracted**: `LIT-007` through `LIT-012` (6 items — pre-1964 SSB context, the 1964
  Higgs papers, electroweak unification, search history/2012 discovery, property
  verification/vacuum stability, BSM alternatives and open questions).
- **Relevance**: primary candidate source for the Gauge/Standard-Model branch's Higgs-mechanism
  content; tangential relevance to Early-universe/Cosmology via its vacuum-stability/inflation
  discussion in the open-questions section.

## Source 3 — `LIT-HASHIMOTO-TOE` — REJECTED

**"Theory of Everything"** — Junichi Hashimoto. *Journal of Innovations in Energy Science*
(ScholArena).

- **Vetting**: **REJECTED**, per this campaign's own Part I.3 prohibition against "fit[ting] the
  desired physical result and then declar[ing] it recovered" / "promot[ing] a numerical
  coincidence to a derivation." Specific findings:
  1. Invented, non-standard units ("Gp"/Galapagos, "Skr"/Sakura) with no traceable definition to
     SI or any recognized unit system.
  2. A self-named free parameter (the "Junichi Parameter," `J`) and an integer `n`, together with
     an ad hoc constraint `x+y=13`, whose values are **not derived** but **chosen after the
     fact** — specifically so that the computed mass/volume/ionization-energy for each of 9 test
     objects (hydrogen atom, electron, Japanese kilogram prototype, bowling ball, Earth, Moon,
     Sun, Venus, Jupiter) matches the already-known measured value.
  3. Rejection of finite light speed, gauge-boson exchange, and Newtonian gravitation via
     informal "relational physics"/"clockwork organism" reasoning, with no rigorous derivation
     replacing them.
- **Items extracted**: `LIT-013` (1 item, retained per the instruction to read *all* supplied
  PDFs, but flagged `SOURCE_VETTING=REJECTED` throughout).
- **Disposition**: excluded from every downstream artifact — `LITERATURE_MDCL_CROSSWALK.csv`,
  `LITERATURE_IMPLEMENTATION_CROSSWALK.csv`, `BRANCH_RECOVERY_MAP.csv`, and
  `L0_PROPOSED_RECOVERY_RECORDS/` — none of them cite `LIT-013` as support for anything. This is
  a documented exclusion, not a silent omission.

## Summary table

| Source ID | Title | Vetting | Items | Used downstream? |
|---|---|---|---|---|
| `LIT-TONG-SM` | The Standard Model (Tong) | ACCEPTED | LIT-001..006 | YES |
| `LIT-EGN-HIGGS` | A Historical Profile of the Higgs Boson (Ellis/Gaillard/Nanopoulos) | ACCEPTED | LIT-007..012 | YES |
| `LIT-HASHIMOTO-TOE` | Theory of Everything (Hashimoto) | **REJECTED** | LIT-013 | NO (recorded only) |

## What this corpus does and does not cover

Covered (at least partially): Symmetry (Lorentz/Poincaré group structure), Quantum (spinor
representations), Gauge/Standard Model (Higgs mechanism, electroweak unification).

**Not covered by any of the 3 documents**: differential geometry / General Relativity, classical
mechanics / variational principle foundations, thermodynamics, early- or late-universe evolution
equations (Friedmann equations), information geometry / Fisher-Rao statistical structure beyond
what this repository has already independently derived, and discrete-graph-to-continuum
convergence theory (the FC-005/DESI branch). This is recorded explicitly in
`L0_GAP_REPORT.md` rather than glossed over.
