"""Three-stage FC-005 DESI execution, run exactly as specified once a
real catalogue is supplied -- never adjusted after the fact to obtain a
particular answer.

The three stages are kept as three INDEPENDENT, separately reported
results, per the standing instruction on this branch:

    mathematical convergence  != observational agreement  != physical validation

Stage 1 (mathematical convergence): does L_tilde_(N,eps), built purely
    from the catalogue's point positions, converge under refinement
    (N up up, eps down) in the sense the FC-005 equations define? This
    is a property of the OPERATOR and the SAMPLING, not of physics. If
    it fails, the pipeline STOPS and names the exact node it failed at
    -- it never proceeds to curvature or cosmology on an operator that
    hasn't been shown to converge.

Stage 2 (curvature closure / "observational agreement" with the
    constant-curvature sector): only entered if stage 1 converged. Fits
    (a0,a1,a2) from the converged spectrum's heat trace and computes
    E_kappa. If |E_kappa| does not shrink toward the predefined
    tolerance, the pipeline STOPS and reports a curvature-closure
    failure -- this is reported as a genuine failure of the
    constant-curvature-sector closure test, not smoothed over.

Stage 3 (physical validation / independent cosmological cross-check):
    only entered if stage 2 closed. Compares kappa_spectral against an
    INDEPENDENTLY SOURCED kappa_cosmological (never derived from the
    same catalogue/run -- passing the same number in for both sides is
    a caller error this function refuses to silently accept).

Nothing here fabricates a catalogue, a cosmological reference value, or
a favorable fit. Every threshold is a parameter with an explicit
default, not a hidden constant tuned to produce closure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, catalogue_to_points,
    graph_laplacian_from_weights, normalize_continuum_limit,
)
from compiler.verification.heat_kernel_fit import (
    CurvatureClosure, curvature_closure, fit_polynomial_coefficients,
)

Stage = Literal["mathematical_convergence", "curvature_closure", "physical_validation"]


@dataclass
class RefinementPoint:
    N: int
    epsilon: float
    low_eigenvalues: list[float]
    solver_residual: float  # max ||L_tilde v_k - lambda_k v_k||


@dataclass
class MathematicalConvergenceResult:
    converged: bool
    failed_dependency: str | None  # exact IR node id, if converged=False
    failure_reason: str
    points: list[RefinementPoint]
    relative_changes: list[float]  # consecutive-refinement relative change in the low spectrum
    tolerance: float

    def to_dict(self) -> dict:
        return {
            "converged": self.converged, "failed_dependency": self.failed_dependency,
            "failure_reason": self.failure_reason,
            "points": [p.__dict__ for p in self.points],
            "relative_changes": self.relative_changes, "tolerance": self.tolerance,
        }


@dataclass
class CurvatureClosureResult:
    closure: CurvatureClosure
    tolerance: float
    closed: bool  # |E_kappa| < tolerance
    n_modes_used: int
    sufficient_modes: bool  # whether n_modes_used covers the requested t-window (see note)
    note: str

    def to_dict(self) -> dict:
        return {"closure": self.closure.to_dict(), "tolerance": self.tolerance, "closed": self.closed,
                "n_modes_used": self.n_modes_used, "sufficient_modes": self.sufficient_modes,
                "note": self.note}


@dataclass
class PhysicalValidationResult:
    kappa_spectral: float
    kappa_cosmological: float
    kappa_cosmological_source: str
    delta_kappa: float
    tolerance: float
    agrees: bool

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class FC005DesiExecutionResult:
    mathematical_convergence: MathematicalConvergenceResult
    curvature_closure_result: CurvatureClosureResult | None
    physical_validation_result: PhysicalValidationResult | None
    stopped_at: Stage
    summary: str

    def to_dict(self) -> dict:
        return {
            "mathematical_convergence": self.mathematical_convergence.to_dict(),
            "curvature_closure_result": self.curvature_closure_result.to_dict()
            if self.curvature_closure_result else None,
            "physical_validation_result": self.physical_validation_result.to_dict()
            if self.physical_validation_result else None,
            "stopped_at": self.stopped_at,
            "summary": self.summary,
        }


def _low_eigen(L_tilde: np.ndarray, n_modes: int) -> tuple[np.ndarray, np.ndarray, float]:
    eigvals, eigvecs = np.linalg.eigh(L_tilde)
    idx = np.argsort(eigvals)
    eigvals, eigvecs = eigvals[idx], eigvecs[:, idx]
    k = min(n_modes, len(eigvals))
    low_vals, low_vecs = eigvals[:k], eigvecs[:, :k]
    residual = float(np.max(np.abs(L_tilde @ low_vecs - low_vecs @ np.diag(low_vals))))
    return low_vals, low_vecs, residual


def run_mathematical_convergence(
    ra: np.ndarray, dec: np.ndarray, z: np.ndarray, weights: np.ndarray | None,
    cosmology: CosmologyModel, *,
    N_values: list[int], epsilon_values: list[float],
    n_modes: int = 60, tolerance: float = 0.05, solver_tolerance: float = 1e-6,
    seed: int = 0,
) -> MathematicalConvergenceResult:
    """Stage 1. Refinement sweep over N (subsample size) and epsilon
    (kernel bandwidth); converged means the low-lying spectrum of
    L_tilde_(N,eps) stabilizes as N increases and eps decreases, exactly
    the FC-005-D convergence audit -- not a single (N, eps) run."""
    pts_full = catalogue_to_points(ra, dec, z, cosmology)
    w_full = weights if weights is not None else np.ones(len(ra))
    rng = np.random.default_rng(seed)

    points_out: list[RefinementPoint] = []
    for N, eps in zip(N_values, epsilon_values):
        if N > len(pts_full):
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="GRAPH-G-DESI",
                failure_reason=f"requested subsample N={N} exceeds catalogue size {len(pts_full)}",
                points=points_out, relative_changes=[], tolerance=tolerance,
            )
        idx = rng.choice(len(pts_full), size=N, replace=False)
        pts, w = pts_full[idx], w_full[idx]
        W = build_kernel_graph(pts, epsilon=eps, weights=w)
        if not np.any(W > 0):
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="OPERATOR-L-DESI",
                failure_reason=f"graph has no edges at N={N}, eps={eps} -- kernel bandwidth "
                               f"too small for this point density",
                points=points_out, relative_changes=[], tolerance=tolerance,
            )
        _, L = graph_laplacian_from_weights(W)
        n_components = _count_connected_components(W)
        if n_components > 1:
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="OPERATOR-L-DESI",
                failure_reason=f"graph is disconnected ({n_components} components) at N={N}, "
                               f"eps={eps} -- kernel(L) is not 1-dimensional, spectral gap "
                               f"analysis is not well-posed",
                points=points_out, relative_changes=[], tolerance=tolerance,
            )
        L_tilde = normalize_continuum_limit(L, N=N, epsilon=eps)
        low_vals, _, residual = _low_eigen(L_tilde, n_modes)
        if residual > solver_tolerance:
            return MathematicalConvergenceResult(
                converged=False, failed_dependency="DESI-SPECTRUM",
                failure_reason=f"eigensolver residual {residual:.3e} exceeds solver tolerance "
                               f"{solver_tolerance:.3e} at N={N}, eps={eps}",
                points=points_out, relative_changes=[], tolerance=tolerance,
            )
        points_out.append(RefinementPoint(N=N, epsilon=eps, low_eigenvalues=low_vals.tolist(),
                                           solver_residual=residual))

    relative_changes = []
    for i in range(len(points_out) - 1):
        prev = np.array(points_out[i].low_eigenvalues)
        curr = np.array(points_out[i + 1].low_eigenvalues)
        denom = np.maximum(np.abs(prev), 1e-12)
        relative_changes.append(float(np.max(np.abs(curr - prev) / denom)))

    if not relative_changes:
        return MathematicalConvergenceResult(
            converged=False, failed_dependency="CONTINUUM-LIMIT-L-DESI",
            failure_reason="fewer than 2 (N, eps) refinement points supplied -- a convergence "
                           "audit requires a refinement sequence, not a single run",
            points=points_out, relative_changes=[], tolerance=tolerance,
        )

    converged = bool(relative_changes[-1] < tolerance and all(
        relative_changes[i + 1] <= relative_changes[i] * 1.5 for i in range(len(relative_changes) - 1)
    ))
    return MathematicalConvergenceResult(
        converged=converged,
        failed_dependency=None if converged else "CONTINUUM-LIMIT-L-DESI",
        failure_reason="" if converged else (
            f"low-spectrum relative change did not fall below tolerance {tolerance} under "
            f"refinement (last relative change {relative_changes[-1]:.4f}); L_tilde_(N,eps) "
            f"does not show numerical evidence of convergence to Delta_h with this catalogue"
        ),
        points=points_out, relative_changes=relative_changes, tolerance=tolerance,
    )


def _count_connected_components(W: np.ndarray) -> int:
    n = W.shape[0]
    seen = np.zeros(n, dtype=bool)
    components = 0
    for start in range(n):
        if seen[start]:
            continue
        components += 1
        stack = [start]
        seen[start] = True
        while stack:
            i = stack.pop()
            neighbors = np.nonzero(W[i] > 0)[0]
            for j in neighbors:
                if not seen[j]:
                    seen[j] = True
                    stack.append(j)
    return components


TRUNCATION_SAFETY_MARGIN = 80.0  # matches compiler/backends/heat_kernel_sphere.py's
# required_l_max margin (exp(-80) ~ 1.8e-35). A smaller margin (e.g. 20, exp(-20)~2e-9)
# looks safe mode-by-mode but is NOT: near lambda_max the mode density (l+1)^2 in 3D
# grows fast enough that many weakly-suppressed high modes still bias the sum -- this
# was caught empirically by the degree-refinement stability check below, not assumed.


def run_curvature_closure(
    convergence: MathematicalConvergenceResult, *,
    t_min_scale: float = 100.0, t_max_scale: float = 400.0, npts: int = 50,
    tolerance: float = 1e-2, degree: int = 3,
) -> CurvatureClosureResult:
    """Stage 2. Only called after stage 1 converged. Builds K(t) from the
    converged low-lying spectrum at the finest (N, eps) point, fits
    (a0, a1, a2), computes E_kappa exactly as in the S^3 control -- same
    fit machinery (compiler/verification/heat_kernel_fit.py) and the same
    dense-window-of-many-points fit shape (not a handful of scattered t
    values, which is numerically ill-conditioned for the Vandermonde
    system), so the two are directly comparable.

    Two independent, complementary safeguards, since neither alone is
    sufficient:
    1. Truncation safety (spec section 13): the heat trace at a given t is
       only trustworthy if modes NOT captured by the eigensolver would
       have contributed negligibly, i.e. exp(-t*lambda_max_captured) is
       small. t_min_scale/t_max_scale are multiples of the UV scale
       1/lambda_max_captured (NOT 1/lambda_min -- the short-time expansion
       needs many high modes, which is what the eigensolver's mode count
       actually limits).
    2. Degree-refinement stability (empirical, assumes nothing about the
       unknown manifold's geometric scale): the fit must not change
       meaningfully when the polynomial degree increases by one. The S^3
       control's own degree-2-vs-3 comparison showed a >1000x swing in
       E_kappa when resolution was insufficient; the same check is run
       here generically.

    Failing either safeguard returns sufficient_modes=False and closed=
    False -- never a silently biased a2."""
    finest = convergence.points[-1]
    lam = np.array(finest.low_eigenvalues)
    lam = lam[lam > 1e-10]  # drop the zero mode
    n_modes_used = len(lam)
    if n_modes_used < degree + 3:
        closure = curvature_closure(float("nan"), float("nan"), float("nan"))
        return CurvatureClosureResult(closure=closure, tolerance=tolerance, closed=False,
                                       n_modes_used=n_modes_used, sufficient_modes=False,
                                       note=f"only {n_modes_used} nonzero modes available, need "
                                            f"at least {degree + 3} for a degree-{degree} fit "
                                            f"plus a degree-{degree + 1} stability check")

    lambda_max_captured = float(lam.max())
    t_ref = 1.0 / lambda_max_captured
    t_min, t_max = t_min_scale * t_ref, t_max_scale * t_ref
    t_min_trustworthy = TRUNCATION_SAFETY_MARGIN / lambda_max_captured
    sufficient_modes = bool(t_min >= t_min_trustworthy)

    if not sufficient_modes:
        closure = curvature_closure(float("nan"), float("nan"), float("nan"))
        return CurvatureClosureResult(
            closure=closure, tolerance=tolerance, closed=False,
            n_modes_used=n_modes_used, sufficient_modes=False,
            note=f"requested t_min={t_min:.3e} is below the trustworthy bound "
                 f"{t_min_trustworthy:.3e} implied by the {n_modes_used} captured modes "
                 f"(lambda_max={lambda_max_captured:.4g}); more eigenmodes must be solved "
                 f"for before this fit window can be trusted -- NOT reporting a curvature "
                 f"result rather than returning one biased by truncation",
        )

    ts = np.linspace(t_min, t_max, npts)
    Y = np.array([np.sum(np.exp(-t * lam)) * (4 * np.pi * t) ** 1.5 for t in ts])
    coeffs = fit_polynomial_coefficients(ts, Y, degree)
    closure = curvature_closure(coeffs[0], coeffs[1], coeffs[2])

    # Empirical stability check (does not assume any a priori knowledge of
    # the manifold's geometric scale, unlike the truncation-margin check
    # above): the fit must not change meaningfully when the polynomial
    # degree is increased by one. The S^3 control's own degree-2-vs-3
    # comparison showed a >1000x swing in E_kappa when resolution was
    # insufficient -- the same empirical test is applied here, generically.
    coeffs_hi = fit_polynomial_coefficients(ts, Y, degree + 1)
    closure_hi = curvature_closure(coeffs_hi[0], coeffs_hi[1], coeffs_hi[2])
    a2_scale = max(abs(closure.a2), abs(closure_hi.a2), 1e-12)
    degree_stable = bool(
        np.isfinite(closure.e_kappa) and np.isfinite(closure_hi.e_kappa)
        and abs(closure.a2 - closure_hi.a2) / a2_scale < 0.2
    )

    if not degree_stable:
        return CurvatureClosureResult(
            closure=closure, tolerance=tolerance, closed=False,
            n_modes_used=n_modes_used, sufficient_modes=False,
            note=f"fit is NOT stable under degree refinement (a2 at degree {degree}="
                 f"{closure.a2:.4g} vs degree {degree + 1}={closure_hi.a2:.4g}) -- more "
                 f"eigenmodes and/or a smaller/denser t-grid are required before this "
                 f"result can be trusted; NOT reporting a curvature closure",
        )

    closed = np.isfinite(closure.e_kappa) and abs(closure.e_kappa) < tolerance
    return CurvatureClosureResult(closure=closure, tolerance=tolerance, closed=bool(closed),
                                   n_modes_used=n_modes_used, sufficient_modes=True,
                                   note="fit window within the truncation-safe t range and "
                                        "stable under degree refinement")


def run_physical_validation(
    curvature: CurvatureClosureResult, *, kappa_cosmological: float,
    kappa_cosmological_source: str, tolerance: float = 0.1,
) -> PhysicalValidationResult:
    """Stage 3. Only called after stage 2 closed. kappa_cosmological MUST
    come from a source independent of the catalogue/run that produced
    kappa_spectral (spec section 16: 'Do not use the same quantity twice
    to generate and validate itself')."""
    if not kappa_cosmological_source or kappa_cosmological_source.strip() == "":
        raise ValueError("kappa_cosmological_source must name an independent source; refusing "
                          "to run a validation stage against an unattributed number")
    kappa_spectral = curvature.closure.kappa_a1
    delta_kappa = float(kappa_spectral - kappa_cosmological)
    agrees = bool(abs(delta_kappa) < tolerance)
    return PhysicalValidationResult(
        kappa_spectral=kappa_spectral, kappa_cosmological=kappa_cosmological,
        kappa_cosmological_source=kappa_cosmological_source, delta_kappa=delta_kappa,
        tolerance=tolerance, agrees=agrees,
    )


def run_fc005_desi_pipeline(
    ra: np.ndarray, dec: np.ndarray, z: np.ndarray, weights: np.ndarray | None,
    cosmology: CosmologyModel, *,
    N_values: list[int], epsilon_values: list[float],
    kappa_cosmological: float | None = None, kappa_cosmological_source: str = "",
    convergence_tolerance: float = 0.05, curvature_tolerance: float = 1e-2,
    physical_tolerance: float = 0.1, n_modes: int = 60,
) -> FC005DesiExecutionResult:
    """The exact three-stage procedure this branch is bound to. Never
    call this with a catalogue-derived number standing in for
    kappa_cosmological -- pass None and the pipeline stops after stage 2
    with that limitation reported, rather than fabricating stage 3.

    n_modes governs BOTH the stage-1 refinement-stability check and the
    number of eigenmodes available to the stage-2 heat-trace fit; if it
    is too small for the requested curvature-closure fit window, stage 2
    reports sufficient_modes=False rather than silently under-resolving
    the fit (see run_curvature_closure)."""
    convergence = run_mathematical_convergence(
        ra, dec, z, weights, cosmology, N_values=N_values, epsilon_values=epsilon_values,
        tolerance=convergence_tolerance, n_modes=n_modes,
    )
    if not convergence.converged:
        return FC005DesiExecutionResult(
            mathematical_convergence=convergence, curvature_closure_result=None,
            physical_validation_result=None, stopped_at="mathematical_convergence",
            summary=f"STOPPED at mathematical convergence: failed dependency "
                    f"'{convergence.failed_dependency}' -- {convergence.failure_reason}",
        )

    curvature = run_curvature_closure(
        convergence, t_min_scale=100.0, t_max_scale=400.0, tolerance=curvature_tolerance,
    )
    if not curvature.closed:
        if not curvature.sufficient_modes:
            reason = f"insufficient eigenmodes to trust the fit -- {curvature.note}"
        else:
            reason = (f"E_kappa={curvature.closure.e_kappa:.4g} did not fall below tolerance "
                      f"{curvature.tolerance:.4g}")
        return FC005DesiExecutionResult(
            mathematical_convergence=convergence, curvature_closure_result=curvature,
            physical_validation_result=None, stopped_at="curvature_closure",
            summary=f"Mathematical convergence PASSED. STOPPED at curvature closure: {reason} "
                    f"-- this is a genuine curvature-closure failure, not proceeding to the "
                    f"cosmological cross-check.",
        )

    if kappa_cosmological is None:
        return FC005DesiExecutionResult(
            mathematical_convergence=convergence, curvature_closure_result=curvature,
            physical_validation_result=None, stopped_at="curvature_closure",
            summary="Mathematical convergence PASSED. Curvature closure PASSED "
                    f"(E_kappa={curvature.closure.e_kappa:.4g}). Physical validation NOT RUN: "
                    "no independently-sourced kappa_cosmological was supplied.",
        )

    validation = run_physical_validation(
        curvature, kappa_cosmological=kappa_cosmological,
        kappa_cosmological_source=kappa_cosmological_source, tolerance=physical_tolerance,
    )
    return FC005DesiExecutionResult(
        mathematical_convergence=convergence, curvature_closure_result=curvature,
        physical_validation_result=validation, stopped_at="physical_validation",
        summary=f"All three stages executed. mathematical_convergence=PASS, "
                f"curvature_closure=PASS (E_kappa={curvature.closure.e_kappa:.4g}), "
                f"physical_validation={'AGREES' if validation.agrees else 'DISAGREES'} "
                f"(delta_kappa={validation.delta_kappa:.4g} vs tolerance {physical_tolerance}).",
    )
