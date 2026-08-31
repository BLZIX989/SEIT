"""The unimodularity step: U(3) -> SU(3)_c from a trace-free gauge
connection (established NCG-Standard-Model construction; SRO Established
Core section 4). Genuine symbolic linear algebra via sympy: builds a
general u(3)-valued connection A_mu = a0*I_3 + sum_a a^a lambda^a (Gell-Mann
generators, each traceless), computes Tr(A_mu) SYMBOLICALLY, and shows the
trace-free condition algebraically forces a0=0, leaving exactly the
traceless su(3) part.
"""
from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


def gell_mann_matrices() -> list[sp.Matrix]:
    i = sp.I
    return [
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, -i, 0], [i, 0, 0], [0, 0, 0]]),
        sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
        sp.Matrix([[0, 0, -i], [0, 0, 0], [i, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, -i], [0, i, 0]]),
        (sp.Rational(1, 3) ** sp.Rational(1, 2)) * sp.Matrix(
            [[1, 0, 0], [0, 1, 0], [0, 0, -2]]),
    ]


@dataclass
class UnimodularityResult:
    trace_of_identity_part: sp.Expr
    trace_of_traceless_part_is_zero: bool
    a0_forced_to_zero: bool


def unimodularity_step(a0: sp.Symbol | None = None) -> UnimodularityResult:
    """Tr(A_mu) = 3*a0 for A_mu = a0*I_3 + sum_a a^a*lambda^a, since every
    Gell-Mann matrix is traceless -- so Tr(A_mu)=0 forces a0=0 whenever 3
    is invertible (always, over the reals/complexes)."""
    if a0 is None:
        a0 = sp.Symbol("a0", real=True)
    lambdas = gell_mann_matrices()
    coeffs = sp.symbols(f"a1:{len(lambdas) + 1}", real=True)

    A_mu = a0 * sp.eye(3)
    for c, lam in zip(coeffs, lambdas):
        A_mu += c * lam

    trace_lambdas_zero = all(sp.simplify(lam.trace()) == 0 for lam in lambdas)
    assert trace_lambdas_zero, "Gell-Mann generators must be traceless (sanity check on the fixture)"

    trace_A = sp.simplify(A_mu.trace())
    trace_of_identity_part = sp.simplify(trace_A - sum(c * sp.simplify(lam.trace())
                                                         for c, lam in zip(coeffs, lambdas)))
    # Solve Tr(A_mu) = 0 for a0 -- genuinely forced to zero, not assumed.
    solutions = sp.solve(sp.Eq(trace_A, 0), a0)
    a0_forced_to_zero = solutions == [0]

    return UnimodularityResult(
        trace_of_identity_part=trace_of_identity_part,
        trace_of_traceless_part_is_zero=trace_lambdas_zero,
        a0_forced_to_zero=a0_forced_to_zero,
    )
