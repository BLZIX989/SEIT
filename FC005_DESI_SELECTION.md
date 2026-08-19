# FC-005 DESI Data Selection

## Canonical selection

```
DESI release       = DR1
LSS version         = v1.5
tracer               = LRG (Luminous Red Galaxies)
cap                  = SGC (South Galactic Cap)
redshift range       = 0.4 < z < 1.1  (documented tracer range; verified in-file: [0.4003, 1.0989] on a 5000-row sample)
catalog file          = LRG_SGC_clustering.dat.fits
catalog version hash  = sha256 ae478557d9ef70257cc689197052515f5ebbc0b23359c81159a8ad3289332e69
random catalog         = LRG_SGC_0_clustering.ran.fits -- located, NOT downloaded for the pilot (see "Randoms" below)
selection rationale    = single well-defined tracer with the largest, cleanest overlap
                         with the FC-005 target range 0.1<=z<=1.1; smallest cap (SGC) for
                         a lean first execution.
```

All downstream pilot calculations use this exact file. No version mixing.

## Why LRG, and why not the full 0.1-1.1 range from one tracer

DESI DR1 assigns disjoint tracers to disjoint redshift ranges by design
(arXiv:2411.12020, "DESI 2024 II: Sample Definitions, Characteristics,
and Two-point Clustering Statistics"):

| tracer | documented range | overlap with FC-005 target (0.1-1.1) |
|---|---|---|
| BGS | 0.1 < z < 0.4 | low-z edge only |
| **LRG** | **0.4 < z < 1.1** | **majority of the range, single tracer** |
| ELG | 0.8 < z < 1.6 | overlaps LRG's upper end, extends past 1.1 |
| QSO | 0.8 < z < 2.1 | overlaps LRG's upper end, extends well past 1.1 |

No single DESI DR1 tracer covers the entire 0.1-1.1 window. The build
command explicitly prefers "a single well-defined tracer/redshift bin"
for the first execution and defers a multi-tracer extension to a
separate design step. LRG is the tracer whose range best satisfies that
preference — the largest single-tracer overlap, and a higher-density
sample than QSO at comparable redshift (favorable for the discrete
graph construction). BGS and QSO were evaluated (see
`FC005_DESI_CATALOG_MANIFEST.json`) and not selected for the reasons in
the table above; a BGS pilot for the 0.1-0.4 window is a natural
follow-up, kept separate rather than combined here.

NGC (North Galactic Cap) was evaluated and not selected purely for size
— same tracer, same selection function, ~2.2x larger file (143 MB vs
64 MB) — appropriate for the full run, not the pilot.

## Version selection: v1.5 over v1.2

The official DR1 release page does not state an explicit "use v1.5"
recommendation; it points to Appendix B of the DESI DR1 BAO papers
for version differences and recommends, generically, using files with
`clustering` in their names. In the absence of an explicit statement,
the selection is based on direct evidence gathered by inspecting both
versions' file headers (via HTTP range requests, no download):

| | v1.2 | v1.5 |
|---|---|---|
| `LRG_SGC_clustering.dat.fits` size | 74.87 MB | 64.27 MB |
| row count | 662,468 | 662,492 |
| columns | ...,`WEIGHT_SN`, `WEIGHT_FKP`, `WEIGHT_RF`, `WEIGHT_ZFAIL`, `WEIGHT_SYS`, `WEIGHT`, `WEIGHT_COMP`, `NX` | ...,`WEIGHT_ZFAIL`, `WEIGHT_SYS`, `WEIGHT`, `WEIGHT_COMP`, `NX`, `WEIGHT_FKP` |
| extra veto-mask variant files | not present | `*_HPmapcut.ran.fits` present |
| directory last-modified | 11-Feb-2025 21:38 | 11-Feb-2025 22:54 (later) |

Real, verified differences: v1.2 carries two additional systematic-weight
columns (`WEIGHT_SN`, `WEIGHT_RF`) that v1.5 does not; v1.5 instead
consolidates systematics into a single refined `WEIGHT_SYS` and adds an
additional HEALPix-map-cut veto variant of the randoms not present in
v1.2. The small row-count difference (24 objects) is consistent with a
refined veto mask. v1.5 is later, is not missing anything v1.2 has that
this pipeline uses (`RA`, `DEC`, `Z`, `WEIGHT`, `WEIGHT_FKP`, `WEIGHT_SYS`
are present in both), and shows evidence of a refinement pass. **v1.5 is
selected as canonical for FC-005.** If a future cross-version validation
is performed, it must be run explicitly and recorded separately (per the
build command) rather than silently mixing files from both versions.

## Randoms

**Not downloaded for the pilot phase**, and this is a documented,
deliberate decision, not an omission:

FC-005's `G_DESI` construction (`compiler/backends/desi_graph.py`,
`compiler/backends/desi_fc005_pipeline.py`) builds a kernel-weighted
graph directly on the DATA catalog's point positions (`RA`, `DEC`,
comoving `z`) and tests whether the resulting normalized graph Laplacian
converges to a continuum operator under (N, epsilon) refinement. This is
a property of the point set and the operator, and does not require a
Landy-Szalay-style DD/DR/RR pair-count estimator, which is where a
random catalog is normally indispensable (correlation function, power
spectrum). For that specific mathematical question, no random catalog is
required, and none was invented or substituted.

This does **not** mean randoms are irrelevant to FC-005. The survey
footprint has real edges, and a kernel graph built without any
mask-awareness will see galaxies near the footprint boundary as
having anomalously few neighbors — indistinguishable, from the graph's
perspective, from a genuine physical boundary (exactly the risk flagged
in the build command's mask section). The random catalog is the
standard way to characterize that footprint. It is therefore recorded
in the manifest as a **required dependency of the full (non-pilot) run**
(`FC005_DESI_CATALOG_MANIFEST.json`, role `RANDOM_CATALOG_DEFERRED`,
520.78 MB for one realization), to be acquired before any full-catalog
mathematical-convergence claim is made — not before the pilot, whose
only job (per the build command) is to test that `D_DESI -> G_DESI ->
L_DESI` executes and produces a well-formed operator (symmetric,
correctly normalized, sane connectivity) on a real subset of real data.

## Redshift sub-binning

The single `LRG_SGC_clustering.dat.fits` file spans the full 0.4-1.1
range; DESI's own BAO/RSD analyses further split LRG into three disjoint
bins (0.4-0.6, 0.6-0.8, 0.8-1.1) as an analysis-time cut on this same
file, not as separate files. The pilot in this build applies the
0.4 < z < 0.6 cut (the lowest LRG bin, smallest object count) to keep
the first `G_DESI` construction lean; the full run can sweep the other
two bins using the same downloaded file, no re-download required.
