"""Concrete theorem instances (Phase 4 of the implementation plan). Exactly
three are `implemented=True`, wired to the ALREADY-EXISTING backend functions
(never duplicated numerics): compiler.backends.graph_laplacian, .spectral,
.heat_flow. The remainder of the task's own theorem-library example list
(section 6) is registered honestly as `implemented=False` -- a real
statement, hypotheses, and citation, but the engine refuses to execute them
(see compiler/derivation/theorems.py::TheoremNotImplemented).
"""
from __future__ import annotations

import numpy as np

from compiler.backends.graph_laplacian import laplacian, laplacian_exact
from compiler.backends.heat_flow import heat_operator
from compiler.backends.spectral import spectrum
from compiler.derivation.obligations import ObligationResult, ProofObligation
from compiler.derivation.symbolic import symbolic_symmetric
from compiler.derivation.theorems import Theorem, TheoremRegistry
from compiler.derivation.types import (
    EpistemicKind, MathObject, MathType, TypeCompositionError, require,
)

EXACT_ARITHMETIC_MAX_N = 8  # matches compiler/backends/pipeline_graph_heatflow.py's own bound


# ---------------------------------------------------------------------------
# THM-SYMMETRIC-QUADRATIC-FORM-PSD  (TEST 1: G -> L, L=L^T, L>=0)
# ---------------------------------------------------------------------------

def _laplacian_applicable(bound: dict) -> bool:
    return bound.get("graph") is not None and bound["graph"].math_type == MathType.GRAPH


def _laplacian_transform(bound: dict):
    graph_obj = bound["graph"]
    g = graph_obj.carrier
    A = g.adjacency()
    L = laplacian(A)

    sym_numeric_check = lambda: bool(np.allclose(L, L.T))  # noqa: E731
    obligations = [ProofObligation(
        "symmetric-numeric", "||L - L^T|| ~ 0, verified numerically", check=sym_numeric_check,
    ).discharge()]

    if g.n <= EXACT_ARITHMETIC_MAX_N:
        L_exact = laplacian_exact(g.adjacency_exact())
        sym_symbolic_result = symbolic_symmetric(L_exact)
        obligations.append(ProofObligation(
            "symmetric-symbolic", "simplify(L - L^T) == 0, exact sympy cross-check (n<=8)",
            check=lambda: sym_symbolic_result,
        ).discharge())

    rng = np.random.default_rng(0)
    quad_min = min(float(x @ L @ x) for x in (rng.standard_normal(g.n) for _ in range(50)))
    eig_min = float(np.linalg.eigvalsh(L).min())
    psd_ok = eig_min >= -1e-9 and quad_min >= -1e-9
    obligations.append(ProofObligation(
        "positive-semidefinite",
        "x^T L x >= 0 for 50 random x (x^T(D-A)x = sum_ij w_ij(x_i-x_j)^2 >= 0), "
        "and min eigenvalue >= 0",
        check=lambda: psd_ok,
    ).discharge())

    output = MathObject(
        id=f"{graph_obj.id}::L", math_type=MathType.MATRIX,
        epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=L,
    )
    if all(o.result == ObligationResult.SATISFIED for o in obligations):
        output.verified_properties["symmetric"] = True
        output.verified_properties["positive_semidefinite"] = True
        output.math_type = MathType.POSITIVE_SEMIDEFINITE_OPERATOR
    return output, obligations


THM_LAPLACIAN_PSD = Theorem(
    theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD",
    statement="For a graph G=(V,E,W) with symmetric nonnegative weights, L=D-A is symmetric "
              "and positive semidefinite: x^T L x = sum_{i,j} w_ij (x_i-x_j)^2 >= 0 for all x.",
    hypotheses=["W is symmetric", "W is nonnegative", "D_ii = sum_j W_ij"],
    conclusion="L = D - A satisfies L = L^T and x^T L x >= 0 for all x",
    conclusion_type=MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
    domain="linear algebra / spectral graph theory",
    provenance="standard linear algebra; elementary quadratic-form argument",
    implemented=True,
    applicability_check=_laplacian_applicable,
    transformation=_laplacian_transform,
)


# ---------------------------------------------------------------------------
# THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC  (TEST 2: L -> Spec(L))
# ---------------------------------------------------------------------------

def _spectrum_applicable(bound: dict) -> bool:
    try:
        require(bound["operator"], MathType.SELF_ADJOINT_OPERATOR)
        return True
    except TypeCompositionError:
        return False


def _spectrum_transform(bound: dict):
    op_obj = require(bound["operator"], MathType.SELF_ADJOINT_OPERATOR)
    L = op_obj.carrier
    spec = spectrum(L)
    residual = spec.eigen_equation_residual(L)

    ob = ProofObligation(
        "eigen-equation-residual",
        "max_n ||L phi_n - lambda_n phi_n|| below tolerance (real symmetric spectral theorem)",
        check=lambda: residual < 1e-8,
    ).discharge()

    output = MathObject(
        id=f"{op_obj.id}::Spec", math_type=MathType.SPECTRUM,
        epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=spec,
    )
    if ob.result == ObligationResult.SATISFIED:
        output.verified_properties["eigendecomposition_valid"] = True
    return output, [ob]


