"""FC-005 sparse-scale diagnostics: separates finite-resolution failure
from point-process failure in the CONTINUUM-LIMIT-L-DESI investigation.

Everything here is a MEASUREMENT tool, matching the discipline of
desi_diagnostics.py: corrections derived from these measurements are
applied explicitly and separately, never silently.

Kernel convention (unchanged from desi_graph.py::build_kernel_graph):
    W_ij = exp(-d_ij^2 / (2*epsilon^2)),  epsilon in LENGTH units.
Truncated to a finite cutoff radius for sparse tractability -- NOT a
different kernel, the same Gaussian kernel with negligible tail beyond
the cutoff discarded. Default cutoff_multiplier=6.0 means truncation at
6*epsilon, where exp(-6^2/2) = exp(-18) ~= 1.5e-8 of the peak value --
far below floating-point-meaningful contribution to any row sum at the
N, epsilon scales used here.

Epsilon-scaling rate (spec section 3): the rate eps_N ~ N^{-1/d} (used
by the "median heuristic, held at multiplier=1" rule in earlier phases
of this investigation) does NOT satisfy the standard asymptotic
convergence condition N*eps_N^{d+2} -> infinity required for the
normalized graph Laplacian to converge to a continuum operator (Hein,
Audibert & von Luxburg 2007; Ting, Huang & Jordan 2010; Garcia
Trillos & Slepcev 2018) -- under that rate, N*eps_N^{d+2} ~ N^{-2/3} -> 0,
the WRONG direction. The standard bias-variance-optimal rate,
eps_N ~ N^{-1/(d+4)} (same rate as in kernel density estimation /
manifold learning; d+4 -> 7 for d=3), satisfies all three required
conditions simultaneously:
    eps_N -> 0
    N * eps_N^d       -> infinity   (avg degree grows -- connectivity)
    N * eps_N^{d+2}   -> infinity   (bias term of the normalized operator vanishes)
This module scales epsilon by this corrected rate; see
epsilon_scaling_sequence() and verify_asymptotic_conditions().
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import eigsh, ArpackNoConvergence


# ---------------------------------------------------------------------
# 1. Sparse graph construction
# ---------------------------------------------------------------------

def build_sparse_kernel_graph(points: np.ndarray, epsilon: float, *,
                               weights: np.ndarray | None = None,
                               cutoff_multiplier: float = 6.0):
    """Sparse W_ij = exp(-d_ij^2/(2*eps^2)) for d_ij <= cutoff_multiplier*eps,
    0 otherwise (truncated-support approximation of the same Gaussian
    kernel used by build_kernel_graph, never densified). Returns a CSR
    matrix."""
    from scipy.spatial import cKDTree
    tree = cKDTree(points)
    cutoff = cutoff_multiplier * epsilon
    coo = tree.sparse_distance_matrix(tree, max_distance=cutoff, output_type="coo_matrix")
    row, col, dist = coo.row, coo.col, coo.data
    keep = row != col  # drop self-pairs (d=0)
    row, col, dist = row[keep], col[keep], dist[keep]
    w = np.exp(-(dist ** 2) / (2 * epsilon ** 2))
    if weights is not None:
        w = w * weights[row] * weights[col]
    n = len(points)
    W = coo_matrix((w, (row, col)), shape=(n, n)).tocsr()
    return W


def sparse_graph_laplacian(W) -> tuple[object, object]:
    deg = np.asarray(W.sum(axis=1)).flatten()
    D = diags(deg)
    L = (D - W).tocsr()
    return D, L


def alpha_normalize_sparse(W, alpha: float = 1.0):
    """Coifman-Lafon density normalization on a sparse kernel matrix:
    W'_ij = W_ij / (D_i^alpha * D_j^alpha)."""
    if alpha == 0.0:
        return W
    deg = np.asarray(W.sum(axis=1)).flatten()
    deg_safe = np.maximum(deg, 1e-300)
    scale = diags(deg_safe ** (-alpha))
    return (scale @ W @ scale).tocsr()


# ---------------------------------------------------------------------
# 2. Sparse eigensolver
# ---------------------------------------------------------------------

@dataclass
class SparseEigenResult:
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    solver: str
    sigma: float
    tol: float
    maxiter: int
    n_modes_requested: int
    max_residual: float
    converged: bool


