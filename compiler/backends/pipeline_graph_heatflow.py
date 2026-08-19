"""Executable Test 1 (spec section 31):

  Ø -> mathematical object -> graph G -> L = D - A -> Spec(L)
    -> e^{-tL} -> P_ker(L)

Run across multiple graph sizes and topologies, with exact-arithmetic
cross-check against the numeric solver on small graphs, and independent
numerical verification of the heat-kernel eigen-action and the kernel
convergence hypotheses (never assumed).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import sympy

from compiler.backends.graph_laplacian import build_graph, laplacian, laplacian_exact
from compiler.backends.heat_flow import verify_eigen_action, verify_kernel_convergence
from compiler.backends.spectral import spectrum, spectrum_exact
from compiler.verification.verify import VerificationResult, numeric_verify

EXACT_ARITHMETIC_MAX_N = 8  # sympy characteristic-polynomial eigenvalues stay tractable here


@dataclass
class Test1CaseResult:
    label: str
    topology: str
    n: int
    eigenvalues: list[float]
    zero_modes: list[int]
    spectral_gap: float
    eigen_equation_residual: float
    exact_cross_check: VerificationResult | None
    heat_eigen_action_residual: float
    kernel_convergence: dict
    verification: list[VerificationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        checks = [
            self.eigen_equation_residual < 1e-6,
            self.heat_eigen_action_residual < 1e-6,
            self.kernel_convergence["converges"],
        ]
        if self.exact_cross_check is not None:
            checks.append(self.exact_cross_check.passed)
        return all(checks)

    def to_dict(self) -> dict:
        return {
            "label": self.label, "topology": self.topology, "n": self.n,
            "eigenvalues": self.eigenvalues, "zero_modes": self.zero_modes,
            "spectral_gap": self.spectral_gap,
            "eigen_equation_residual": self.eigen_equation_residual,
            "exact_cross_check": self.exact_cross_check.to_dict() if self.exact_cross_check else None,
            "heat_eigen_action_residual": self.heat_eigen_action_residual,
            "kernel_convergence": self.kernel_convergence,
            "passed": self.passed,
        }


def run_case(topology: str, n: int, *, seed: int | None = None) -> Test1CaseResult:
    g = build_graph(topology, n, seed=seed)
    A = g.adjacency()
    L = laplacian(A)
    spec = spectrum(L)

    exact_cross_check = None
    if g.n <= EXACT_ARITHMETIC_MAX_N:
        A_exact = g.adjacency_exact()
        L_exact = laplacian_exact(A_exact)
        exact_eigs = spectrum_exact(L_exact)  # {value: multiplicity}
        exact_sorted = sorted(float(v) for v, m in exact_eigs.items() for _ in range(m))
        numeric_sorted = sorted(spec.eigenvalues.tolist())
        exact_cross_check = numeric_verify(
            numeric_sorted, exact_sorted,
            test=f"{g.label}: exact-vs-numeric eigenvalue cross-check",
            tolerance=1e-6,
            details={"exact": [str(v) for v in exact_sorted], "numeric": numeric_sorted},
        )

    eigen_eq_residual = spec.eigen_equation_residual(L)
    heat_result = verify_eigen_action(L, spec, t=0.37)
    # Probe convergence in units of the relaxation time 1/gap: an
    # absolute t range that works for one graph size is meaningless for
    # another, since e^{-t*gap} is what actually controls the residual.
    gap = spec.spectral_gap
    tau = 1.0 / gap if gap > 1e-12 else 1.0
    t_values = [k * tau for k in (0.5, 1, 2, 5, 10, 20, 40)]
    kernel_conv = verify_kernel_convergence(L, spec, t_values=t_values)

    return Test1CaseResult(
        label=g.label, topology=topology, n=g.n,
        eigenvalues=spec.eigenvalues.tolist(),
        zero_modes=spec.zero_modes,
        spectral_gap=spec.spectral_gap,
        eigen_equation_residual=eigen_eq_residual,
        exact_cross_check=exact_cross_check,
        heat_eigen_action_residual=heat_result.eigen_action_residual,
        kernel_convergence=kernel_conv,
    )


DEFAULT_SWEEP: list[tuple[str, int]] = [
    ("path", 4), ("path", 10), ("path", 25),
    ("cycle", 5), ("cycle", 12), ("cycle", 30),
    ("complete", 5), ("complete", 9),
    ("star", 6), ("star", 15),
    ("grid2d", 3), ("grid2d", 5),
    ("erdos_renyi", 8), ("erdos_renyi", 20),
]


def run_sweep(cases: list[tuple[str, int]] | None = None) -> list[Test1CaseResult]:
    cases = cases if cases is not None else DEFAULT_SWEEP
    results = []
    for topology, n in cases:
        seed = 42 if topology == "erdos_renyi" else None
        results.append(run_case(topology, n, seed=seed))
    return results
