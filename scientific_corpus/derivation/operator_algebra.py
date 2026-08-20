"""Operator-algebra audit (brief section X): explicit, exact (sympy)
construction and verification of the Clifford relation
{gamma^mu, gamma^nu} = 2 g^{mu nu} I for a concrete representation, and a
Jacobi-identity check for the su(2) structure constants -- both external,
established mathematics, verified by direct construction rather than
asserted.
"""
from __future__ import annotations

import sympy as sp


def clifford_algebra_check(signature: tuple[int, ...] = (1, -1, -1, -1)) -> dict:
    """Standard Dirac gamma matrices (Dirac basis, 4x4) for the mostly-minus
    signature (+,-,-,-). External, established mathematics -- verified by
    exact symbolic matrix multiplication, not cited without checking."""
    I2 = sp.eye(2)
    Z2 = sp.zeros(2, 2)
    sigma1 = sp.Matrix([[0, 1], [1, 0]])
    sigma2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sigma3 = sp.Matrix([[1, 0], [0, -1]])
    sigmas = [sigma1, sigma2, sigma3]

    gamma0 = sp.Matrix(sp.BlockMatrix([[I2, Z2], [Z2, -I2]]))
    gammas = [gamma0]
    for s in sigmas:
        block = sp.Matrix(sp.BlockMatrix([[Z2, s], [-s, Z2]]))
        gammas.append(block)

    g = sp.diag(*signature)  # metric g^{mu nu}, mostly-minus
    n = len(gammas)
    all_hold = True
    failures = []
    for mu in range(n):
        for nu in range(n):
            anticomm = gammas[mu] * gammas[nu] + gammas[nu] * gammas[mu]
            expected = 2 * g[mu, nu] * sp.eye(4)
            holds = sp.simplify(anticomm - expected) == sp.zeros(4, 4)
            all_hold = all_hold and holds
            if not holds:
                failures.append((mu, nu))
    return {
        "claim": "{gamma^mu, gamma^nu} = 2 g^{mu nu} I (Dirac basis, signature (+,-,-,-))",
        "external_established_mathematics": True,
        "holds_exactly_for_all_16_mu_nu_pairs": bool(all_hold),
        "failures": failures,
    }


def su2_jacobi_identity_check() -> dict:
    """su(2) structure constants f_{abc} = epsilon_{abc} (Pauli-matrix
    normalization [T_a,T_b]=i*eps_{abc}*T_c with T_a=sigma_a/2). Verifies
    the Jacobi identity holds EXACTLY for the actual Pauli-matrix
    commutators, not merely cited as a property of Lie algebras in
    general."""
    sigma1 = sp.Matrix([[0, 1], [1, 0]])
    sigma2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sigma3 = sp.Matrix([[1, 0], [0, -1]])
    T = [s / 2 for s in (sigma1, sigma2, sigma3)]

    def comm(A, B):
        return A * B - B * A

    all_hold = True
    max_residual = 0
    for a in range(3):
        for b in range(3):
            for c in range(3):
                lhs = comm(T[a], comm(T[b], T[c])) + comm(T[b], comm(T[c], T[a])) + comm(T[c], comm(T[a], T[b]))
                residual = sp.simplify(lhs)
                holds = residual == sp.zeros(2, 2)
                all_hold = all_hold and holds
    return {
        "claim": "Jacobi identity [T_a,[T_b,T_c]] + [T_b,[T_c,T_a]] + [T_c,[T_a,T_b]] = 0 "
                 "for T_a = sigma_a/2 (su(2) fundamental representation)",
        "external_established_mathematics": True,
        "holds_exactly_for_all_27_abc_triples": bool(all_hold),
    }


def gauge_covariant_derivative_dimensional_check() -> dict:
    """D_mu = partial_mu + i g A_mu (SEIT-20/Vol.4 Ch.24 language). Dimensional
    bookkeeping only, per brief section XII -- not a numerical computation."""
    return {
        "claim": "D_mu = partial_mu + i g A_mu",
        "[partial_mu]": "[length]^-1",
        "[D_mu]": "[length]^-1 (must match partial_mu for the sum to typecheck)",
        "[g A_mu]": "must equal [length]^-1, so [g] = [length]^-1 / [A_mu]",
        "consequence": (
            "The coupling constant g's dimension is FIXED once a convention for [A_mu] is "
            "chosen (e.g. [A_mu]=[length]^-1 in natural units with g dimensionless, the "
            "standard QFT convention) -- this is internally consistent standard physics, "
            "not a finding specific to this project, included here only because the brief "
            "explicitly asked for every major equation's dimensional audit to be performed "
            "rather than assumed.",
        ),
    }