def sparse_low_eigen(neg_L_tilde, n_modes: int, *, sigma: float | None = None,
                      tol: float = 1e-8, maxiter: int = 20000) -> SparseEigenResult:
    """Smallest n_modes eigenpairs of a sparse PSD operator (here always
    called on -L_tilde = L_N/(C_K*N*eps^(d+2)), sign convention per
    desi_fc005_pipeline.py: the eigenproblem used for the heat trace is
    Spec(-Delta_h) = Spec(-L_tilde), lambda>=0.

    Solver: ARPACK via scipy.sparse.linalg.eigsh, which='SA' (smallest
    algebraic), NO shift-invert. Shift-invert (sigma near 0, which='LM')
    was tried first and rejected: it requires factorizing (A - sigma*I)
    via sparse LU (splu), and for a 3D nearest-neighbour-type sparse
    geometric graph this factorization suffers severe fill-in and does
    not scale past a few thousand nodes in practice (measured directly:
    splu hung past 100s already at N=16000). which='SA' uses plain
    Lanczos with only sparse matrix-vector products, no factorization --
    and converges well here because the target eigenvalues (lowest few
    modes of a PSD operator) are EXTREMAL, not interior, which is
    exactly the regime plain Lanczos handles efficiently. Verified
    directly: N=16000 in ~5s, scaling tested up to N=128000."""
    n = neg_L_tilde.shape[0]
    k = min(n_modes, n - 2)
    converged = True
    try:
        vals, vecs = eigsh(neg_L_tilde, k=k, which="SA", tol=tol, maxiter=maxiter)
    except ArpackNoConvergence as exc:
        converged = False
        vals, vecs = exc.eigenvalues, exc.eigenvectors
    order = np.argsort(vals)
    vals, vecs = vals[order], vecs[:, order]
    resid = neg_L_tilde @ vecs - vecs * vals[None, :]
    max_residual = float(np.max(np.linalg.norm(resid, axis=0))) if vals.size else float("nan")
    return SparseEigenResult(
        eigenvalues=vals, eigenvectors=vecs,
        solver="scipy.sparse.linalg.eigsh (ARPACK, which='SA', no shift-invert, symmetric)",
        sigma=float("nan"), tol=tol, maxiter=maxiter,
        n_modes_requested=n_modes, max_residual=max_residual, converged=converged,
    )


# ---------------------------------------------------------------------
# 3. Epsilon-scaling (spec section 3)
# ---------------------------------------------------------------------

def epsilon_scaling_sequence(eps_ref: float, N_ref: int, N_values: list[int], *,
                              d: int = 3) -> list[float]:
    """eps_N = eps_ref * (N_ref/N)^(1/(d+4)) -- the bias-variance-optimal
    rate (see module docstring), NOT (N_ref/N)^(1/d) (density-matching,
    which violates N*eps^(d+2) -> infinity)."""
    return [eps_ref * (N_ref / n) ** (1.0 / (d + 4)) for n in N_values]


def verify_asymptotic_conditions(N_values: list[int], eps_values: list[float], *,
                                  d: int = 3) -> list[dict]:
    rows = []
    for N, eps in zip(N_values, eps_values):
        rows.append({
            "N": N, "epsilon_N": eps,
            "N_times_eps_pow_d": N * eps ** d,
            "N_times_eps_pow_d_plus_2": N * eps ** (d + 2),
        })
    increasing_d = all(rows[i + 1]["N_times_eps_pow_d"] > rows[i]["N_times_eps_pow_d"]
                        for i in range(len(rows) - 1))
    increasing_d2 = all(rows[i + 1]["N_times_eps_pow_d_plus_2"] > rows[i]["N_times_eps_pow_d_plus_2"]
                         for i in range(len(rows) - 1))
    eps_decreasing = all(eps_values[i + 1] < eps_values[i] for i in range(len(eps_values) - 1))
    for row in rows:
        row["eps_decreasing_overall"] = eps_decreasing
        row["N_eps_d_increasing_overall"] = increasing_d
        row["N_eps_d_plus_2_increasing_overall"] = increasing_d2
    return rows


# ---------------------------------------------------------------------
# 4. Scale-relative low-spectrum convergence (spec section 4)
# ---------------------------------------------------------------------

def relative_changes_scaled(low_eigs: list[np.ndarray]) -> list[float]:
    """Same corrected metric used throughout this investigation: excludes
    the zero mode, floor relative to each run's own eigenvalue scale --
    never a fixed absolute constant (see FC005_CONTINUUM_DIAGNOSTIC_REPORT.md
    section 3.1 for the bug this fixes)."""
    out = []
    for i in range(len(low_eigs) - 1):
        prev, curr = low_eigs[i][1:], low_eigs[i + 1][1:]
        n = min(len(prev), len(curr))
        prev, curr = prev[:n], curr[:n]
        scale = float(np.mean(np.abs(prev))) if n else 1e-300
        floor = max(scale * 1e-6, 1e-300)
        denom = np.maximum(np.abs(prev), floor)
        out.append(float(np.max(np.abs(curr - prev) / denom)))
    return out


# ---------------------------------------------------------------------
# 5. Eigenvector / subspace convergence (spec section 5)
# ---------------------------------------------------------------------

