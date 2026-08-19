"""Registers the results of the two spec-mandated executable tests
(spec sections 31, 32) into the IR as Objects/Transformations, separate
from (and not descending from) the still-open forward-chain template
(spec section 6/10). GRAPH-G-SEED is a directly postulated mathematical
object, exactly as spec section 31 frames the first executable test.
"""
from __future__ import annotations

from compiler.backends.diffusion_metric import refinement_sweep
from compiler.backends.pipeline_graph_heatflow import DEFAULT_SWEEP, run_sweep
from compiler.core.ir import Equation, Object, Transformation
from compiler.core.status import Status
from compiler.falsification.protocols import FalsificationRecord
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance
from compiler.verification.verify import symbolic_verify


def _prove_laplacian_row_sum_zero(n: int = 5):
    """Symbolic proof that L @ 1 = 0 for L = D - A, any symmetric A with
    zero diagonal (a graph adjacency matrix) -- an exact DERIVED identity,
    not merely a numeric observation on one example."""
    import sympy
    A = sympy.zeros(n, n)
    symbols = {}
    for i in range(n):
        for j in range(i + 1, n):
            s = sympy.Symbol(f"a_{i}_{j}")
            symbols[(i, j)] = s
            A[i, j] = s
            A[j, i] = s
    D = sympy.diag(*[sum(A.row(i)) for i in range(n)])
    L = D - A
    ones = sympy.ones(n, 1)
    lhs = L * ones
    rhs = sympy.zeros(n, 1)
    results = [symbolic_verify(lhs[i], rhs[i], test=f"(L@1)[{i}]=0") for i in range(n)]
    all_passed = all(r.passed for r in results)
    return all_passed, results


