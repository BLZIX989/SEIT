# FC-005 DESI Data Acquisition Report

Real DESI DR1 public data was acquired from the official release, validated,
and executed through Gate 1. Nothing here is fabricated, synthetic, or
substituted from a compressed statistic (P(k), ξ(r), BAO products).

## A. Which DESI catalog version was selected?

**v1.5** (DR1, LSS/iron/LSScats). See `FC005_DESI_SELECTION.md` for the
full v1.2-vs-v1.5 comparison (a real schema difference was found:
v1.2 carries `WEIGHT_SN`/`WEIGHT_RF`, v1.5 consolidates into a refined
`WEIGHT_SYS` and adds `*_HPmapcut` veto variants).

## B. Which tracer?

**LRG** (Luminous Red Galaxies), **SGC** cap (South Galactic Cap).

## C. Which redshift interval?

Full file: 0.4 < z < 1.1 (verified in-file: observed range [0.4000, 1.1000]
over all 662,492 rows). Pilot/Gate-1 execution used the 0.4 ≤ z < 0.6
sub-bin (160,150 objects).

## D. Which exact files?

- `LRG_SGC_clustering.dat.fits` (v1.5) — the data catalog, downloaded and
  used.
- `LRG_SGC_0_clustering.ran.fits` (v1.5) — the random catalog, **located
  and checksum-recorded but NOT downloaded** for this phase (see
  `FC005_DESI_SELECTION.md` "Randoms" for why it isn't required by the
  current `G_DESI` construction, and why it's a recorded dependency of a
  future mask-corrected full run).

Full URLs and checksums: `FC005_DESI_CATALOG_MANIFEST.json`.

## E. What are their sizes?

`LRG_SGC_clustering.dat.fits`: 64,272,960 bytes (64.27 MB), 662,492 rows.

## F. What columns exist?

`TARGETID, Z, NTILE, RA, DEC, PHOTSYS, FRAC_TLOBS_TILES, WEIGHT_ZFAIL,
WEIGHT_SYS, WEIGHT, WEIGHT_COMP, NX, WEIGHT_FKP` — read directly from
the file header via `astropy.io.fits`, not assumed.

## G. Which weights are used?

`WEIGHT` (combined clustering weight, used for the kernel graph's
edge weighting `W_ij *= w_i*w_j`), `WEIGHT_FKP` and `WEIGHT_SYS`
(loaded and mapped, available for future estimators). See
`compiler/backends/desi_schema.py::SCHEMA_MAP`.

## H. Is a random catalog required?

Not for the current `G_DESI` construction (a kernel graph built directly
on data-point positions, no DD/DR/RR pair-count estimator). It **is**
recorded as a required dependency of a future survey-mask-boundary
correction before any full-catalogue closure claim — see
`FC005_DESI_SELECTION.md` "Randoms" for the complete justification. Not
invented, not silently skipped.

## I. Is an angular mask required?

Not applied in this phase. `PHOTSYS`, `NTILE`, and `FRAC_TLOBS_TILES`
(mask/completeness fields) were confirmed present in the catalog and
loaded into the canonical `D_DESI` table, but no explicit boundary
correction was implemented — the pilot and Gate-1 phases test graph
*construction* correctness and mathematical convergence, not
mask-deconvolved closure. This is a recorded limitation of the current
run, not a silent omission: the fields needed for it are already loaded
and available.

## J. Has the data been validated?

**Yes — 12/12 checks PASSED.** `FC005_DESI_VALIDATION_REPORT.md` /
`FC005_DESI_SCHEMA_REPORT.json`: FITS opens, expected HDUs present,
required columns present, valid dtypes, object count matches manifest
(662,492), RA/DEC/Z/weights all finite (zero NaN/Inf), redshifts fall
within the documented LRG range, 0 duplicate TARGETIDs, mask fields
present, no out-of-range RA/DEC contamination.

## K. Has G_DESI been successfully constructed?

**Yes.** Both in the small committed pilot fixture (3000 real objects,
`data/desi/dr1/fc005/validated/pilot_fixture/`) and in a larger sweep
(N up to 4000) on the full downloaded catalog. Verified: W symmetric,
non-negative, zero diagonal; single connected component; degree
distribution recorded; sparsity ~43% at the pilot's data-derived
epsilon. See `data/desi/dr1/fc005/derived/pilot_run_result.json`.

## L. Has L_DESI been successfully constructed?

**Yes**, at every individual (N, ε) point tested: `L = D - W` symmetric,
row-sums zero to machine precision, `v^T L v ≥ 0` confirmed over 200
random test vectors, exactly one zero eigenvalue matching the one
connected component.

## Beyond the acquisition task's stated scope: Gate 1 was also executed

Per the standing instruction on this branch ("proceed automatically
through Gate 1 ... if the data are successfully acquired and validated,
continue directly into FC-005 spectral execution"), the mathematical-
convergence gate (`compiler/backends/desi_fc005_pipeline.py::
run_mathematical_convergence`) was run on the real, validated data —
both the full downloaded catalog (N = 800, 1500, 2500, 4000) and the
small committed pilot fixture (N = 300, 600, 1000, 1500) for
reproducibility from a fresh checkout.

**Result: Gate 1 FAILED.** Relative change in the low-lying spectrum
across the refinement sequence was 0.42, 0.28, 0.41 (full catalog run)
against a pre-registered tolerance of 0.15 — it does not shrink
monotonically toward the tolerance. **Exact failed dependency:
`CONTINUUM-LIMIT-L-DESI`.**

A genuine sign-convention bug was found and fixed *during* this
execution (documented in `FC005_DESI_PROVENANCE.json` step
"eigenproblem" and inline in `desi_fc005_pipeline.py`): the workbook's
own equations define `L_tilde → Δ_h` (negative semidefinite) while the
heat-trace eigenproblem needs `Spec(-Δ_h)`. The earlier code
diagonalized `L_tilde` directly; the fix diagonalizes `-L_tilde`. This
is a correctness fix required by the equations as given, made once,
before generating the result reported above — not a parameter search
for a favorable answer, and no parameter was touched after seeing a
result.

**Per instruction, Gate 2 (curvature closure) and Gate 3 (physical
validation) were NOT entered.** No heat trace, no (a0,a1,a2) fit, no
E_κ, no κ_spectral, no Δκ was computed for DESI data. Everything past
`CONTINUUM-LIMIT-L-DESI` in the IR remains `OPEN`.

## What this does and does not mean

This is a real, negative, informative result about the specific
(N, ε) refinement sequence tested against real DESI DR1 LRG data — not
a proof that the discrete-to-continuum bridge is wrong in general. The
diagnostic evidence (`FC005_DESI_PROVENANCE.json`) shows the normalized
operator's nonzero eigenvalues are many orders of magnitude smaller than
the normalization would suggest is "order 1", consistent with the
tested ε values (136–234 Mpc, chosen from the data's own nearest-
neighbor spacing) not yet being small relative to the sample's spatial
extent — i.e. not yet deep in the asymptotic (N→∞, ε→0) regime the
continuum-limit theorem requires. Per instruction, this run was **not**
followed by a search for parameters that converge; that would be
altering the model to obtain closure. A properly-resolved sweep (much
smaller ε, much larger N, sparse/kNN methods per the build command's
own §15) is the natural next step and is explicitly **not attempted
here**.