def eigenvector_subspace_comparison(vecs_small: np.ndarray, vecs_large: np.ndarray,
                                     n_small: int, vals_small: np.ndarray,
                                     vals_large: np.ndarray, *,
                                     degeneracy_rel_gap: float = 0.15) -> list[dict]:
    """vecs_large's first n_small rows correspond exactly to the same
    points as vecs_small (nested-sample prefix property: D_small is a
    literal prefix of D_large's point ordering). Groups near-degenerate
    modes (relative eigenvalue gap < degeneracy_rel_gap, scale-relative)
    and compares via principal angles (subspace) rather than raw
    eigenvector dot products when degenerate; plain cosine similarity
    otherwise."""
    k = min(vecs_small.shape[1], vecs_large.shape[1], len(vals_small), len(vals_large))
    vecs_small, vecs_large = vecs_small[:, :k], vecs_large[:n_small, :k]
    vals_small, vals_large = vals_small[:k], vals_large[:k]

    scale = float(np.mean(np.abs(vals_small[1:]))) if k > 1 else 1.0
    scale = max(scale, 1e-300)

    # group into degeneracy clusters using vals_small's spacing
    clusters = []
    start = 1  # skip zero mode
    for i in range(2, k):
        if abs(vals_small[i] - vals_small[i - 1]) / scale > degeneracy_rel_gap:
            clusters.append((start, i))
            start = i
    if start < k:
        clusters.append((start, k))

    rows = []
    for (a, b) in clusters:
        Vs = vecs_small[:, a:b]
        Vl = vecs_large[:, a:b]
        # re-orthonormalize the restricted (row-truncated) large-N block
        Vl_q, _ = np.linalg.qr(Vl)
        Vl_q = Vl_q[:, :Vl.shape[1]]
        cross = Vs.T @ Vl_q
        svals = np.linalg.svd(cross, compute_uv=False)
        principal_cos_min = float(np.min(svals)) if len(svals) else float("nan")
        eig_rel_change = float(np.max(np.abs(vals_large[a:b] - vals_small[a:b]) /
                                       np.maximum(np.abs(vals_small[a:b]), scale * 1e-6)))
        eig_unstable = eig_rel_change > 0.15
        vec_unstable = principal_cos_min < 0.9
        if eig_unstable and vec_unstable:
            classification = "both"
        elif eig_unstable:
            classification = "eigenvalue-only"
        elif vec_unstable:
            classification = "eigenvector-only"
        else:
            classification = "neither"
        rows.append({
            "mode_range": [int(a), int(b)], "is_degenerate_cluster": (b - a) > 1,
            "eigenvalue_relative_change": eig_rel_change,
            "subspace_principal_cosine_min": principal_cos_min,
            "classification": classification,
        })
    return rows


# ---------------------------------------------------------------------
# 6. Operator identification (spec section 10) -- diagnostic candidate only
# ---------------------------------------------------------------------

def operator_identification(low_eigs_alpha0: np.ndarray, low_eigs_alpha1: np.ndarray) -> dict:
    """Compares the largest-N spectrum under alpha=0 (unnormalized,
    theoretically Delta + 2*grad(log p).grad per Coifman-Lafon 2006) vs
    alpha=1 (density-normalized, theoretically pure Delta) for the SAME
    point process. A persistent, non-noise difference between the two
    spectra at the largest tested N is direct numerical evidence the
    alpha=0 operator carries a density-dependent term beyond pure
    Delta_h -- exactly the pre-existing Coifman-Lafon derivation, not a
    new physical law. This function only reports the numerical
    comparison; it does not assert which schematic term is present."""
    n = min(len(low_eigs_alpha0), len(low_eigs_alpha1))
    a0, a1 = low_eigs_alpha0[1:n], low_eigs_alpha1[1:n]
    scale = max(float(np.mean(np.abs(a0))), 1e-300)
    rel_diff = float(np.max(np.abs(a0 - a1) / np.maximum(np.abs(a0), scale * 1e-6)))
    return {
        "n_modes_compared": n - 1, "relative_spectral_difference_alpha0_vs_alpha1": rel_diff,
        "interpretation": (
            "alpha=0 and alpha=1 spectra differ substantially at the largest tested N -- "
            "consistent with (not proof of) the unnormalized operator retaining a "
            "density-dependent term distinct from pure Delta_h, per the pre-existing "
            "Coifman-Lafon (2006) derivation Delta + 2*(1-alpha)*grad(log p).grad"
            if rel_diff > 0.15 else
            "alpha=0 and alpha=1 spectra agree at the largest tested N -- no numerical "
            "evidence of a density-dependent term distinguishing the two operators at "
            "this resolution"
        ),
    }