def register_executable_tests(registries: MDCLRegistries) -> dict:
    """Runs Test 1 and Test 2, registers IR nodes + calculation entries,
    and returns {"test1_results": [...], "test2_reports": [...],
    "calculations": [...], "falsifications": [FalsificationRecord, ...]}."""

    seed = Object(
        id="GRAPH-G-SEED", type="mathematical_object", status=Status.PROPOSED,
        role="upstream_construction",
        carrier="A graph G=(V,E), directly postulated as a candidate mathematical "
                "object per spec section 31's own framing of the first executable "
                "test; not claimed to descend from the (OPEN) Selection/Vacuum chain.",
        assumptions=["Directly given test object, not derived from Sigma/Vacuum."],
    )
    seed.provenance = make_provenance(source="spec section 31", object_id=seed.id, status=Status.PROPOSED)
    registries.objects.add_object(seed)

    test1_results = run_sweep(DEFAULT_SWEEP)
    all_passed = all(r.passed for r in test1_results)
    calculations = []
    for r in test1_results:
        calculations.append({
            "id": f"CALC-T1-{r.label}",
            "kind": "graph_to_heatflow_pipeline",
            "inputs": {"topology": r.topology, "n": r.n},
            "results": {
                "eigenvalues": r.eigenvalues, "zero_modes": r.zero_modes,
                "spectral_gap": r.spectral_gap,
            },
            "verification": {
                "eigen_equation_residual": r.eigen_equation_residual,
                "heat_eigen_action_residual": r.heat_eigen_action_residual,
                "kernel_convergence": r.kernel_convergence,
                "exact_cross_check": r.exact_cross_check.to_dict() if r.exact_cross_check else None,
            },
            "status": Status.VERIFIED.value if r.passed else Status.FAIL.value,
        })

    operator_status = Status.CALCULATED
    spectrum_status = Status.VERIFIED if all_passed else Status.FAIL
    heatflow_status = Status.VERIFIED if all_passed else Status.FAIL
    kernel_status = Status.VERIFIED if all_passed else Status.FAIL

    operator = Object(id="OPERATOR-L", type="graph_laplacian_operator", status=operator_status,
                       role="upstream_construction", dependencies=["GRAPH-G-SEED"],
                       carrier="L = D - A, computed across a sweep of topologies/sizes "
                               f"({len(test1_results)} cases); see calculation_registry.")
    spectrum_obj = Object(id="SPECTRUM-L", type="spectral_data", status=spectrum_status,
                           role="upstream_construction", dependencies=["OPERATOR-L"],
                           carrier="Spec(L) = {lambda_n}, eigen-equation verified numerically "
                                   "(eigh) with exact sympy cross-check for n<=8.")
    heatflow = Object(id="HEAT-FLOW-R", type="heat_semigroup", status=heatflow_status,
                       role="upstream_construction", dependencies=["SPECTRUM-L"],
                       carrier="R(t) = e^{-tL}; R(t)phi_n = e^{-t lambda_n} phi_n verified numerically.")
    kernel = Object(id="KERNEL-PROJECTOR", type="projector", status=kernel_status,
                     role="upstream_construction", dependencies=["HEAT-FLOW-R"],
                     carrier="P_ker(L) = lim_{t->inf} e^{-tL}; hypotheses (symmetric, PSD) "
                             "checked programmatically before the limit is claimed, per graph.")
    for obj, calc_id in [(operator, "CALC-T1-OPERATOR"), (spectrum_obj, "CALC-T1-SPECTRUM"),
                          (heatflow, "CALC-T1-HEATFLOW"), (kernel, "CALC-T1-KERNEL")]:
        obj.provenance = make_provenance(
            source="compiler/backends/pipeline_graph_heatflow.py", object_id=obj.id,
            calculation_id=calc_id, status=obj.status,
            verification={"n_cases": len(test1_results), "n_passed": sum(r.passed for r in test1_results)},
        )
        registries.objects.add_object(obj)

    transformations = [
        Transformation(id="T-GRAPH-TO-OPERATOR", domain="GRAPH-G-SEED", codomain="OPERATOR-L",
                        action="L = D - A", status=operator_status, dependencies=["GRAPH-G-SEED"],
                        proof="D, A read directly off the graph's edge set; L = D - A by definition."),
        Transformation(id="T-OPERATOR-TO-SPECTRUM", domain="OPERATOR-L", codomain="SPECTRUM-L",
                        action="L phi_n = lambda_n phi_n", status=spectrum_status,
                        dependencies=["OPERATOR-L"],
                        proof="numpy.linalg.eigh (symmetric solver) cross-checked against sympy "
                              "exact characteristic-polynomial eigenvalues for n<=8."),
        Transformation(id="T-SPECTRUM-TO-HEATFLOW", domain="SPECTRUM-L", codomain="HEAT-FLOW-R",
                        action="R(t) = e^{-tL}", status=heatflow_status, dependencies=["SPECTRUM-L"],
                        proof="scipy.linalg.expm; eigen-action R(t)phi_n = e^{-t lambda_n} phi_n "
                              "verified to <1e-6 residual on every swept case."),
        Transformation(id="T-HEATFLOW-TO-KERNEL", domain="HEAT-FLOW-R", codomain="KERNEL-PROJECTOR",
                        action="lim_{t->inf} e^{-tL} = P_ker(L)", status=kernel_status,
                        dependencies=["HEAT-FLOW-R"],
                        preconditions=["L symmetric", "L positive semidefinite"],
                        proof="hypotheses checked numerically per case; residual ||e^{-tL}-P_ker(L)|| "
                              "probed at t scaled to 1/spectral_gap and confirmed < 1e-6."),
    ]
    for t in transformations:
        t.provenance = make_provenance(
            source="compiler/backends/pipeline_graph_heatflow.py",
            transformation_id=t.id, status=t.status,
            verification={"n_cases": len(test1_results),
                          "n_passed": sum(r.passed for r in test1_results),
                          "max_eigen_equation_residual": max((r.eigen_equation_residual for r in test1_results), default=0.0),
                          "max_heat_eigen_action_residual": max((r.heat_eigen_action_residual for r in test1_results), default=0.0)},
        )
        registries.transformations.add_transformation(t)

    # --- Test 2: Spec(L) -> diffusion distance -> metric candidate ---
    test2_reports = []
    falsifications: list[FalsificationRecord] = []
    for topology, sizes in [("cycle", [8, 16, 32, 64, 128]), ("path", [8, 16, 32, 64, 128]),
                             ("grid2d", [3, 4, 5, 6, 7])]:
        report = refinement_sweep(topology, sizes=sizes)
        test2_reports.append(report)
        calculations.append({
            "id": f"CALC-T2-{topology}",
            "kind": "diffusion_distance_refinement_sweep",
            "inputs": {"topology": topology, "sizes": sizes, "tau_multipliers": [0.5, 1.0, 2.0]},
            "results": {"normalized_sequence": report.normalized_sequence,
                        "classification": report.classification},
            "verification": {"relative_changes": report.relative_changes,
                              "across_time_choice_spread": report.across_time_choice_spread},
            "status": Status.CONDITIONAL.value if report.classification != "divergent" else Status.FAIL.value,
        })
        if report.classification == "non_unique":
            falsifications.append(FalsificationRecord(
                id=f"FALS-METRIC-UNIQUENESS-{topology}",
                protocol="structural_elimination",
                target=f"diffusion-metric-candidate({topology})",
                passed=False,
                detail=report.reason,
                evidence={"across_time_choice_spread": report.across_time_choice_spread,
                          "normalized_sequence": report.normalized_sequence},
            ))

    diffusion = Object(id="DIFFUSION-DISTANCE", type="diffusion_distance", status=Status.CALCULATED,
                        role="upstream_construction", dependencies=["SPECTRUM-L"],
                        carrier="d_t(i,j)^2 = sum_{n:lambda_n>0} e^{-2t lambda_n}(phi_n(i)-phi_n(j))^2")
    diffusion.provenance = make_provenance(source="compiler/backends/diffusion_metric.py",
                                            object_id=diffusion.id, status=Status.CALCULATED)
    registries.objects.add_object(diffusion)

    any_non_unique = any(r.classification == "non_unique" for r in test2_reports)
    metric_status = Status.CONDITIONAL if not any_non_unique else Status.CONDITIONAL
    metric = Object(
        id="METRIC-CANDIDATE", type="geometry_candidate", status=metric_status,
        role="upstream_construction", dependencies=["DIFFUSION-DISTANCE"],
        carrier="candidate g_ij extracted from diffusion-distance refinement; spec section 32 "
                "classification recorded per topology in calculation_registry (never 'exact').",
        assumptions=[
            "No analytic convergence proof registered; numeric refinement trend only.",
            f"{sum(1 for r in test2_reports if r.classification == 'non_unique')}/"
            f"{len(test2_reports)} topologies show the construction is NON-UNIQUE "
            "(depends on the free diffusion-time parameter) -- see falsification_registry.",
        ],
    )
    metric.provenance = make_provenance(source="compiler/backends/diffusion_metric.py",
                                         object_id=metric.id, status=metric_status,
                                         verification={"reports": [r.classification for r in test2_reports]})
    registries.objects.add_object(metric)

    t_diffusion = Transformation(id="T-SPECTRUM-TO-DIFFUSION", domain="SPECTRUM-L",
                                  codomain="DIFFUSION-DISTANCE", action="d_t(i,j)",
                                  status=Status.CALCULATED, dependencies=["SPECTRUM-L"],
                                  proof="direct evaluation of the diffusion-map distance formula.")
    t_metric = Transformation(id="T-DIFFUSION-TO-METRIC", domain="DIFFUSION-DISTANCE",
                               codomain="METRIC-CANDIDATE", action="refinement-sweep metric candidate",
                               status=metric_status, dependencies=["DIFFUSION-DISTANCE"],
                               proof="", postconditions=["classification in {approximate,conditional,"
                                                           "divergent,non_unique} -- never 'exact'"])
    for t in (t_diffusion, t_metric):
        t.provenance = make_provenance(source="compiler/backends/diffusion_metric.py",
                                        transformation_id=t.id, status=t.status)
        registries.transformations.add_transformation(t)

    # --- Equations: symbolic identities exercised by this build ---
    row_sum_passed, row_sum_evidence = _prove_laplacian_row_sum_zero()
    eq_row_sum = Equation(
        id="EQ-LAPLACIAN-ROW-SUM-ZERO", lhs="L @ ones_vector", rhs="0_vector",
        domain="graph Laplacian operators", status=Status.DERIVED if row_sum_passed else Status.FAIL,
        role="upstream_construction", dependencies=["OPERATOR-L"],
        derivation="D_ii := sum_j A_ij by definition, so (L@1)_i = D_ii - sum_j A_ij = 0 for every i; "
                   "proved symbolically (sympy) for a generic 5x5 symmetric zero-diagonal adjacency "
                   "matrix, not merely observed on one numeric example.",
        verification={"n_cases": len(row_sum_evidence),
                      "all_passed": row_sum_passed,
                      "precision": "exact"},
    )
    eq_row_sum.provenance = make_provenance(
        source="compiler/ir/executable_tests.py:_prove_laplacian_row_sum_zero",
        equation_id=eq_row_sum.id, status=eq_row_sum.status,
        verification={"n_cases": len(row_sum_evidence), "all_passed": row_sum_passed},
    )
    registries.equations.add_equation(eq_row_sum)

    eq_heat_eigen = Equation(
        id="EQ-HEAT-KERNEL-EIGEN-ACTION", lhs="R(t) phi_n", rhs="exp(-t*lambda_n) * phi_n",
        domain="heat semigroup", status=Status.VERIFIED if all_passed else Status.FAIL,
        role="upstream_construction", dependencies=["HEAT-FLOW-R"],
        derivation="follows from L phi_n = lambda_n phi_n and R(t) = e^{-tL} via the spectral "
                   "theorem for symmetric operators; verified numerically (not re-derived "
                   "symbolically) across every swept topology/size.",
        verification={"n_cases": len(test1_results),
                      "max_residual": max((r.heat_eigen_action_residual for r in test1_results), default=0.0),
                      "precision": "numeric"},
    )
    eq_heat_eigen.provenance = make_provenance(
        source="compiler/backends/heat_flow.py", equation_id=eq_heat_eigen.id, status=eq_heat_eigen.status,
        verification={"n_cases": len(test1_results), "all_passed": all_passed},
    )
    registries.equations.add_equation(eq_heat_eigen)

    return {
        "test1_results": test1_results,
        "test2_reports": test2_reports,
        "calculations": calculations,
        "falsifications": falsifications,
    }
