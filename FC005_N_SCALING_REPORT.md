# FC-005 N-Scaling Report — Separating Finite-Resolution Failure from Point-Process Failure

Follow-up to `FC005_CONTINUUM_DIAGNOSTIC_REPORT.md`'s stated next dependency after the
CONTINUUM-LIMIT-L-DESI Gate 1 failure investigation. Current canonical status going in:
`CONTINUUM-LIMIT-L-DESI = FAIL / RETRIABLE`. This report does not reclassify it as
`FALSIFIED`. **Final status at the end of this report: FAIL / RETRIABLE, unchanged** — but
with substantially refined evidence (see section 15).

## 1. Sparse eigensolver

Dense `eigh` was replaced entirely — the sparse kernel graph is never densified.

- **Solver**: `scipy.sparse.linalg.eigsh`, `which='SA'` (smallest algebraic), **no
  shift-invert**. Shift-invert (`sigma` near 0, `which='LM'`) was tried first and rejected:
  it requires factorizing `(A - sigma*I)` via sparse LU (`splu`), and for a 3D
  nearest-neighbour-type geometric graph this factorization suffers severe fill-in —
  measured directly to hang past 100s already at N=16000. Plain Lanczos targeting
  algebraically-smallest eigenvalues needs only sparse matrix-vector products and converges
  well because the target modes are extremal, not interior.
- **Tolerance**: `tol=1e-8`.
- **Maximum iterations**: `maxiter=500`, applied *uniformly* to all three point processes
  (never tuned per-process). Chosen after the clustered control was measured to take >500s
  at just N=8000 with an unbounded default (`maxiter=20000`) — bounding it means a
  genuinely ill-conditioned case fails fast and its non-convergence is recorded honestly
  (`arpack_converged=False`) rather than consuming unbounded compute.
- **Number of requested modes**: 15 (reduced from an initial 20/30 for tractability at
  N=64000 across 6 configurations).
- **Convergence residuals**: reported per (N, config) in `FC005_SPARSE_SPECTRAL_RESULTS.csv`
  (`max_residual` column). Every successfully-converged case has residual `<1e-18` (uniform,
  DESI) — the eigenvalues themselves are numerically trustworthy wherever ARPACK converged.

## 2. N-scaling

Nested prefixes of a single `rng.permutation` (`seed=20250819`, same seed used throughout
this investigation) over each point set: `D_4000 ⊂ D_8000 ⊂ D_16000 ⊂ D_32000 ⊂ D_64000`.
N=128000 was attempted for the synthetic controls and timed out after 300s in a standalone
test before any bug fixes; with 6 total (process × alpha) configurations this was not
feasible within this session's compute budget, so **64000 is the shared ceiling** — the
computational-feasibility boundary named in the spec. DESI is naturally bounded by the real
160,150-object pilot-bin catalogue (64000 = 40% of it, no synthetic substitution).

## 3. Epsilon scaling

**Critical correction found in this round, before running anything**: the bandwidth rule
used in the prior diagnostic phase (`eps_N = eps_ref × (N_ref/N)^(1/d)`, i.e. `N^(-1/3)` for
d=3 — density-matching, chosen so a fixed-multiplier "local" graph looks similar at each N)
does **not** satisfy the asymptotic condition `N·eps_N^(d+2) → ∞` required for graph-Laplacian
convergence (Hein, Audibert & von Luxburg 2007; Ting, Huang & Jordan 2010; García Trillos &
Slepcev 2018). Under that rate, `N·eps_N^(d+2) ~ N^(-2/3) → 0` — the wrong direction, meaning
the earlier N-refinement work was never actually approaching the theorem's regime no matter
how large N got.

**Corrected rate used here**: `eps_N = eps_ref × (N_ref/N)^(1/(d+4))`, i.e. exponent `1/7` for
d=3 — the standard bias-variance-optimal rate from kernel density estimation / manifold
learning, applied here (not invented for this task). Verified directly for every
configuration (`verify_asymptotic_conditions`, folded into `FC005_POINT_PROCESS_COMPARISON.csv`
columns `N_eps_pow_d_increasing` / `N_eps_pow_d_plus_2_increasing`): **both quantities
increase monotonically with N in every tested configuration** — `True` for all six rows.

