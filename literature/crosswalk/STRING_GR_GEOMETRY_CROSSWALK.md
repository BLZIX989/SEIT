# String Theory → GR / Geometry Crosswalk

Part IX of the L0-ST specification. Explicitly checks whether the ingested corpus DERIVES the
chain worldsheet geometry → target-space geometry → effective spacetime metric → curvature →
Einstein equations → low-energy effective action → supergravity, or merely states pieces of it.

## What was actually read

Only worldsheet geometry (Tong §1.2–1.3, Kiritsis §3.2, items `ST-005` through `ST-011`,
`ST-016`, `ST-018`–`ST-020` in `STRING_THEORY_LITERATURE_REGISTRY.json`) was read this phase.
This is the induced/dynamical metric on the **2-dimensional worldsheet** the string sweeps out —
`γ_αβ = ∂_α X^μ ∂_β X^ν η_μν` (Tong eq. 1.12) or the independent Polyakov metric `g_αβ` (Tong eq.
1.22) — parametrizing a map `X^μ(σ,τ)` from the worldsheet into a **fixed, flat, non-dynamical**
Minkowski target space `η_μν`. Nowhere in the pages read is the target-space metric `η_μν`
itself made dynamical, varied, or shown to obey any Einstein-like field equation.

## The chain, checked link by link

| Link | Present in pages read? | Evidence / gap |
|---|---|---|
| Worldsheet geometry | **YES** | `ST-005`, `ST-009`, `ST-011`, `ST-016`, `ST-018` — genuine, derived 2D geometry (induced metric, Weyl-transform-to-flat, 2D Riemann-tensor decomposition `R_αβγδ=(R/2)(g_αγg_βδ−g_αδg_βγ)`) |
| Worldsheet geometry → target-space geometry | **NOT ESTABLISHED IN PAGES READ** | The target metric `η_μν` is fixed and flat throughout every equation read this phase; nothing promotes it to a dynamical field |
| Target-space geometry → effective spacetime metric | **NOT READ** | Would require Tong §7 "Low Energy Effective Actions" (p.157–195, specifically §7.1 "Einstein's Equations," p.158) — table-of-contents only, not extracted |
| Effective spacetime metric → curvature | **NOT READ** | Same chapter, not read |
| Curvature → Einstein equations | **NOT READ** | Same chapter; Tong's own TOC line "7.1 Einstein's Equations" confirms the *destination* of this chain exists somewhere in this source, but its content and derivation were not extracted this phase |
| → low-energy effective action | **NOT READ** | Tong §7.3 "The Low-Energy Effective Action" (p.167+), Kiritsis §9 "Strings in background fields and low-energy effective actions" (p.102+) — both TOC-only |
| → supergravity | **NOT READ** | Kiritsis Appendix D (p.221+) — TOC-only |

## Explicit non-collapse statement

Per this campaign's standing rule and the L0-ST specification's own Part IX instruction:

**worldsheet geometry ≠ target-space geometry ≠ spacetime geometry**

unless the source explicitly establishes the mathematical mapping. The pages read this phase do
**not** establish that mapping — they only work with worldsheet geometry, and the target
spacetime is held fixed and flat throughout. `STRING_THEORY_MDCL_CROSSWALK.csv` accordingly
records `STRUCTURAL_CORRESPONDENCE = NONE` for any attempted crosswalk between `ST-011`
(worldsheet 2D geometry) and `GEOMETRY-NODE` (which needs 4D target-spacetime curvature). This is
a **negative but genuine finding**, not a gap glossed over: even a source that indisputably
contains real, derived differential geometry does not automatically supply what `GEOMETRY-NODE`
needs, because it is the *wrong* geometry (2D worldsheet, not 4D spacetime).

## What would be needed to actually check this chain

Reading Tong §7 (specifically §7.1 "Einstein's Equations" and §7.1.1 "The Beta Function," which —
per the chapter's own title in the TOC — is presumably where the worldsheet Weyl-anomaly
cancellation condition is shown to imply the target-space Einstein equations as a *consistency
condition of the 2D quantum theory*, the standard route by which string theory is known in the
broader literature to relate worldsheet physics to spacetime gravity) was not performed this
phase and is flagged as the single highest-priority unread section for any future, deeper
GR/Geometry crosswalk attempt.

## Conclusion

`GEOMETRY-NODE` and the `GR` branch receive **no usable literature support** from this ingestion
phase's actually-read content. The corpus almost certainly contains the relevant derivation
(§7.1's very title names it), but it was not read this phase, so nothing from it may be recorded
as extracted, crosswalked, or used as a recovery source — consistent with Part XI's provenance
requirement and Part XV's external-status firewall.
