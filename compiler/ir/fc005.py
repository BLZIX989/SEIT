"""FC-005 registration: reconstructs the physics DAG described in the
supplied workbooks inside the EXISTING MDCL (same Object/Transformation/
Equation IR, same Status enum, same Provenance model, same
MDCLRegistries) -- spec section 2 of the FC-005 build command forbids a
second competing registry/dependency system, so none is created here.

Governing rule applied throughout (spec section 4 of the FC-005 build
command): a workbook's own STATUS column is prose, not proof. It is
recorded in each node's provenance as `workbook_claimed_status` for
audit transparency, but every node's actual `Status` here is either (a)
independently computed by this build (S^3 control, Fisher-Rao PSD proof,
eigenvalue-uniqueness counterexample), or (b) PROPOSED/OPEN by default
for anything not independently executed -- exactly the same discipline
`compiler/core/status.py::map_legacy_status` already applies to prose
documents.
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

from compiler.backends.heat_kernel_sphere import EXACT_A0, EXACT_A1, EXACT_A2, run_s3_control
from compiler.core.ir import Equation, Object, Transformation
from compiler.core.status import Status
from compiler.falsification.eigen_uniqueness import run_counterexample
from compiler.falsification.protocols import FalsificationRecord
from compiler.historical.fc005_reconciliation import (
    DISCREPANCY_AUDIT_RESULT, FILENAME_DISCREPANCIES, WORKBOOK_CHAIN,
)
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance
from compiler.verification.fisher_information import run_fisher_lorentzian_obstruction_demo

PRIMARY_WORKBOOK = WORKBOOK_CHAIN[3]["repo_path"]  # canonical for FC-005 per the reconciliation audit
PRIMARY_WORKBOOK_SHEET = "Equations"


def _load_reference_equations(root: Path) -> list[dict]:
    """Reads the canonical workbook's Equations sheet directly (not the
    scratch CSV dump) so this is reproducible from a fresh checkout."""
    wb = openpyxl.load_workbook(root / PRIMARY_WORKBOOK, data_only=True)
    ws = wb[PRIMARY_WORKBOOK_SHEET]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h) for h in rows[0]]
    out = []
    for row in rows[1:]:
        if row is None or all(c is None for c in row):
            continue
        out.append(dict(zip(header, row)))
    return out


TYPE_DEFS_FC005 = [
    ("established_equation", "an equation asserted by an external/prior source; PROPOSED "
                              "until independently executed in this compiler", None),
    ("heat_trace_function", "K(t) = sum_n exp(-t lambda_n)", "mathematical_object"),
    ("heat_kernel_coefficients", "fitted (a0, a1, a2, ...) short-time heat-kernel expansion "
                                  "coefficients", "mathematical_object"),
    ("curvature_closure", "the E_kappa = a1/a0 - sgn(a1)*sqrt(2a2/a0) consistency test result", None),
    ("pending_data_construction", "a construction whose code path exists but that cannot be "
                                   "executed because required observational data is absent", None),
    ("semiclassical_framework_equation", "the established semiclassical Einstein equation "
                                          "G_munu + Lambda g_munu = (8piG/c^4) <T_munu>_ren", None),
    ("statistical_family", "a parametric probability family used to compute a Fisher "
                            "information matrix", "mathematical_object"),
    ("operator_uniqueness_counterexample", "an executed counterexample to spectrum-determines-"
                                            "operator", None),
    ("stage_gate", "one of the three independently-reported FC-005 execution stages "
                   "(mathematical convergence, curvature closure, physical validation); "
                   "its status is never inferred from another stage_gate's status", None),
    ("workbook_reconciliation_record", "provenance/precedence record for the four supplied "
                                        "FC-005 workbooks", None),
]


def register_fc005(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []
    falsifications: list[FalsificationRecord] = []

    # ---- 0. Workbook reconciliation record ----
    reconciliation = Object(
        id="FC005-WORKBOOK-RECONCILIATION", type="workbook_reconciliation_record",
        status=Status.CALCULATED, role="comparison",
        carrier=f"4 workbooks compared pairwise across all shared sheets "
                f"({len(DISCREPANCY_AUDIT_RESULT['sheets_compared'])} sheets); "
                f"{DISCREPANCY_AUDIT_RESULT['discrepancies_found']} discrepancies found. "
                "Nested-superset chain, not competing versions.",
        assumptions=[f"canonical (rank 4, PRIMARY): {WORKBOOK_CHAIN[3]['repo_path']}",
                     f"filename discrepancies vs the FC-005 build command's own naming: "
                     f"{len(FILENAME_DISCREPANCIES)} (see provenance.verification)"],
    )
    reconciliation.provenance = make_provenance(
        source="fc005_source_workbooks/ (4 files)", object_id=reconciliation.id,
        status=Status.CALCULATED,
        verification={"discrepancy_audit": DISCREPANCY_AUDIT_RESULT,
                      "filename_discrepancies": [d.__dict__ for d in FILENAME_DISCREPANCIES],
                      "chain": WORKBOOK_CHAIN},
    )
    registries.objects.add_object(reconciliation)

    # ---- 1. Bulk-import reference equations (Level 1/3 source, comparison-only) ----
    ref_rows = _load_reference_equations(repo_root)
    for row in ref_rows:
        eq_id = str(row["ID"])
        workbook_status = str(row.get("Status", ""))
        eq = Equation(
            id=eq_id, lhs=str(row.get("Name", "")), rhs=str(row.get("Equation", "")),
            domain="FC-005 reference equation set", status=Status.PROPOSED,
            role="comparison",
            derivation=f"variables: {row.get('Variables', '')}",
            assumptions=[
                f"workbook_claimed_status='{workbook_status}' -- NOT trusted at face value "
                "(spec section 2/4); PROPOSED until independently executed in this compiler.",
            ],
        )
        eq.provenance = make_provenance(
            source=f"{PRIMARY_WORKBOOK}::{PRIMARY_WORKBOOK_SHEET}::{eq_id}",
            equation_id=eq_id, status=Status.PROPOSED,
            verification={"workbook_claimed_status": workbook_status},
        )
        registries.equations.add_equation(eq)

    # ---- 2. S^3 heat-kernel control (executed regression test) ----
    s3 = run_s3_control()
    calculations.append({
        "id": "CALC-FC005-S3-CONTROL", "kind": "s3_heat_kernel_control_regression_test",
        "inputs": {"windows": [(r.t_min, r.t_max) for r in s3.fit_results],
                   "degree": s3.fit_results[0].degree, "tolerance": s3.tolerance},
        "results": {"fit_results": [r.to_dict() for r in s3.fit_results],
                    "degree_sweep": {str(d): [r.to_dict() for r in rs] for d, rs in s3.degree_sweep.items()}},
        "verification": {"max_abs_e_kappa": s3.max_abs_e_kappa, "a0_max_residual": s3.a0_max_residual,
                          "a1_max_residual": s3.a1_max_residual, "a2_max_residual": s3.a2_max_residual,
                          "exact": {"a0": EXACT_A0, "a1": EXACT_A1, "a2": EXACT_A2}},
        "status": Status.VERIFIED.value if s3.passed else Status.FAIL.value,
    })
    s3_status = Status.VERIFIED if s3.passed else Status.FAIL

    s3_manifold = Object(id="S3-MANIFOLD", type="mathematical_object", status=Status.PROPOSED,
                          role="upstream_construction",
                          carrier="unit 3-sphere, analytic constant-curvature control manifold "
                                  "(kappa=1, R=6)")
    s3_spectrum = Object(id="S3-SPECTRUM", type="spectral_data", status=Status.CALCULATED,
                          role="upstream_construction", dependencies=["S3-MANIFOLD"],
                          carrier="lambda_l = l(l+2), multiplicity (l+1)^2, l=0,1,2,... (closed form)")
    s3_heat_trace = Object(id="S3-HEAT-TRACE", type="heat_trace_function", status=Status.CALCULATED,
                            role="upstream_construction", dependencies=["S3-SPECTRUM"],
                            carrier="K(t) = sum_l (l+1)^2 exp(-t l(l+2)), truncated at l_max "
                                    "chosen so truncation error < 1e-35")
    s3_coeffs = Object(id="S3-HEAT-COEFFICIENTS", type="heat_kernel_coefficients", status=s3_status,
                        role="upstream_construction", dependencies=["S3-HEAT-TRACE"],
                        carrier=f"degree-3 local polynomial fit of Y(t)=K(t)(4*pi*t)^1.5 across "
                                f"{len(s3.fit_results)} fit windows; max relative residual vs exact "
                                f"(a0,a1,a2)=(2pi^2,2pi^2,pi^2): "
                                f"{max(s3.a0_max_residual, s3.a1_max_residual, s3.a2_max_residual):.3e}",
                        assumptions=["degree=2 quadratic fit alone is insufficient (biased by the "
                                     "neglected a3 t^3 term to |E_kappa|~1e-3); degree>=3 removes "
                                     "the leading bias -- see degree_sweep in provenance.verification"])
    s3_curvature = Object(id="S3-CURVATURE-CLOSURE", type="curvature_closure", status=s3_status,
                           role="upstream_construction", dependencies=["S3-HEAT-COEFFICIENTS"],
                           carrier=f"E_kappa = a1/a0 - sgn(a1)*sqrt(2a2/a0); "
                                   f"max|E_kappa| over swept windows = {s3.max_abs_e_kappa:.3e} "
                                   f"(tolerance {s3.tolerance:.0e}) -> {'PASSED' if s3.passed else 'FAILED'}")
    for obj in (s3_manifold, s3_spectrum, s3_heat_trace, s3_coeffs, s3_curvature):
        obj.provenance = make_provenance(
            source="compiler/backends/heat_kernel_sphere.py", object_id=obj.id,
            calculation_id="CALC-FC005-S3-CONTROL", status=obj.status,
            verification={"max_abs_e_kappa": s3.max_abs_e_kappa} if obj.id in
            ("S3-HEAT-COEFFICIENTS", "S3-CURVATURE-CLOSURE") else {},
        )
        registries.objects.add_object(obj)

    eq_s3 = Equation(
        id="EQ-FC005-S3-CURVATURE-RESIDUAL", lhs="E_kappa", rhs="a1/a0 - sgn(a1)*sqrt(2*a2/a0)",
        domain="S^3 heat-kernel control", status=s3_status, role="upstream_construction",
        dependencies=["S3-CURVATURE-CLOSURE"],
        derivation="independently executed regression test reproducing the workbook's ~1e-6 "
                   "closure result (workbook nominal 3.2156e-06 at window [0.0015,0.006]; this "
                   f"build: {s3.fit_results[1].e_kappa:.4e} at the same window, degree-3 fit)",
        verification={"max_abs_e_kappa": s3.max_abs_e_kappa, "tolerance": s3.tolerance,
                      "passed": s3.passed},
    )
    eq_s3.provenance = make_provenance(source="compiler/backends/heat_kernel_sphere.py",
                                        equation_id=eq_s3.id, calculation_id="CALC-FC005-S3-CONTROL",
                                        status=s3_status, verification={"passed": s3.passed})
    registries.equations.add_equation(eq_s3)

    t_s3 = Transformation(id="T-FC005-S3-CONTROL-CHAIN", domain="S3-MANIFOLD",
                           codomain="S3-CURVATURE-CLOSURE", action="analytic Spec -> K(t) -> fit -> E_kappa",
                           status=s3_status, dependencies=["S3-MANIFOLD"],
                           proof="closed-form S^3 spectrum, numpy heat-trace summation with "
                                 "controlled truncation, numpy.polyfit degree-3/4/5 sweep")
    t_s3.provenance = make_provenance(source="compiler/backends/heat_kernel_sphere.py",
                                       transformation_id=t_s3.id, status=s3_status,
                                       verification={"passed": s3.passed})
    registries.transformations.add_transformation(t_s3)

    # ---- 3. DESI chain: honestly OPEN / PENDING DATA ----
    # role="observational_output": per spec section 9 of the FC-005 build command,
    # this branch exists specifically to test whether the discrete-observation ->
    # continuum-operator bridge converges WHEN APPLIED TO real survey data -- the
    # catalogue is the empirical input/output side of a bridge test, not a
    # downstream value being smuggled in to bias an upstream theory selection
    # (that is what the firewall's "upstream_construction" default guards
    # against). Nothing in this branch feeds back into SELECTION-SIGMA, GAUGE-NODE,
    # or any other forward_chain_template node -- verified by
    # test_fc005_leakage.py::test_desi_branch_never_feeds_forward_chain_template.
    desi_catalogue = Object(
        id="DESI-CATALOGUE", type="pending_data_construction", status=Status.OPEN,
        role="observational_output",
        carrier="required: RA, DEC, z, and DESI weights (w_FKP, w_sys, ...) for a galaxy-level "
                "point catalogue. ABSENT from the repository, the current workspace, and all "
                "four supplied FC-005 workbooks -- the primary workbook's own "
                "'FC-005 Full Execution Index' sheet records this: 'No catalog file present "
                "in uploaded workbook.' This build independently confirmed the absence "
                "(filesystem search of the repository and /root/.claude/uploads).",
        assumptions=["STOP condition per spec section 25 of the FC-005 build command: required "
                     "DESI data is absent. Not fabricated. Code path is implemented and unit-"
                     "tested on synthetic data in compiler/backends/desi_graph.py."],
    )
    desi_catalogue.provenance = make_provenance(
        source="repository + workspace filesystem audit", object_id=desi_catalogue.id,
        status=Status.OPEN, verification={"catalogue_found": False},
    )
    registries.objects.add_object(desi_catalogue)

    desi_chain_specs = [
        ("GRAPH-G-DESI", "mathematical_object", ["DESI-CATALOGUE"],
         "G_DESI = (V,E,W): weighted observational graph from the DESI catalogue"),
        ("OPERATOR-L-DESI", "graph_laplacian_operator", ["GRAPH-G-DESI"], "L_DESI = D - W"),
        ("CONTINUUM-LIMIT-L-DESI", "mathematical_object", ["OPERATOR-L-DESI"],
         "L_tilde_(N,eps) = -L_N/(C_K N eps^(5/2)), d=3"),
        ("DESI-SPECTRUM", "spectral_data", ["CONTINUUM-LIMIT-L-DESI"], "Spec(Delta_h) via L_tilde eigenproblem"),
        ("DESI-HEAT-TRACE", "heat_trace_function", ["DESI-SPECTRUM"], "K(t) from the DESI-derived spectrum"),
        ("DESI-HEAT-COEFFICIENTS", "heat_kernel_coefficients", ["DESI-HEAT-TRACE"], "(a0,a1,a2) fit"),
        ("KAPPA-DESI", "curvature_closure", ["DESI-HEAT-COEFFICIENTS"], "kappa_spectral from DESI data"),
        ("E-KAPPA-DESI", "curvature_closure", ["KAPPA-DESI"], "E_kappa closure residual for DESI"),
        ("DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK", "curvature_closure", ["KAPPA-DESI"],
         "Delta_kappa = kappa_spectral - kappa_cosmological (independent cross-check)"),
    ]
    for node_id, type_, deps, desc in desi_chain_specs:
        obj = Object(id=node_id, type=type_, status=Status.OPEN, role="observational_output",
                     dependencies=deps, carrier=desc,
                     assumptions=["PENDING DATA: blocked on DESI-CATALOGUE (spec section 25 STOP "
                                  "condition). Pipeline code exists (compiler/backends/desi_graph.py) "
                                  "and is unit-tested on synthetic data only."])
        obj.provenance = make_provenance(source="compiler/backends/desi_graph.py (not executed on real data)",
                                          object_id=obj.id, status=Status.OPEN,
                                          verification={"blocked_on": "DESI-CATALOGUE"})
        registries.objects.add_object(obj)

    # ---- 3b. Explicit three-stage gates (never merged into one bit):
    # mathematical convergence != observational agreement != physical
    # validation. compiler/backends/desi_fc005_pipeline.py implements the
    # exact stop-on-failure procedure these three gates represent; when a
    # real catalogue is executed, each gate's status is set independently
    # from that run's MathematicalConvergenceResult / CurvatureClosureResult
    # / PhysicalValidationResult -- never collapsed into a single closed/
    # not-closed flag, and a later stage's status is never set unless the
    # earlier stage actually passed (spec: "never alter the model to
    # obtain closure").
    stage_gates = [
        ("MATHEMATICAL-CONVERGENCE-DESI",
         ["GRAPH-G-DESI", "OPERATOR-L-DESI", "CONTINUUM-LIMIT-L-DESI", "DESI-SPECTRUM"],
         "Stage 1: does L_tilde_(N,eps) converge under (N,eps) refinement? A property of the "
         "operator and the sampling, evaluated independently of any curvature or cosmological "
         "claim. See compiler/backends/desi_fc005_pipeline.py::run_mathematical_convergence. "
         "On failure, the exact failed node id is reported (e.g. OPERATOR-L-DESI for a "
         "disconnected graph) and the pipeline stops -- stages 2 and 3 are never evaluated."),
        ("CURVATURE-CLOSURE-DESI",
         ["MATHEMATICAL-CONVERGENCE-DESI", "DESI-HEAT-TRACE", "DESI-HEAT-COEFFICIENTS", "E-KAPPA-DESI"],
         "Stage 2: only evaluated if stage 1 converged. Does E_kappa fall below the "
         "predefined tolerance? A property of the fitted heat-kernel coefficients, "
         "independent of any external/observational comparison. See "
         "compiler/backends/desi_fc005_pipeline.py::run_curvature_closure. A stage-1 pass "
         "with a stage-2 failure is reported as a genuine curvature-closure failure, not "
         "reinterpreted or hidden."),
        ("PHYSICAL-VALIDATION-DESI",
         ["CURVATURE-CLOSURE-DESI", "DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK"],
         "Stage 3: only evaluated if stage 2 closed. Does kappa_spectral agree with an "
         "INDEPENDENTLY sourced kappa_cosmological (never derived from the same "
         "catalogue/run)? See compiler/backends/desi_fc005_pipeline.py::run_physical_validation, "
         "which raises rather than runs if no independent source is named."),
    ]
    for node_id, deps, desc in stage_gates:
        gate = Object(id=node_id, type="stage_gate", status=Status.OPEN,
                      role="observational_output", dependencies=deps, carrier=desc,
                      assumptions=["PENDING DATA: blocked on DESI-CATALOGUE. This gate's status "
                                   "is set independently by its own pipeline stage function when "
                                   "a real catalogue is executed -- never inferred from another "
                                   "gate's result and never force-closed."])
        gate.provenance = make_provenance(source="compiler/backends/desi_fc005_pipeline.py",
                                           object_id=gate.id, status=Status.OPEN,
                                           verification={"blocked_on": "DESI-CATALOGUE"})
        registries.objects.add_object(gate)

    # ---- 4. Semiclassical quantum/gravity boundary (spec section 18): OPEN, not full QG ----
    semiclassical = Object(
        id="SEMICLASSICAL-EINSTEIN-EQUATION", type="semiclassical_framework_equation",
        status=Status.PROPOSED, role="comparison",
        carrier="G_munu + Lambda g_munu = (8*pi*G/c^4) <T_munu>_ren -- established semiclassical "
                "gravity framework equation (external physics, not derived by this build).",
    )
    semiclassical.provenance = make_provenance(source="established semiclassical gravity literature",
                                                object_id=semiclassical.id, status=Status.PROPOSED)
    registries.objects.add_object(semiclassical)

    e_sc = Object(
        id="SEMICLASSICAL-RESIDUAL-E-SC", type="curvature_closure", status=Status.OPEN,
        role="upstream_construction", dependencies=["SEMICLASSICAL-EINSTEIN-EQUATION"],
        carrier="E_SC[g] = G_munu + Lambda g_munu - (8piG/c^4)<T_munu[g]>_ren",
        assumptions=["requires a constructed quantum state rho_Q and a renormalized stress "
                     "tensor <T_munu>_ren; neither is constructed in this build. This is "
                     "reported as SEMICLASSICAL CLOSURE scope only, never as full quantum "
                     "gravity (spec section 18)."],
    )
    e_sc.provenance = make_provenance(source="spec section 18 (FC-005 build command)",
                                       object_id=e_sc.id, status=Status.OPEN)
    registries.objects.add_object(e_sc)

    # ---- 5. Fisher-Rao -> Lorentzian obstruction (executed) ----
    fisher = run_fisher_lorentzian_obstruction_demo()
    calculations.append({
        "id": "CALC-FC005-FISHER-PSD", "kind": "fisher_information_psd_demonstration",
        "inputs": {"family": fisher.family},
        "results": {"eigenvalues_at_sigma1": fisher.numeric_eigenvalues_at_sigma1,
                    "F_symbolic": fisher.F_symbolic},
        "verification": {"is_positive_semidefinite": fisher.is_positive_semidefinite},
        "status": Status.VERIFIED.value if fisher.is_positive_semidefinite else Status.FAIL.value,
    })
    statistical_family = Object(id="FISHER-STATISTICAL-FAMILY", type="statistical_family",
                                 status=Status.PROPOSED, role="upstream_construction",
                                 carrier=fisher.family)
    statistical_family.provenance = make_provenance(source="compiler/verification/fisher_information.py",
                                                      object_id=statistical_family.id, status=Status.PROPOSED)
    registries.objects.add_object(statistical_family)

    fisher_psd = Equation(
        id="EQ-FC005-FISHER-PSD", lhs="v^T F v", rhs=">= 0 for all v",
        domain="information geometry", status=Status.VERIFIED if fisher.is_positive_semidefinite else Status.FAIL,
        role="upstream_construction", dependencies=["FISHER-STATISTICAL-FAMILY"],
        derivation="F computed by genuine sympy symbolic integration over the Gaussian family "
                   "(not hardcoded); eigenvalues confirmed >=0 both symbolically and by sampling "
                   "v^T F v >= 0 numerically at multiple sigma.",
        verification={"eigenvalues_at_sigma1": fisher.numeric_eigenvalues_at_sigma1},
    )
    fisher_psd.provenance = make_provenance(source="compiler/verification/fisher_information.py",
                                             equation_id=fisher_psd.id, calculation_id="CALC-FC005-FISHER-PSD",
                                             status=fisher_psd.status,
                                             verification={"is_positive_semidefinite": fisher.is_positive_semidefinite})
    registries.equations.add_equation(fisher_psd)

    fisher_obstruction = Equation(
        id="EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION", lhs="F", rhs="g_munu (Lorentzian, signature (-,+,+,+))",
        domain="information geometry vs spacetime geometry",
        status=Status.FALSIFIED, role="comparison", dependencies=["FISHER-STATISTICAL-FAMILY"],
        derivation="F is PSD (EQ-FC005-FISHER-PSD, executed); a Lorentzian metric requires a "
                   "strictly negative eigenvalue; signature is basis-independent (spectral "
                   "theorem); PSD and Lorentzian signatures are disjoint. Direct identification "
                   "F = g_munu is therefore FALSIFIED.",
        verification={"conclusion": fisher.conclusion},
    )
    fisher_obstruction.provenance = make_provenance(source="compiler/verification/fisher_information.py",
                                                      equation_id=fisher_obstruction.id, status=Status.FALSIFIED,
                                                      verification={"conclusion": fisher.conclusion})
    registries.equations.add_equation(fisher_obstruction)

    falsifications.append(FalsificationRecord(
        id="FALS-FC005-FISHER-LORENTZIAN", protocol="mathematical_invariance",
        target="Fisher-Rao metric F = Lorentzian spacetime metric g_munu",
        passed=False,
        detail=fisher.conclusion,
        evidence={"eigenvalues_at_sigma1": fisher.numeric_eigenvalues_at_sigma1,
                  "family": fisher.family},
    ))

    # ---- 6. Eigenvalue-uniqueness open obstruction (executed counterexample) ----
    eigen_cx = run_counterexample()
    calculations.append({
        "id": "CALC-FC005-EIGEN-UNIQUENESS", "kind": "spectrum_determines_operator_counterexample",
        "inputs": {"n": eigen_cx.n, "n_trials": eigen_cx.n_trials},
        "results": {"n_confirmed": eigen_cx.n_confirmed,
                    "spectra_match_max_residual": eigen_cx.spectra_match_max_residual},
        "verification": {"matrices_differ": eigen_cx.matrices_differ},
        "status": Status.VERIFIED.value if eigen_cx.matrices_differ else Status.FAIL.value,
    })
    spec_uniqueness = Object(
        id="SPEC-H-UNIQUENESS", type="operator_uniqueness_counterexample",
        status=Status.OPEN, role="upstream_construction",
        carrier=f"Spec(H) does NOT determine H: {eigen_cx.n_confirmed}/{eigen_cx.n_trials} random "
                f"trials confirm H' = U H U^dagger has identical spectrum "
                f"(max residual {eigen_cx.spectra_match_max_residual:.2e}) while H' != H.",
        assumptions=["OPEN OBSTRUCTION (spec section 7B / workbook R-003, TEST-006): eigenvalue-"
                     "only spectral data cannot reconstruct the operator, and therefore cannot "
                     "alone reconstruct a geometry (Spec(H) alone -> g_munu is NOT claimed)."],
    )
    spec_uniqueness.provenance = make_provenance(source="compiler/falsification/eigen_uniqueness.py",
                                                  object_id=spec_uniqueness.id,
                                                  calculation_id="CALC-FC005-EIGEN-UNIQUENESS",
                                                  status=Status.OPEN,
                                                  verification={"n_confirmed": eigen_cx.n_confirmed,
                                                                "n_trials": eigen_cx.n_trials})
    registries.objects.add_object(spec_uniqueness)

    falsifications.append(FalsificationRecord(
        id="FALS-FC005-EIGENVALUE-UNIQUENESS", protocol="structural_elimination",
        target="H is uniquely determined by Spec(H)",
        passed=False,
        detail=f"{eigen_cx.n_confirmed}/{eigen_cx.n_trials} random unitary-conjugation trials "
               "produce a distinct operator with identical spectrum.",
        evidence={"n_confirmed": eigen_cx.n_confirmed, "n_trials": eigen_cx.n_trials,
                  "spectra_match_max_residual": eigen_cx.spectra_match_max_residual},
    ))

    return {
        "calculations": calculations,
        "falsifications": falsifications,
        "s3_report": s3,
        "fisher_demo": fisher,
        "eigen_counterexample": eigen_cx,
        "n_reference_equations": len(ref_rows),
    }