THM_SPECTRAL_DECOMPOSITION = Theorem(
    theorem_id="THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC",
    statement="A real symmetric matrix L has a complete orthonormal eigenbasis {phi_n} with "
              "real eigenvalues {lambda_n}: L phi_n = lambda_n phi_n.",
    hypotheses=["L is a real, symmetric (self-adjoint) operator"],
    conclusion="Spec(L) = {(lambda_n, phi_n)} exists, is real, and satisfies L phi_n = lambda_n phi_n",
    conclusion_type=MathType.SPECTRUM,
    domain="linear algebra",
    provenance="standard spectral theorem for real symmetric matrices",
    implemented=True,
    applicability_check=_spectrum_applicable,
    transformation=_spectrum_transform,
)


# ---------------------------------------------------------------------------
# THM-MATRIX-EXPONENTIAL-SEMIGROUP  (TEST 3: L -> e^{-tL})
# ---------------------------------------------------------------------------

def _heat_kernel_applicable(bound: dict) -> bool:
    if bound.get("spectrum") is None or bound["spectrum"].math_type != MathType.SPECTRUM:
        return False
    try:
        require(bound["operator"], MathType.SELF_ADJOINT_OPERATOR)
        return True
    except TypeCompositionError:
        return False


def _heat_kernel_transform(bound: dict):
    op_obj = require(bound["operator"], MathType.SELF_ADJOINT_OPERATOR)
    L = op_obj.carrier
    t = float(bound["t"])
    H_t = heat_operator(L, t)
    n = L.shape[0]

    identity_ok = bool(np.allclose(heat_operator(L, 0.0), np.eye(n), atol=1e-9))
    rng = np.random.default_rng(1)
    s1, s2 = float(rng.uniform(0.01, 2.0)), float(rng.uniform(0.01, 2.0))
    semigroup_ok = bool(np.allclose(
        heat_operator(L, s1 + s2), heat_operator(L, s1) @ heat_operator(L, s2), atol=1e-8,
    ))

    obligations = [
        ProofObligation("heat-kernel-identity-at-zero", "H(0) = I",
                          check=lambda: identity_ok).discharge(),
        ProofObligation("heat-kernel-semigroup", "H(s+t) = H(s) H(t) for sampled s,t > 0",
                          check=lambda: semigroup_ok).discharge(),
    ]
    output = MathObject(
        id=f"{op_obj.id}::H(t={t})", math_type=MathType.HEAT_KERNEL,
        epistemic_kind=EpistemicKind.DERIVED_RESULT, carrier=H_t,
    )
    if all(o.result == ObligationResult.SATISFIED for o in obligations):
        output.verified_properties["semigroup"] = True
    return output, obligations


THM_HEAT_SEMIGROUP = Theorem(
    theorem_id="THM-MATRIX-EXPONENTIAL-SEMIGROUP",
    statement="H(t) = e^{-tL} = sum_n e^{-t lambda_n} phi_n phi_n^T is a well-defined, "
              "self-adjoint semigroup: H(0)=I and H(s)H(t)=H(s+t).",
    hypotheses=["L is self-adjoint with real spectrum Spec(L)"],
    conclusion="H(t)=e^{-tL} satisfies H(0)=I and the semigroup property",
    conclusion_type=MathType.HEAT_KERNEL,
    domain="functional calculus / spectral graph theory",
    provenance="standard matrix functional calculus applied to the spectral decomposition",
    implemented=True,
    applicability_check=_heat_kernel_applicable,
    transformation=_heat_kernel_transform,
)


# ---------------------------------------------------------------------------
# Registered-but-unimplemented library entries (task section 6's own list).
# Real statements and citations; the engine refuses to execute these
# (TheoremNotImplemented) until a future phase implements them.
# ---------------------------------------------------------------------------

def _stub(theorem_id, statement, hypotheses, conclusion, conclusion_type, domain, provenance):
    return Theorem(
        theorem_id=theorem_id, statement=statement, hypotheses=hypotheses,
        conclusion=conclusion, conclusion_type=conclusion_type, domain=domain,
        provenance=provenance, implemented=False,
    )


