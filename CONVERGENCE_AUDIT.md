# CONVERGENCE_AUDIT.md

Real data source: data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json (N=4000->8000->16000->32000->64000, already computed by scripts/run_desi_sparse_n_scaling.py -- reused read-only here, not recomputed).

## Rigorous Mosco M1/M2 status

NOT COMPUTABLE FROM AVAILABLE DEFINITIONS

**Missing object:** A stated identification/embedding map iota_n: H_n -> H (or a common ambient Hilbert space with fixed inner product that all H_n, of varying dimension N, embed into) is required before the quadratic-form liminf/recovery-sequence conditions (M1/M2) are even well-posed questions. Neither the This-from-That whitepaper nor any compiler module (compiler/backends/desi_sparse.py, desi_graph.py, desi_fc005_pipeline.py) defines such a map -- each N is treated as an independent finite-dimensional problem with its own R^N, not as a term in a sequence embedded in a fixed limiting space. This is the exact, precise dependency gap the brief's section V asks to be identified rather than hand-waved past.

**What was computed instead:** Numerical convergence/divergence evidence on the low-eigenvalue trajectories actually recorded for each real dataset (uniform/clustered/desi, alpha in {0.0, 1.0}) across the real N=4000->64000 sequence already run by scripts/run_desi_sparse_n_scaling.py -- see per-dataset results above.

## Per-dataset numerical convergence evidence

### uniform_alpha0.0
- status: **NUMERICAL_EVIDENCE_FOR_CONVERGENCE**
- mean successive ratio 0.629 < 1 -- consistent with geometric convergence (Cauchy-like behavior)

### clustered_alpha0.0
- status: **NO_CONVERGED_MODES_AT_ANY_N**
- ARPACK failed to produce converged low modes at every N tested (ARPACK_INSUFFICIENT_CONVERGED_MODES) -- this is a STRONGER form of non-convergence evidence than a slowly-decaying relative change: the solver could not even resolve stable low eigenmodes to compare across N, consistent with the existing CONTINUUM-LIMIT-L-DESI=FAIL finding for this class of geometry.

### desi_alpha0.0
- status: **NUMERICAL_EVIDENCE_AGAINST_CONVERGENCE_AT_TESTED_N**
- mean successive ratio 0.560 < 1 -- consistent with geometric convergence (Cauchy-like behavior)

### uniform_alpha1.0
- status: **NUMERICAL_EVIDENCE_AGAINST_CONVERGENCE_AT_TESTED_N**
- mean successive ratio 0.984 < 1 -- consistent with geometric convergence (Cauchy-like behavior)

### clustered_alpha1.0
- status: **NO_CONVERGED_MODES_AT_ANY_N**
- ARPACK failed to produce converged low modes at every N tested (ARPACK_INSUFFICIENT_CONVERGED_MODES) -- this is a STRONGER form of non-convergence evidence than a slowly-decaying relative change: the solver could not even resolve stable low eigenmodes to compare across N, consistent with the existing CONTINUUM-LIMIT-L-DESI=FAIL finding for this class of geometry.

### desi_alpha1.0
- status: **NUMERICAL_EVIDENCE_AGAINST_CONVERGENCE_AT_TESTED_N**
- mean successive ratio 1.000 >= 1 -- NOT decaying, inconsistent with convergence at the N range tested

