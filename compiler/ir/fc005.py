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

import json
from pathlib import Path

import openpyxl

from compiler.backends.desi_fc005_pipeline import run_gate1_on_pilot_fixture
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

    # ---- 3. DESI chain: real DESI DR1 data has been acquired and validated
    # (FC005_DESI_CATALOG_MANIFEST.json, FC005_DESI_VALIDATION_REPORT.md).
    # role="observational_output": per spec section 9 of the FC-005 build command,
    # this branch exists specifically to test whether the discrete-observation ->
    # continuum-operator bridge converges WHEN APPLIED TO real survey data -- the
    # catalogue is the empirical input/output side of a bridge test, not a
    # downstream value being smuggled in to bias an upstream theory selection
    # (that is what the firewall's "upstream_construction" default guards
    # against). Nothing in this branch feeds back into SELECTION-SIGMA, GAUGE-NODE,
    # or any other forward_chain_template node -- verified by
    # test_fc005_integration.py::test_desi_branch_never_feeds_forward_chain_template.
    #
    # Gate 1 (mathematical convergence) is executed here, live, on the small
    # committed REAL pilot fixture (data/desi/dr1/fc005/validated/pilot_fixture/),
    # so this is reproducible from a fresh checkout without a 64 MB download.
    # Per instruction: proceed automatically through Gate 1; enter Gate 2 only
    # if Gate 1 passes; never adjust parameters after seeing the result to
    # force a different outcome.
    gate1_run = run_gate1_on_pilot_fixture(repo_root)
    catalogue_acquired = gate1_run is not None

    desi_catalogue = Object(
        id="DESI-CATALOGUE", type="pending_data_construction",
        status=Status.CALCULATED if catalogue_acquired else Status.OPEN,
        role="observational_output",
        carrier=(
            f"DESI DR1 LRG SGC clustering catalogue, v1.5, real data acquired from the "
            f"official public release and checksum-verified. Pilot fixture: "
            f"{gate1_run['n_fixture_objects']} objects (0.4<=z<0.6 subsample), used here for a "
            f"reproducible-from-checkout live Gate 1 run. Full catalogue (662,492 objects) "
            f"downloaded separately to data/desi/dr1/fc005/raw/ (gitignored, re-fetchable via "
            f"download_desi_fc005.py)."
            if catalogue_acquired else
            "required: RA, DEC, z, and DESI weights for a galaxy-level point catalogue. "
            "ABSENT from the repository/workspace."
        ),
        assumptions=(
            ["Checksum-verified against the official DESI DR1 sha256 manifest "
             "(FC005_DESI_CATALOG_MANIFEST.json). See FC005_DESI_VALIDATION_REPORT.md for the "
             "full 12-point validation checklist (all PASSED)."]
            if catalogue_acquired else
            ["STOP condition per spec section 25 of the FC-005 build command: required DESI "
             "data is absent. Not fabricated."]
        ),
    )
    desi_catalogue.provenance = make_provenance(
        source="https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/LRG_SGC_clustering.dat.fits",
        object_id=desi_catalogue.id, status=desi_catalogue.status,
        verification={"catalogue_found": catalogue_acquired,
                      "checksum_sha256": "ae478557d9ef70257cc689197052515f5ebbc0b23359c81159a8ad3289332e69"
                      if catalogue_acquired else None},
    )
    registries.objects.add_object(desi_catalogue)

    if catalogue_acquired:
        mc = gate1_run["result"].mathematical_convergence
        # GRAPH-G-DESI and OPERATOR-L-DESI make no convergence claim of
        # their own -- each individual (N, eps) construction genuinely
        # succeeded (graph built, Laplacian symmetric, eigensolver residual
        # tiny at every point tested), so CALCULATED is correct for them
        # regardless of Gate 1's outcome. CONTINUUM-LIMIT-L-DESI *is* the
        # convergence claim, and DESI-SPECTRUM's meaning ("Spec of the
        # continuum operator") is only as trustworthy as that claim -- if
        # it FAILs, DESI-SPECTRUM must FAIL too, not stay CALCULATED
        # (caught by leakage_control_audit: a FAIL ancestor must never sit
        # beneath an active/CALCULATED node).
        graph_status = Status.CALCULATED
        operator_status = Status.CALCULATED
        continuum_limit_status = Status.CALCULATED if mc.converged else Status.FAIL
        spectrum_status = continuum_limit_status
        downstream_status = Status.OPEN  # never entered -- Gate 1 did not pass
        desi_source = f"compiler/backends/desi_fc005_pipeline.py (executed on {gate1_run['fixture_path']})"
        desi_verification = {"gate1_converged": mc.converged, "relative_changes": mc.relative_changes,
                             "failed_dependency": mc.failed_dependency}
    else:
        graph_status = operator_status = continuum_limit_status = spectrum_status = Status.OPEN
        downstream_status = Status.OPEN
        desi_source = "compiler/backends/desi_graph.py (not executed on real data)"
        desi_verification = {"blocked_on": "DESI-CATALOGUE"}

    desi_chain_specs = [
        ("GRAPH-G-DESI", "mathematical_object", ["DESI-CATALOGUE"], graph_status,
         "G_DESI = (V,E,W): weighted observational graph from the DESI catalogue"),
        ("OPERATOR-L-DESI", "graph_laplacian_operator", ["GRAPH-G-DESI"], operator_status, "L_DESI = D - W"),
        ("CONTINUUM-LIMIT-L-DESI", "mathematical_object", ["OPERATOR-L-DESI"], continuum_limit_status,
         "L_tilde_(N,eps) = -L_N/(C_K N eps^(5/2)), d=3"),
        ("DESI-SPECTRUM", "spectral_data", ["CONTINUUM-LIMIT-L-DESI"], spectrum_status,
         "Spec(-Delta_h) via -L_tilde eigenproblem (sign-corrected, see desi_fc005_pipeline.py)"),
        ("DESI-HEAT-TRACE", "heat_trace_function", ["DESI-SPECTRUM"], downstream_status,
         "K(t) from the DESI-derived spectrum"),
        ("DESI-HEAT-COEFFICIENTS", "heat_kernel_coefficients", ["DESI-HEAT-TRACE"], downstream_status,
         "(a0,a1,a2) fit"),
        ("KAPPA-DESI", "curvature_closure", ["DESI-HEAT-COEFFICIENTS"], downstream_status,
         "kappa_spectral from DESI data"),
        ("E-KAPPA-DESI", "curvature_closure", ["KAPPA-DESI"], downstream_status,
         "E_kappa closure residual for DESI"),
        ("DELTA-KAPPA-COSMOLOGICAL-CROSSCHECK", "curvature_closure", ["KAPPA-DESI"], downstream_status,
         "Delta_kappa = kappa_spectral - kappa_cosmological (independent cross-check)"),
    ]
    for node_id, type_, deps, status, desc in desi_chain_specs:
        assumptions = (["PENDING DATA: blocked on DESI-CATALOGUE (spec section 25 STOP condition)."]
                       if not catalogue_acquired else
                       ["Gate 1 (mathematical convergence) FAILED on the real pilot fixture -- this "
                        "node was never entered/executed, per instruction: only enter Gate 2 if "
                        "Gate 1 passes."] if status == Status.OPEN and node_id not in
                       ("GRAPH-G-DESI", "OPERATOR-L-DESI", "DESI-SPECTRUM") else [])
        obj = Object(id=node_id, type=type_, status=status, role="observational_output",
                     dependencies=deps, carrier=desc, assumptions=assumptions)
        obj.provenance = make_provenance(source=desi_source, object_id=obj.id, status=status,
                                          verification=desi_verification)
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
    if catalogue_acquired:
        mc = gate1_run["result"].mathematical_convergence
        gate_status = {
            "MATHEMATICAL-CONVERGENCE-DESI": Status.CALCULATED if mc.converged else Status.FAIL,
            "CURVATURE-CLOSURE-DESI": Status.OPEN,   # never entered: Gate 1 did not pass
            "PHYSICAL-VALIDATION-DESI": Status.OPEN,  # never entered: Gate 2 was never reached
        }
        gate_verification = {"gate1_converged": mc.converged,
                             "relative_changes": mc.relative_changes,
                             "N_values": gate1_run["N_values"], "tolerance": mc.tolerance}
    else:
        gate_status = {k: Status.OPEN for k in
                       ("MATHEMATICAL-CONVERGENCE-DESI", "CURVATURE-CLOSURE-DESI", "PHYSICAL-VALIDATION-DESI")}
        gate_verification = {"blocked_on": "DESI-CATALOGUE"}

    for node_id, deps, desc in stage_gates:
        status = gate_status[node_id]
        if not catalogue_acquired:
            assumptions = ["PENDING DATA: blocked on DESI-CATALOGUE. This gate's status is set "
                           "independently by its own pipeline stage function when a real "
                           "catalogue is executed -- never inferred from another gate's result "
                           "and never force-closed."]
        elif node_id == "MATHEMATICAL-CONVERGENCE-DESI":
            assumptions = [f"Executed live on {gate1_run['fixture_path']} "
                           f"({gate1_run['n_fixture_objects']} real objects). "
                           f"Result: {gate1_run['result'].summary}"]
        else:
            assumptions = ["Never entered: Gate 1 (mathematical convergence) did not pass on the "
                           "real pilot fixture. Per instruction, later gates are never evaluated "
                           "when an earlier gate fails."]
        gate = Object(id=node_id, type="stage_gate", status=status,
                      role="observational_output", dependencies=deps, carrier=desc,
                      assumptions=assumptions)
        gate.provenance = make_provenance(source="compiler/backends/desi_fc005_pipeline.py",
                                           object_id=gate.id, status=status,
                                           verification=gate_verification)
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

    if catalogue_acquired:
        mc = gate1_run["result"].mathematical_convergence
        calculations.append({
            "id": "CALC-FC005-DESI-GATE1", "kind": "desi_mathematical_convergence_gate",
            "inputs": {"fixture": gate1_run["fixture_path"], "N_values": gate1_run["N_values"],
                      "epsilon_values": gate1_run["epsilon_values"]},
            "results": {"relative_changes": mc.relative_changes,
                       "points": [p.__dict__ for p in mc.points]},
            "verification": {"converged": mc.converged, "tolerance": mc.tolerance,
                             "failed_dependency": mc.failed_dependency},
            "status": Status.CALCULATED.value if mc.converged else Status.FAIL.value,
        })

        # Follow-up sparse N-scaling investigation (separates finite-
        # resolution failure from point-process failure for the same
        # CONTINUUM-LIMIT-L-DESI failure -- see FC005_N_SCALING_REPORT.md
        # and FC005_CONTINUUM_DIAGNOSTIC_REPORT.md section 16). Loaded
        # from its pre-computed result file (a ~40-minute sparse-
        # eigensolver sweep up to N=64000, not re-run on every compiler
        # build) if present; absent gracefully otherwise. This node
        # records that the INVESTIGATION was executed -- it never sets
        # CONTINUUM-LIMIT-L-DESI's own status, which comes only from
        # CALC-FC005-DESI-GATE1 above.
        sparse_path = (Path(repo_root) / "data" / "desi" / "dr1" / "fc005" / "derived" /
                       "sparse_n_scaling_full_results.json")
        if sparse_path.exists():
            sparse_raw = json.loads(sparse_path.read_text())
            sparse_summary = {
                name: {
                    "converged": res["converged"], "relative_changes": res["relative_changes"],
                    "N_values_completed": [r["N"] for r in res["per_N"] if r["status"] == "OK"],
                }
                for name, res in sparse_raw.items()
            }
            calculations.append({
                "id": "CALC-FC005-DESI-SPARSE-N-SCALING",
                "kind": "desi_sparse_n_scaling_point_process_separation",
                "inputs": {"report": "FC005_N_SCALING_REPORT.md",
                          "raw_data": str(sparse_path.relative_to(Path(repo_root)))},
                "results": sparse_summary,
                "verification": {"purpose": "separate finite-resolution failure from "
                                            "point-process failure for CONTINUUM-LIMIT-L-DESI, "
                                            "per FC005_CONTINUUM_DIAGNOSTIC_REPORT.md section 16"},
                "status": Status.CALCULATED.value,
            })

    return {
        "calculations": calculations,
        "falsifications": falsifications,
        "s3_report": s3,
        "fisher_demo": fisher,
        "eigen_counterexample": eigen_cx,
        "n_reference_equations": len(ref_rows),
        "gate1_run": gate1_run,
    }
