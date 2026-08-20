#!/usr/bin/env python3
"""Part VI: MASTER_PHYSICS_VALIDATION_MATRIX.csv with the exact column
set specified in this campaign's Part VI, covering the 17 named
branches (Primitive, Variational, Euler-Lagrange, Symmetry,
Conservation, Geometry, GR, Statistical, Quantum, Thermodynamic,
Spectral, DESI, Continuum, Curvature, Quantum/Gravity,
Early-universe/Cosmology, Late-universe/Cosmology).

Every value is sourced from the live registries or from direct
inspection of the compiler source -- nothing here is asserted without
a registry/code citation. FC-005 is read as-is (frozen, unchanged) per
this campaign's execution override -- not rerun.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NA = "n/a -- no executable backend registered in this compiler"
NR = "not reachable / not executed"

FIELDS = ["branch", "result_id", "canonical_equation", "canonical_variables",
          "dependencies", "derivation_source", "independent_reexecution",
          "invariant_checks", "symbolic_validation", "numerical_validation",
          "external_validation", "limiting_case", "falsification_test",
          "provenance", "status", "unresolved_dependencies", "next_action"]


def load(name):
    return json.loads((ROOT / name).read_text())


ROWS = [
    dict(branch="Primitive", result_id="TEMPLATE-CHAIN-FOUNDATION",
         canonical_equation="F0=(Logic,in,Axioms); F1=EmptySet; M=math universe; "
         "P={M in Mathset | Sigma(M)=1}",
         canonical_variables="F0, F1, M, P, Sigma",
         dependencies="SELECTION-SIGMA (Transformation, OPEN)",
         derivation_source="compiler/ir/forward_chain.py TEMPLATE_CHAIN -- registered as a "
         "dependency template, explicitly documented 'not a proof'",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="OPEN",
         status="OPEN",
         unresolved_dependencies="SELECTION-SIGMA: 'no non-arbitrary, unique, "
         "representation-invariant derivation of Sigma is registered in this build' "
         "(compiler/ir/forward_chain.py, verbatim)",
         next_action="requires an admissible, non-arbitrary Sigma -- out of scope to "
         "construct (would be inventing new physics/ontology, prohibited)"),

    dict(branch="Variational", result_id="VARIATIONAL-NODE",
         canonical_equation="S[phi]=int L d^4x; delta S/delta phi=0",
         canonical_variables="phi, S, L", dependencies="SPECTRUM-NODE (OPEN)",
         derivation_source="compiler/ir/forward_chain.py, bare OPEN template node",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="OPEN", status="OPEN",
         unresolved_dependencies="no action functional is registered anywhere in this "
         "compiler to derive from",
         next_action="none pursued -- would require inventing an action functional, out of "
         "scope"),

    dict(branch="Euler-Lagrange", result_id="EULER-LAGRANGE",
         canonical_equation="d/dt(dL/d(dphi/dt)) - dL/dphi = 0",
         canonical_variables="L, phi, dphi/dt", dependencies="VARIATIONAL-NODE (OPEN)",
         derivation_source="not separately registered -- subsumed under VARIATIONAL-NODE, "
         "which has no executed content",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance=NA, status="OPEN",
         unresolved_dependencies="blocked on VARIATIONAL-NODE (S[phi] itself unexecuted)",
         next_action="none pursued -- downstream of an unexecuted node"),

    dict(branch="Symmetry", result_id="NOETHER-SYMMETRY",
         canonical_equation="continuous symmetry -> conserved current J^mu",
         canonical_variables="phi, J^mu, symmetry generator",
         dependencies="VARIATIONAL-NODE (OPEN)",
         derivation_source="NOT REGISTERED -- no IR node of any kind exists for this",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="NOT REGISTERED", status="NOT REGISTERED",
         unresolved_dependencies="no node exists to check dependencies of",
         next_action="none -- nothing to validate"),

    dict(branch="Conservation", result_id="CONSERVATION-LAW",
         canonical_equation="d_mu J^mu = 0", canonical_variables="J^mu",
         dependencies="NOETHER-SYMMETRY (not registered)",
         derivation_source="NOT REGISTERED -- no IR node of any kind exists for this",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="NOT REGISTERED", status="NOT REGISTERED",
         unresolved_dependencies="no node exists to check dependencies of",
         next_action="none -- nothing to validate"),

    dict(branch="Geometry", result_id="GEOMETRY-NODE",
         canonical_equation="g_munu -> nabla -> R^rho_sigmamunu -> R_munu -> R",
         canonical_variables="g_munu, nabla, R^rho_sigmamunu, R_munu, R",
         dependencies="SPECTRUM-NODE (OPEN)",
         derivation_source="compiler/ir/forward_chain.py, bare OPEN template node",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="OPEN", status="OPEN",
         unresolved_dependencies="no metric g_munu, connection, or curvature tensor "
         "computation is registered anywhere in this compiler",
         next_action="none pursued -- out of scope to construct a new GR backend"),

    dict(branch="GR", result_id="EINSTEIN-FIELD-EQUATION",
         canonical_equation="G_munu + Lambda g_munu = (8 pi G/c^4) T_munu; "
         "nabla^mu G_munu=0 => nabla^mu T_munu=0",
         canonical_variables="G_munu, Lambda, g_munu, T_munu",
         dependencies="GEOMETRY-NODE (OPEN), MATTER-NODE (OPEN)",
         derivation_source="not separately registered as an IR node at all -- there is no "
         "GEOMETRY-NODE successor computing G_munu; the only field-equation-adjacent node is "
         "SEMICLASSICAL-EINSTEIN-EQUATION (see 'Matter/Geometry Interface', PROPOSED)",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance=NA, status="OPEN",
         unresolved_dependencies="no Riemann/Ricci/Einstein-tensor computation, no Bianchi "
         "identity check, no weak-field/Newtonian limit is registered or executed anywhere",
         next_action="none pursued -- out of scope to construct a new GR backend"),

    dict(branch="Statistical", result_id="FISHER-RAO-PSD",
         canonical_equation="F_ij = E[(d/d theta_i log p)(d/d theta_j log p)]",
         canonical_variables="F (Fisher-Rao metric), theta=(mu,sigma) for a Gaussian family",
         dependencies="none (self-contained)",
         derivation_source="compiler/verification/fisher_information.py, executed via "
         "CALC-FC005-FISHER-PSD",
         independent_reexecution="re-executed twice this campaign, bit-for-bit reproducible "
         "(eigenvalues [1.0, 2.0] at sigma=1, both runs)",
         invariant_checks="positive-semidefiniteness verified directly",
         symbolic_validation="VERIFIED (symbolic F derived via sympy)",
         numerical_validation="VERIFIED", external_validation=NR,
         limiting_case="not applicable (a single-family symbolic result, no limiting regime "
         "declared)",
         falsification_test="FALS-FC005-FISHER-LORENTZIAN: PSD F cannot equal a Lorentzian "
         "g_munu under any basis change -- correctly falsified, see 'Falsified Branches'",
         provenance="VERIFIED", status="VERIFIED",
         unresolved_dependencies="none for this one step; the broader Statistical Recovery "
         "Core chain (mu,P,X,E[X],Var(X),H(P),Z,P(x,t),L and its spectral decomposition) is "
         "NOT registered as executed IR nodes anywhere -- only this last step exists",
         next_action="none for this step; the rest of the stated SRC chain would require "
         "independently executing 10+ intermediate steps, out of scope for a validation-only "
         "campaign"),

    dict(branch="Quantum", result_id="EIGENVALUE-UNIQUENESS-COUNTEREXAMPLE",
         canonical_equation="H|n>=E_n|n>; Spec(H_1)=Spec(H_2) but H_1 != H_2",
         canonical_variables="H, E_n, |n>, Spec(H)",
         dependencies="none (self-contained)",
         derivation_source="compiler/falsification/eigen_uniqueness.py, executed via "
         "CALC-FC005-EIGEN-UNIQUENESS",
         independent_reexecution="re-executed twice this campaign, bit-for-bit reproducible "
         "(25/25 trials, max residual 8.88e-16, both runs)",
         invariant_checks="matrices_differ=True confirmed while Spec matches to solver "
         "precision",
         symbolic_validation="VERIFIED", numerical_validation="VERIFIED",
         external_validation=NR, limiting_case="n=2 case only; not extended to higher "
         "dimension (would be new scope)",
         falsification_test="FALS-FC005-EIGENVALUE-UNIQUENESS: correctly falsifies "
         "'spectrum uniquely determines operator' -- see 'Falsified Branches'",
         provenance="VERIFIED", status="VERIFIED",
         unresolved_dependencies="none for this one step; the broader Quantum Recovery Core "
         "chain (Hilbert space, observables, quantization map) is NOT registered as executed "
         "IR nodes anywhere -- QUANTUM-NODE remains a bare OPEN template",
         next_action="none for this step; the rest of the stated QRC chain is out of scope "
         "to construct"),

    dict(branch="Thermodynamic", result_id="THERMODYNAMICS-NODE",
         canonical_equation="e=E/rho-(1/2)u^alpha u_alpha; Clausius-Duhem; S^mu; "
         "q^mu=-kappa*grad^mu T, kappa>=0",
         canonical_variables="e, E, rho, u^alpha, S^mu, q^mu, kappa, T",
         dependencies="MATTER-NODE (OPEN)",
         derivation_source="compiler/ir/forward_chain.py, bare OPEN template node",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="OPEN", status="OPEN",
         unresolved_dependencies="no thermodynamic-recovery computation of any kind is "
         "registered anywhere in this compiler",
         next_action="none pursued -- out of scope to construct a new thermodynamic backend"),

    dict(branch="Spectral", result_id="GRAPH-LAPLACIAN-HEAT-KERNEL-PIPELINE",
         canonical_equation="L phi_n=lambda_n phi_n; K(t)=sum_n exp(-t lambda_n); heat-flow "
         "R(t); S^3 analytic control (a0,a1,a2)",
         canonical_variables="L, lambda_n, phi_n, K(t), R(t), S3 coefficients",
         dependencies="none (self-contained pipeline + independent S^3 control)",
         derivation_source="compiler/backends/{graph_laplacian,spectral,heat_flow,"
         "pipeline_graph_heatflow,heat_kernel_sphere}.py; 14 CALC-T1-* + CALC-FC005-S3-CONTROL",
         independent_reexecution="re-executed twice this campaign, bit-for-bit reproducible "
         "for all 15 calculations",
         invariant_checks="row-sums of L ~0 to machine precision, symmetry confirmed, "
         "eigenvalues sorted ascending, eigenvector norms=1 (see compiler/tests/"
         "test_graph_laplacian.py-style assertions embedded in the pipeline)",
         symbolic_validation="n/a (numerical mathematics, not symbolic)",
         numerical_validation="VERIFIED (14 graph topologies); VERIFIED (S^3, "
         "max|E_kappa|=1.02e-5 vs pre-registered 1e-4 tolerance, 4 fit windows x degree 2-6)",
         external_validation="n/a (pure mathematics, not an observational claim)",
         limiting_case="S^3 numerical fit -> exact analytic (a0,a1,a2) as fit degree "
         "increases (degree 2 -> |E_kappa|~1e-3, degree 4/5 -> |E_kappa|~1e-8/1e-9)",
         falsification_test="FALS-SPECTRUM-RELABELING-INVARIANCE: Spec(L) confirmed invariant "
         "under vertex relabeling, 5 representations, passed=True",
         provenance="VERIFIED", status="VERIFIED",
         unresolved_dependencies="none", next_action="none -- this branch is fully closed "
         "for the scope it covers"),

    dict(branch="DESI", result_id="DESI-GATE1-FROZEN",
         canonical_equation="G_DESI -> L_DESI -> L_tilde_(N,eps) -> Spec(-L_tilde)",
         canonical_variables="N, epsilon, L_N, L_tilde, lambda_n",
         dependencies="DESI-CATALOGUE (CALCULATED), GRAPH-G-DESI (CALCULATED), "
         "OPERATOR-L-DESI (CALCULATED)",
         derivation_source="compiler/backends/desi_{graph,fc005_pipeline,sparse,"
         "diagnostics}.py; FC005_CHECKPOINT.md",
         independent_reexecution="NOT rerun this campaign -- per explicit execution "
         "override, the completed sparse N-scaling investigation is frozen and used as-is",
         invariant_checks="W_nonneg=True, W_symmetric=True, L_symmetric=True, L.1~0 to "
         "float precision, v^TLv>=0 over 200 test vectors (FC005_CONTINUUM_DIAGNOSTIC_REPORT.md "
         "section 3.5)",
         symbolic_validation="n/a", numerical_validation="FAIL (see 'Continuum' row below)",
         external_validation="real DESI DR1 LRG SGC data, checksum-verified, no synthetic "
         "substitution",
         limiting_case="N-scaling to N=64000 (sparse solver) tested; modes 1-4 of 15 show "
         "genuine joint eigenvalue+eigenvector convergence, modes 5-15 do not",
         falsification_test="not falsified -- FAIL/RETRIABLE is deliberately distinct from "
         "FALSIFIED, per FC005_CHECKPOINT.md's explicit reasoning",
         provenance="VERIFIED (full provenance chain, leakage control confirmed)",
         status="FAIL / RETRIABLE",
         unresolved_dependencies="CONTINUUM-LIMIT-L-DESI itself is the unresolved dependency "
         "for Gate 2/3",
         next_action="see FC005_N_SCALING_REPORT.md section 16 -- explicitly not pursued "
         "further this campaign per the execution override"),

    dict(branch="Continuum", result_id="CONTINUUM-LIMIT-L-DESI",
         canonical_equation="L_tilde_(N,eps) -> Delta_h as N->infinity, eps->0, "
         "N*eps^(d+2)->infinity",
         canonical_variables="N, epsilon, C_K, d",
         dependencies="OPERATOR-L-DESI (CALCULATED)",
         derivation_source="reports/fc005/FC005_N_SCALING_REPORT.md",
         independent_reexecution="frozen, not rerun this campaign",
         invariant_checks="asymptotic condition N*eps_N^(d+2) -> infinity verified to hold "
         "at every tested N for the corrected eps_N ~ N^(-1/(d+4)) rate",
         symbolic_validation="n/a",
         numerical_validation="modes 1-4 of 15: joint eigenvalue+eigenvector convergence "
         "confirmed (cosine 0.99+). Modes 5-15: eigenvalue-crossing false positive identified "
         "and rejected (cosine 0.07-0.15) -- NOT converged for the full retained spectrum",
         external_validation="real DESI data",
         limiting_case="uniform IID control converges through mode ~11 at the same N -- "
         "confirms the numerical method itself works; DESI trails it, not a method failure",
         falsification_test="not falsified -- the limiting operator, where it does converge "
         "(modes 1-4), has not been shown to differ from Delta_h; where it doesn't converge "
         "(modes 5+), no limiting operator can yet be identified at all (neither Delta_h nor "
         "any density-weighted alternative)",
         provenance="VERIFIED", status="FAIL / RETRIABLE",
         unresolved_dependencies="whether modes 5+ converge at larger N, or reflect a "
         "genuine, different limiting behavior, is unresolved",
         next_action="extend N further for DESI specifically (real catalogue supports up to "
         "160,150); not pursued this campaign per the execution override"),

    dict(branch="Curvature", result_id="CURVATURE-CLOSURE-DESI",
         canonical_equation="Spec(L_DESI) -> K(t) -> (a0,a1,a2) -> kappa -> E_kappa",
         canonical_variables="K(t), a0, a1, a2, kappa, E_kappa",
         dependencies="MATHEMATICAL-CONVERGENCE-DESI (FAIL), DESI-HEAT-TRACE (OPEN), "
         "DESI-HEAT-COEFFICIENTS (OPEN), E-KAPPA-DESI (OPEN)",
         derivation_source="compiler/backends/desi_fc005_pipeline.py::run_curvature_closure "
         "(code exists, never invoked on real data)",
         independent_reexecution="NOT executed -- Gate 2 was never entered, per instruction "
         "('do not enter Gate 2')",
         invariant_checks=NR, symbolic_validation=NR, numerical_validation=NR,
         external_validation=NR, limiting_case=NR, falsification_test=NR,
         provenance="OPEN (never entered)", status="OPEN",
         unresolved_dependencies="blocked entirely on MATHEMATICAL-CONVERGENCE-DESI = FAIL",
         next_action="blocked until Gate 1 closes -- explicitly not pursued, per instruction "
         "and per this campaign's own governing rule against propagating downstream from a "
         "FAIL node"),

    dict(branch="Quantum/Gravity", result_id="INTERFACE-I",
         canonical_equation="no admissible bridge equation registered",
         canonical_variables="n/a", dependencies="QUANTUM-NODE (OPEN), GEOMETRY-NODE (OPEN), "
         "T2-NCG-BRIDGE (OPEN)",
         derivation_source="compiler/historical/register.py: T2-REPRODUCTION explicitly "
         "'Not attempted; OPEN per spec section 5 (stop the branch, do not force closure)'",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test="EIGENVALUE-UNIQUENESS-COUNTEREXAMPLE is a NEGATIVE/guardrail "
         "result tangential to this interface (rejects a specific naive spectral-geometric "
         "identification), not a positive bridge",
         provenance="OPEN", status="OPEN",
         unresolved_dependencies="the full QRC chain (Quantum branch) and the full GR chain "
         "(GR branch) would both need to exist first",
         next_action="none pursued -- out of scope to construct new physics"),

    dict(branch="Early-universe/Cosmology", result_id="COSMOLOGY-EARLY",
         canonical_equation="Friedmann equations, inflationary/thermal initial conditions",
         canonical_variables="a(t), H(t), rho, p, T (early)",
         dependencies="COSMOLOGY-NODE (OPEN), THERMODYNAMICS-NODE (OPEN)",
         derivation_source="compiler/ir/forward_chain.py, bare OPEN template node",
         independent_reexecution=NR, invariant_checks=NR, symbolic_validation=NR,
         numerical_validation=NR, external_validation=NR, limiting_case=NR,
         falsification_test=NR, provenance="OPEN", status="OPEN",
         unresolved_dependencies="no early-universe evolution equation of any kind is "
         "registered or executed anywhere in this compiler",
         next_action="none pursued -- out of scope to construct new physics"),

    dict(branch="Late-universe/Cosmology", result_id="COSMOLOGY-LATE",
         canonical_equation="a(t), H(t), Lambda -- late-time evolution and observables",
         canonical_variables="a(t), H(t), Lambda, Omega_m, Omega_Lambda",
         dependencies="COSMOLOGY-NODE (OPEN)",
         derivation_source="the only late-universe content in this repository is "
         "FC005_cosmology.yaml (DESI's own published fiducial H0=67.36, Om=0.315192, "
         "OL=0.684808, w0=-1.0, numerically = Planck 2018 base-LambdaCDM), consumed purely as "
         "INPUT to the frozen DESI pipeline's comoving-distance calculation",
         independent_reexecution="the parameter file itself is used, unmodified, every time "
         "the DESI pipeline runs -- but this is consumption of an external published value, "
         "not an executed derivation of a late-universe evolution equation",
         invariant_checks=NR, symbolic_validation=NR,
         numerical_validation="used correctly and consistently as a coordinate-transform "
         "input (comoving_distance in compiler/backends/desi_graph.py) -- not itself a "
         "validated physics result",
         external_validation="the parameter VALUES are DESI's own published fiducial "
         "cosmology (arXiv:2404.03005) -- externally sourced, not independently derived here",
         limiting_case=NR, falsification_test=NR, provenance="CALCULATED (as pipeline input)",
         status="OPEN (as an evolution-equation branch); the parameter values themselves are "
         "externally validated inputs, not a project result",
         unresolved_dependencies="no late-universe evolution equation (Friedmann-equation "
         "derivation, dark-energy equation of state derivation, etc.) is registered or "
         "executed anywhere in this compiler",
         next_action="none pursued -- out of scope to construct new physics; the existing "
         "usage (as DESI pipeline input) is correctly scoped and does not overclaim"),
]


def main():
    csv_path = ROOT / "reports/physics_validation/MASTER_PHYSICS_VALIDATION_MATRIX.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ROWS)
    print(f"wrote {csv_path} ({len(ROWS)} rows)")


if __name__ == "__main__":
    main()