STUB_THEOREMS = [
    _stub("THM-RANK-NULLITY",
          "dim(ker T) + dim(im T) = dim(V) for a linear map T: V -> W.",
          ["T is linear", "V is finite-dimensional"], "rank(T)+nullity(T)=dim(V)",
          MathType.SCALAR, "linear algebra", "standard linear algebra"),
    _stub("THM-SVD",
          "Every matrix A admits A = U Sigma V^* with U,V unitary and Sigma nonnegative diagonal.",
          ["A is a linear map between finite-dimensional inner product spaces"],
          "A = U Sigma V^*", MathType.MATRIX, "linear algebra", "standard linear algebra"),
    _stub("THM-HODGE-DECOMPOSITION",
          "Omega^k(M) = im(d) (+) im(delta) (+) H^k, an orthogonal direct sum of exact, "
          "coexact, and harmonic k-forms.",
          ["M is a compact Riemannian manifold (or finite chain complex analogue)"],
          "Omega^k = exact (+) coexact (+) harmonic",
          MathType.DIFFERENTIAL, "differential/discrete geometry", "Hodge 1941; discrete analogue standard"),
    _stub("THM-D-SQUARED-ZERO",
          "The exterior derivative (or discrete coboundary operator) satisfies d(d(omega))=0.",
          ["d is the exterior derivative / discrete coboundary map"],
          "d^2 = 0", MathType.DIFFERENTIAL, "differential/discrete geometry",
          "standard differential/discrete exterior calculus"),
    _stub("THM-EULER-LAGRANGE",
          "A curve extremizing a functional S[y]=int L(y,y',t) dt satisfies "
          "d/dt(dL/dy') - dL/dy = 0.",
          ["S is Frechet-differentiable", "boundary values of y are fixed"],
          "d/dt(dL/dy') - dL/dy = 0", MathType.EQUATION, "variational calculus",
          "standard calculus of variations"),
    _stub("THM-NOETHER",
          "Every continuous symmetry of the action corresponds to a conserved current/charge.",
          ["S is invariant under a continuous one-parameter group of transformations"],
          "d_mu J^mu = 0 for the associated Noether current",
          MathType.OBSERVABLE, "variational calculus / field theory", "Noether 1918"),
    _stub("THM-LEVI-CIVITA-UNIQUENESS",
          "There exists a unique torsion-free connection compatible with a given metric g.",
          ["g is a nondegenerate metric tensor"],
          "Gamma^c_ab = (1/2) g^cd(d_a g_db + d_b g_da - d_d g_ab), unique",
          MathType.CONNECTION, "differential geometry", "standard Riemannian geometry"),
    _stub("THM-BIANCHI-IDENTITIES",
          "The Riemann tensor satisfies R^a_b[cd;e]=0 (second Bianchi); its contraction gives "
          "nabla^mu G_mu_nu = 0.",
          ["nabla is the Levi-Civita connection of g"],
          "nabla^mu G_mu_nu = 0", MathType.CURVATURE_TENSOR, "differential geometry",
          "standard Riemannian geometry"),
    _stub("THM-LICHNEROWICZ-FORMULA",
          "For a Dirac-type operator D on a spin manifold, D^2 = nabla*nabla + (1/4)R "
          "(+ gauge curvature term E in the twisted case).",
          ["D is a Dirac-type operator compatible with a Clifford module structure"],
          "D^2 = -(nabla^2) + E", MathType.LINEAR_OPERATOR,
          "spin geometry / noncommutative geometry",
          "Lichnerowicz 1963; specific numeric control-manifold cases already independently "
          "checked in this repository (compiler/backends/lichnerowicz_seeley_dewitt.py, "
          "VERIFIED for flat-2D-gauge and round-S^2-gravity controls) -- NOT yet reformulated "
          "through this general theorem entry"),
    _stub("THM-SEELEY-DEWITT-HEAT-KERNEL-EXPANSION",
          "Tr(e^{-t D^2}) ~ (4 pi t)^{-d/2} sum_k a_k t^k as t->0+, with a_0,a_2,a_4 the "
          "Seeley-DeWitt coefficients built from E and curvature invariants.",
          ["D^2 is a Laplace-type operator on a closed Riemannian manifold"],
          "a_0=tr(I)Vol, a_2=tr(E+R/6)Vol, a_4=(1/360)tr[...]Vol",
          MathType.SCALAR, "spectral geometry",
          "Gilkey 1975; Vassilevich 2003; a0/a2/a4 already numerically VERIFIED on control "
          "manifolds in compiler/backends/lichnerowicz_seeley_dewitt.py -- not yet reformulated "
          "through this general theorem entry; a6 explicitly NOT independently rederived anywhere "
          "in this repository (see CL-SEELEY-DEWITT-TO-SPECTRAL-ACTION's own OPEN status)"),
    _stub("THM-CLIFFORD-RELATIONS",
          "Generators of a Clifford algebra satisfy {gamma^a, gamma^b} = -2 g^{ab} I.",
          ["gamma^a act on a module compatible with the metric g"],
          "gamma^a gamma^b + gamma^b gamma^a = -2 g^{ab} I",
          MathType.CLIFFORD_ALGEBRA, "Clifford algebra / spin geometry", "standard Clifford algebra"),
]


def build_default_theorem_registry() -> TheoremRegistry:
    reg = TheoremRegistry()
    for t in (THM_LAPLACIAN_PSD, THM_SPECTRAL_DECOMPOSITION, THM_HEAT_SEMIGROUP, *STUB_THEOREMS):
        reg.register(t)
    return reg
