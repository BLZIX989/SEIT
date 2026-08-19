"""Verification engine (spec section 24).

Every calculation returns result, residual, precision, tolerance, test,
provenance. Symbolic verification uses sympy.simplify(LHS-RHS) == 0;
numeric verification uses a norm-based residual against an explicit
tolerance. Universal claims require sweeps (multiple sizes/topologies),
never a single successful example (see backends/graph_laplacian.py and
backends/diffusion_metric.py for the sweep callers).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class VerificationResult:
    test: str
    passed: bool
    residual: float
    tolerance: float
    precision: str  # "exact" | "numeric"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "test": self.test,
            "passed": self.passed,
            "residual": self.residual,
            "tolerance": self.tolerance,
            "precision": self.precision,
            "details": self.details,
        }


def symbolic_verify(lhs, rhs, *, test: str, assumptions: list[str] | None = None) -> VerificationResult:
    import sympy
    diff = sympy.simplify(lhs - rhs)
    passed = diff == 0
    return VerificationResult(
        test=test,
        passed=bool(passed),
        residual=0.0 if passed else float("nan"),
        tolerance=0.0,
        precision="exact",
        details={"assumptions": assumptions or [], "simplified_residual": str(diff)},
    )


def numeric_verify(
    lhs: np.ndarray | float,
    rhs: np.ndarray | float,
    *,
    test: str,
    tolerance: float = 1e-9,
    details: dict[str, Any] | None = None,
) -> VerificationResult:
    lhs_a = np.asarray(lhs, dtype=float)
    rhs_a = np.asarray(rhs, dtype=float)
    residual = float(np.linalg.norm(lhs_a - rhs_a))
    passed = residual <= tolerance
    return VerificationResult(
        test=test,
        passed=passed,
        residual=residual,
        tolerance=tolerance,
        precision="numeric",
        details=details or {},
    )


def sweep_verify(name: str, results: list[VerificationResult]) -> VerificationResult:
    """Aggregate a parameter/topology/size sweep into one universal-claim
    verification (spec section 24: sweeps required, not one example)."""
    passed = all(r.passed for r in results)
    worst = max((r.residual for r in results if r.residual == r.residual), default=0.0)
    return VerificationResult(
        test=name,
        passed=passed,
        residual=worst,
        tolerance=max((r.tolerance for r in results), default=0.0),
        precision="sweep",
        details={
            "n_cases": len(results),
            "n_passed": sum(1 for r in results if r.passed),
            "cases": [r.to_dict() for r in results],
        },
    )