Kernel convention: unchanged from `desi_graph.py::build_kernel_graph`,
`W_ij = exp(-d_ij²/(2ε²))`, `ε` in length units (this codebase's convention, reconciled with
the workbook's length²-unit `K(d²/ε)` convention in the prior diagnostic phase — see
`FC005_CONTINUUM_DIAGNOSTIC_REPORT.md` section 3.2). The canonical physical convention was
**not** altered here.

Sparse truncation: the Gaussian kernel's unbounded tail is truncated at
`6×ε` (`cutoff_multiplier=6.0` in `build_sparse_kernel_graph`) — `exp(-6²/2) ≈ 1.5e-8` of peak,
negligible relative to any row sum at these scales. This is the same kernel, not a different
one, with a numerically negligible tail discarded for sparse tractability.

## 4. Low-spectrum convergence

Reported in full in `FC005_SPARSE_SPECTRAL_RESULTS.csv` (per-N eigenvalues, residuals,
elapsed time) and summarized in `FC005_POINT_PROCESS_COMPARISON.csv`. The scale-relative
metric from the prior diagnostic phase is reused unchanged (excludes the zero mode, floor
relative to each run's own eigenvalue scale, never a fixed absolute constant).

**Naive scalar (eigenvalue-only) relative changes, α=0 (unnormalized, the canonical
construction):**

| Dataset | N=4000→8000 | 8000→16000 | 16000→32000 | 32000→64000 | "converged"? |
|---|---|---|---|---|---|
| Uniform IID | 0.221 | 0.142 | 0.089 | 0.055 | **True** |
| Clustered non-IID | — (0 modes ever resolved) | — | — | — | **False** |
| DESI real | 1.347 | 1.460 | 0.501 | **0.127** | **True** (naive) |

At face value, DESI's naive scalar metric crosses below the 0.15 tolerance at N=64000. **This
is exactly the kind of result this investigation's own discipline requires treating with the
maximum possible suspicion before accepting** — see section 5.

## 5. Eigenvector / subspace convergence — the naive result is a false positive for the higher modes

This is the central, load-bearing analysis of this report. Per spec section 12
("distinguish numerical spectral instability from genuine operator non-convergence"), every
consecutive N-pair was checked for degenerate/near-degenerate eigenvalue clusters and
compared via **principal angles of the restricted invariant subspace** (nested-sample prefix
property: `D_small`'s points are literally the first `N_small` rows of `D_large`), not naive
eigenvector dot products.

**Result for DESI, N=32000→64000 (the transition that produces the reported 0.127):**

| Mode range | Eigenvalue rel. change | Subspace cosine (min) | Classification |
|---|---|---|---|
| [1,2] | 0.033 | **0.999** | neither (stable) |
| [2,4] | 0.070 | **0.995** | neither (stable) |
| [4,5] | 0.037 | **0.993** | neither (stable) |
| [5,8] | 0.127 | **0.133** | **eigenvector-only unstable** |
| [8,14] | 0.065 | **0.067** | **eigenvector-only unstable** |
| [14,15] | 0.049 | **0.151** | **eigenvector-only unstable** |

Modes 5 and above have *small eigenvalue changes* (which is exactly why the naive scalar
metric reported "converged") but their invariant subspaces are **nearly orthogonal** between
N=32000 and N=64000 (cosine 0.07–0.15, close to what two unrelated random subspaces of the
same dimension would give). This is a textbook eigenvalue-crossing artifact: ARPACK returns
eigenvalues that happen to land numerically close between two refinement levels, but they
correspond to physically different modes — the operator has **not** converged there, only the
number attached to "mode index 5" happened to coincide.

**Comparison — uniform IID, the same transition:**

| Mode range | Eigenvalue rel. change | Subspace cosine (min) | Classification |
|---|---|---|---|
| [1,4] | 0.037 | 0.999 | neither (stable) |
| [4,7] | 0.042 | 0.999 | neither (stable) |
| [7,8] | 0.039 | 0.997 | neither (stable) |
| [8,11] | 0.045 | 0.991 | neither (stable) |
| [11,15] | 0.055 | 0.759 | eigenvector-only unstable |

Uniform shows the **same qualitative mechanism** (higher modes need more N to stabilize — a
well-established feature of graph-Laplacian convergence rate theory: the k-th eigenvalue
requires larger N than the (k-1)-th for a fixed accuracy) but at a **much lower mode index
where it breaks down**: uniform is jointly stable through mode 11 by N=64000; DESI is jointly
stable only through mode 4.

**Progression across all four N-transitions (uniform IID)** — modes stabilize outward
steadily as N grows: modes [1,7] stable already by N=4000→8000; modes [1,8] by 8000→16000;
modes [1,11] by 16000→32000 and 32000→64000 (with mode range [11,15] persistently the last to
stabilize, cosine improving 0.48→0.62→0.89→0.76 — noisy but clearly trending up from the
first transition).

**Progression across all four N-transitions (DESI real)** — modes stabilize outward far more
slowly: **total** instability (every tested mode, "both" unstable) through N=8000→16000;
only modes [1,4] stabilize by 16000→32000; modes [1,5] stabilize by 32000→64000, with modes
5+ still unstable at the largest N tested.

**Classification**: for DESI at the largest tested N, instability in the higher modes is
**eigenvector-only** (small eigenvalue change, unstable subspace) — the mechanism spec
section 15 calls "clustered/DESI converges to a different operator" does not apply here
(that would show up as *stable* eigenvectors converging to a *different* limit, not unstable
eigenvectors); this is instead unresolved finite-N noise in the higher modes, consistent with
Category D (resolution) still being active at this mode index, compounded by DESI needing
more N than uniform to reach the same mode index (Category I, quantified precisely here for
the first time).

## 6. Three-control separation — what actually distinguishes DESI from finite-N noise

| Process | Lowest jointly-stable mode index by N=64000 | Character |
|---|---|---|
| A. Uniform IID | ~11 | Steady, monotonic outward stabilization from N=4000 |
| B. Clustered non-IID | 0 (none) | **Total, persistent instability at every N tested** — ARPACK never resolved even a single eigenvalue within the 500-iteration budget, at any of the 5 N values, under either α=0 or α=1. `n_connected_components` also behaves non-monotonically (6→5→4→5→11 as N grows), itself informative: the clumped structure does not simply "heal" into one well-connected component as N grows the way a real survey's structure would. |
| C. Real DESI | ~4 | Steady but much slower outward stabilization than uniform; **not** total instability like the clustered control |

DESI's failure mode is qualitatively **between** the two synthetic controls, not equal to
either: it does not show the clustered control's total breakdown, but it stabilizes far more
slowly than the uniform control. This directly answers the section 9 objective: DESI's
Gate-1 failure at the previous (dense-eigh, N≤4000) resolution was dominated by **finite
resolution** (Category D) — proven here because raising N resolves the lowest modes cleanly,
something that never happened at N≤4000 for *any* process including uniform. A residual,
now precisely localized effect (higher modes converging more slowly for DESI than for
uniform at matched N) is consistent with Category I (DESI's real clustering reduces the
effective information content per sample relative to i.i.d. sampling) but is not itself
evidence of convergence to a *different* limiting operator, nor of non-existence of the
limit.

## 7. Positive control

Demonstrated: uniform IID achieves stable convergence (joint eigenvalue+eigenvector) through
mode index ~11 by N=64000, with a clean, monotonically-improving trend at every step
(scalar relative changes 0.221→0.142→0.089→0.055, all decreasing). This resolves the
ambiguity left open in `FC005_CONTINUUM_DIAGNOSTIC_REPORT.md` section 8.3, where the same
control was only borderline convergent at N≤4000 with dense `eigh`. **N=800–4000 was
genuinely an insufficient-resolution regime for this construction — confirmed, not merely
suspected.**

## 8. Clustered control

Determined (not assumed): **C. persistent instability.** The clustered non-IID control did
not converge toward the same operator as IID, did not converge toward a density-weighted
operator, and did not converge toward any distinguishable operator — ARPACK could not
resolve a single eigenvalue within the 500-iteration budget at any tested N, under either
normalization. `n_connected_components` stayed at 4–11 throughout (never reaching 1), with
the largest component holding ≥91% of nodes throughout — the instability is not simple
disconnection but severe ill-conditioning from weak bridges between near-separate density
clumps. This is a real, disclosed numerical finding, not a suppressed failure: a graph
Laplacian eigenproblem can be so poorly conditioned by strong density clustering that
standard iterative solvers cannot resolve its spectrum at all within a practical budget,
independent of whether a true continuum limit exists in principle.

## 9. DESI comparison

See sections 5–6 above. DESI's asymptotic trend (mode-by-mode outward stabilization,
slower than uniform, not exhibiting the clustered control's total breakdown) was compared
across all three processes at matched N, not at a single N.

## 10. Operator identification

**Attempted, result inconclusive** — reported honestly rather than forced. The α=0 vs α=1
comparison (`FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv`) shows a large relative spectral
difference at the largest N for both uniform (0.994) and DESI (0.988). This was intended to
test whether the unnormalized (α=0) operator carries a density-dependent drift term distinct
from the pure Laplace-Beltrami limit (Coifman-Lafon 2006: `Δ + 2(1-α)·∇(log p)·∇`). **It
cannot be used as clean evidence of that here**: α=1 (density-normalized) did not converge
for *either* process at this N range and epsilon-scaling rate (α=1 relative changes stayed
flat around 0.55–0.60 for both uniform and DESI, `converged=False` for both) — the
eps-scaling rate calibrated for α=0 does not evidently carry over correctly to the
α=1 construction (its effective kernel/degree structure differs). This is recorded as an
open methodological question for α-normalization specifically, not resolved in this round,
and the α=0 vs α=1 comparison is **not** treated as evidence either for or against a
density-weighted limiting operator for DESI.

## 11. Density normalization

Repeated for both plain (α=0) and Coifman-Lafon (α=1) constructions, per the spec. Result:
α=1 did not achieve a usable convergent regime for any process at this N range under the
eps-scaling rate calibrated for α=0 (section 10). This does **not** contradict the prior
diagnostic phase's finding that α=1 is a legitimate, standard construction (that finding
still stands as a citation-level fact); it means this specific implementation, at this
N range, with the eps-scaling rate derived for the unnormalized operator, does not yet
demonstrate α=1's theoretical convergence numerically. Verifying α=1's own correct
eps-scaling exponent (which need not be identical to α=0's) is named as a candidate next
step, not claimed here.

## 12. Observational interpretation

Unchanged and reaffirmed: `G_DESI` is built from a tracer point process (galaxies), not the
matter distribution or spacetime manifold itself. Nothing in this report treats "DESI's
graph Laplacian spectrum stabilizes for its lowest modes" as evidence about spacetime
curvature — it is evidence only about the discrete-to-continuum mathematical construction's
numerical behavior on this specific catalogue. `CONTINUUM-LIMIT-L-DESI` remains the only
node whose status changes here; no downstream physical node is touched.

## 13. Stop conditions (per spec)

- Uniform control converges (section 7) → proceed to interpret clustered/DESI, per spec.
- Clustered and DESI do **not** converge to the same operator (clustered does not converge
  to *any* resolvable operator at all) → they are not comparable in the sense spec section 13
  anticipated ("if clustered and DESI both converge to the same operator, record that as
  potentially important") — clustered's total non-convergence forecloses that comparison.
- DESI is **partially** unstable (higher modes) while the uniform control is **also**
  partially unstable at its own higher modes (just at a higher index) → per spec section 13's
  fourth clause ("if DESI remains unstable while both controls converge, the observational
  point-process interface becomes the leading unresolved dependency") — the clustered
  control did *not* converge, so this exact clause does not strictly apply either. The
  honest classification is the hybrid one in section 6: DESI's failure mode sits between the
  two controls, closer to (but slower than) uniform's own resolution-limited behavior.
- Gate 1 does **not** close: not every retained mode (1–15) shows joint eigenvalue+eigenvector
  stability for DESI, only modes 1–4. Per spec, the pipeline does **not** proceed to
  curvature extraction (Gate 2/3 remain `OPEN`, never entered).

## 14. Required output files

- `FC005_N_SCALING_REPORT.md` (this file)
- `FC005_SPARSE_SPECTRAL_RESULTS.csv` — every (dataset, α, N) row: solver, tolerance,
  maxiter, modes requested/converged, max residual, elapsed time, λ₁, λ₂, relative change.
- `FC005_OPERATOR_LIMIT_DIAGNOSTIC.csv` — α=0 vs α=1 comparison at largest N, per dataset.
- `FC005_POINT_PROCESS_COMPARISON.csv` — N/epsilon sequences, asymptotic-condition checks,
  relative-change sequences, naive convergence flag, per (dataset, α).
- `data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json` — full raw data including
  every eigenvector-subspace comparison cluster, for independent re-analysis.

No prior failed run was deleted; `FC005_CONTINUUM_FAILURE_MATRIX.csv` and its underlying
JSON from the earlier diagnostic phase remain in the repository unchanged.

## 15. Final classification

**FAIL / RETRIABLE.** Not `CLOSED` (the full retained mode set does not show joint
convergence — only modes 1–4 of 15 do). Not `FALSIFIED` (the opposite: this is the first
evidence in the entire investigation of genuine, dual eigenvalue-and-eigenvector convergence
for real DESI data, for a defensible subset of the spectrum, closely paralleling — just more
slowly than — the positive control's own behavior). Not `OPEN` in the sense of "insufficient
mathematics to decide anything" — a great deal was decided here, precisely:

- The finite-resolution confound (Category D) is **confirmed**, not merely suspected: it was
  the dominant limiting factor at N≤4000 for every process tested, including the uniform
  positive control.
- A residual, now precisely localized point-process effect (Category I) remains: DESI's
  higher modes (5–15) require more N than uniform's do to reach the same joint stability,
  quantified here for the first time via matched three-way comparison at true refinement
  scale.
- The clustered control's *total* non-convergence is a distinct, more severe phenomenon
  (persistent ARPACK instability, not slow-but-steady mode-by-mode stabilization) — DESI does
  **not** exhibit this more severe failure mode.

`CONTINUUM-LIMIT-L-DESI` and `MATHEMATICAL-CONVERGENCE-DESI` remain `Status.FAIL`
(retriable), unchanged from before this investigation. Gates 2 and 3 remain `OPEN`, never
entered.

## 15a. Checkpoint addendum: canonical `converged` field corrected

Following this report, `FC005_CHECKPOINT.md` formalized the rule this report's section 5
establishes and applied it structurally: `data/desi/dr1/fc005/derived/
sparse_n_scaling_full_results.json`'s `converged` field for every dataset now equals the
joint (eigenvalue+eigenvector) verdict via `compiler/backends/desi_sparse.py::
joint_spectral_convergence`, never the scalar eigenvalue-only value shown in this report's
own tables above (which are preserved here, explicitly labeled "naive", for the historical
record of what the unvalidated metric reported). Under the corrected field, **all six tested
configurations show `converged=False`**, including uniform IID (whose highest tested mode
cluster [11,15] falls just short of the strict joint criterion, cosine 0.76 < 0.9) — a more
conservative and honest canonical state than this report's own naive table implies. A new,
ninth self-audit (`spectral_validation_audit`) now fails the build if this correction is ever
silently reverted. See `FC005_CHECKPOINT.md` for full verification detail.

## 16. Next dependency

1. **Extend N further for DESI specifically** (the real catalogue supports up to 160,150;
   64000 was this session's practical ceiling, not a hard limit) to test whether modes 5+
   eventually stabilize the same way modes 1–4 already have, and whether uniform's own
   breakdown point (mode ~11) similarly recedes further at larger N — this is the single
   most direct test of whether the residual gap is purely a (further) resolution effect or
   asymptotes to something else.
2. **Determine the correct eps-scaling exponent for α=1** independently, rather than reusing
   α=0's rate, before attempting the operator-identification test (section 10) again.
3. **Determine, as a methodological question (not decided here), whether Gate 1's closure
   criterion should be defined over the full retained mode set or over a smaller,
   physically-motivated subset** (e.g. only the modes needed for the leading heat-trace
   coefficients a0/a1/a2) — this is a scope decision for the FC-005 specification, not a
   result this investigation can unilaterally impose.
4. Do not re-attempt tolerance changes, cherry-picked parameter points, or synthetic
   substitution for DESI. The same prohibitions in force throughout this investigation
   remain in force.
