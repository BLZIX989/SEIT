"""Registers the D_A^2=-(nabla^2+E) / Seeley-DeWitt a0,a2,a4,a6
verification (see compiler/backends/lichnerowicz_seeley_dewitt.py and
compiler/historical/seeley_dewitt_verification.py) into the EXISTING MDCL
-- same Object/Transformation/Equation IR, same Status enum, same
Provenance model, same MDCLRegistries as every other branch.

Must run AFTER register_fc005() (compiler/ir/fc005.py): reuses the
already-registered S3-MANIFOLD object as the control manifold for the
numeric Seeley-DeWitt a0/a2/a4 check, rather than registering a
duplicate.

SCOPE, repeated a third time deliberately (backend module docstring,
historical record, and here -- this note must survive wherever a reader
lands first): every status below verifies the GENERAL Lichnerowicz/
Gilkey formulas on standard CONTROL manifolds. None of it certifies this
project's own candidate Dirac operator D_B or attaches physical meaning
to seit_lang.spectral_action's Tr f(D/Lambda) for that construction.
"""
from __future__ import annotations

from pathlib import Path

from compiler.backends.lichnerowicz_seeley_dewitt import (
    verify_lichnerowicz_gauge_term, verify_lichnerowicz_gravity_term, verify_seeley_dewitt_E_dependence,
)
from compiler.core.ir import Object, Transformation
from compiler.core.status import Status
from compiler.historical.seeley_dewitt_verification import (
    A6_SCOPE_NOTE, ERRORS_FOUND_AND_FIXED, METHOD_SUMMARY,
)
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

TYPE_DEFS_SEELEY_DEWITT = [
    ("control_manifold", "a standard, independently-known-analytic manifold used as a verification "
                          "control (same status as S3-MANIFOLD), never a claim about this project's "
                          "own constructions", None),
    ("lichnerowicz_term", "one piece (gauge or gravity) of the general D_A^2=-(nabla^2+E) identity, "
                           "verified on a control manifold", "mathematical_object"),
    ("seeley_dewitt_coefficient", "a general Gilkey heat-kernel coefficient (a0, a2, a4, or a6), "
                                   "verified or left OPEN on a control manifold", "mathematical_object"),
    ("spectral_action_certification", "whether Tr f(D_A/Lambda) can be certified for physical use; "
                                       "OPEN until every Seeley-DeWitt coefficient it depends on is "
                                       "resolved", None),
]


def register_seeley_dewitt_verification(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []

    control_s2 = Object(
        id="CONTROL-MANIFOLD-S2", type="control_manifold", status=Status.PROPOSED,
        role="upstream_construction",
        carrier="round unit 2-sphere, standard constant-curvature control manifold (R=2), used ONLY "
                "to verify the general Lichnerowicz gravity-term formula -- not a claim about any "
                "physical manifold this project constructs elsewhere.",
    )
    control_s2.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", object_id=control_s2.id,
        status=Status.PROPOSED,
    )
    registries.objects.add_object(control_s2)

    control_flat_2d = Object(
        id="CONTROL-FLAT-2D", type="control_manifold", status=Status.PROPOSED,
        role="upstream_construction",
        carrier="flat 2D Euclidean space (R=0 identically), standard control used ONLY to verify the "
                "general Lichnerowicz gauge-term formula in isolation from the gravity term -- not a "
                "claim about any physical space this project constructs elsewhere.",
    )
    control_flat_2d.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", object_id=control_flat_2d.id,
        status=Status.PROPOSED,
    )
    registries.objects.add_object(control_flat_2d)

    # ---- gauge term (flat 2D, exact symbolic) ----
    gauge_result = verify_lichnerowicz_gauge_term()
    calculations.append({
        "id": "CALC-LICHNEROWICZ-GAUGE-TERM", "kind": "symbolic_operator_composition_flat_2d",
        "inputs": {"gauge_field": "abstract abelian A_mu(x,y), arbitrary symbolic functions", "curvature": "R=0 (flat)"},
        "results": {"E_gauge_formula": gauge_result.E_gauge_formula,
                    "clifford_algebra_checked": gauge_result.clifford_algebra_checked},
        "verification": {"residual_is_zero": gauge_result.residual_is_zero},
        "status": Status.VERIFIED.value if gauge_result.residual_is_zero else Status.FAIL.value,
    })
    gauge_status = Status.VERIFIED if gauge_result.residual_is_zero else Status.FAIL
    lichnerowicz_gauge = Object(
        id="LICHNEROWICZ-GAUGE-TERM", type="lichnerowicz_term", status=gauge_status,
        role="upstream_construction", dependencies=["CONTROL-FLAT-2D"],
        carrier=f"D_A^2=-(nabla^2+E), E={gauge_result.E_gauge_formula}. Exact zero residual, "
                "symbolic operator composition, flat 2D Euclidean space, an abstract abelian gauge "
                "field only (R=0 identically -- isolates this term from the gravity term cleanly).",
        assumptions=["Overall i factor required in D_A for self-adjointness (D_A^2>=0); first "
                     "attempt without it gave a residual exactly 2x the nabla^2 term, diagnosed "
                     "and fixed -- see compiler/historical/seeley_dewitt_verification.py."],
    )
    lichnerowicz_gauge.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py::verify_lichnerowicz_gauge_term",
        object_id=lichnerowicz_gauge.id, calculation_id="CALC-LICHNEROWICZ-GAUGE-TERM", status=gauge_status,
        verification={"residual_is_zero": gauge_result.residual_is_zero},
    )
    registries.objects.add_object(lichnerowicz_gauge)

    t_gauge = Transformation(
        id="T-LICHNEROWICZ-GAUGE-TERM", domain="CONTROL-FLAT-2D", codomain="LICHNEROWICZ-GAUGE-TERM",
        action="D_A = i*gamma^a(d_a+iA_a), squared by direct symbolic operator composition",
        status=gauge_status, dependencies=["CONTROL-FLAT-2D"],
        proof="sympy symbolic Matrix differential-operator composition, exact (not numeric) zero residual",
    )
    t_gauge.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", transformation_id=t_gauge.id,
        status=gauge_status, verification={"residual_is_zero": gauge_result.residual_is_zero},
    )
    registries.transformations.add_transformation(t_gauge)

    # ---- gravity term (round S^2, exact symbolic, coefficient solved) ----
    gravity_result = verify_lichnerowicz_gravity_term()
    calculations.append({
        "id": "CALC-LICHNEROWICZ-GRAVITY-TERM", "kind": "symbolic_operator_composition_round_s2",
        "inputs": {"manifold": "round unit S^2", "gauge_field": "none (R contribution isolated)"},
        "results": {"omega12_derived": gravity_result.omega12_derived, "R_computed": gravity_result.R_computed,
                    "lichnerowicz_coefficient_c": str(gravity_result.lichnerowicz_coefficient_c)},
        "verification": {"christoffel_checked": gravity_result.christoffel_checked,
                         "matches_textbook_quarter": gravity_result.matches_textbook_quarter},
        "status": Status.VERIFIED.value if gravity_result.matches_textbook_quarter else Status.FAIL.value,
    })
    gravity_status = Status.VERIFIED if gravity_result.matches_textbook_quarter else Status.FAIL
    lichnerowicz_gravity = Object(
        id="LICHNEROWICZ-GRAVITY-TERM-S2", type="lichnerowicz_term", status=gravity_status,
        role="upstream_construction", dependencies=["CONTROL-MANIFOLD-S2"],
        carrier=f"D^2=-(nabla^2+E), E=c*R with c={gravity_result.lichnerowicz_coefficient_c} SOLVED "
                f"FOR (not assumed) on the round unit S^2 (R={gravity_result.R_computed}, "
                "independently computed, not quoted). Reproduces the textbook Lichnerowicz formula "
                "D^2=-nabla^2+R/4 exactly.",
        assumptions=["Spin connection derived from the Cartan structure equation, not quoted.",
                     "Riemann tensor sign convention reused verbatim from the earlier FRW/Bianchi-"
                     "identity verification pass (an independent from-scratch attempt here first "
                     "gave R=-2, traced to an index-order inconsistency, discarded in favor of the "
                     "already-validated convention) -- see "
                     "compiler/historical/seeley_dewitt_verification.py."],
    )
    lichnerowicz_gravity.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py::verify_lichnerowicz_gravity_term",
        object_id=lichnerowicz_gravity.id, calculation_id="CALC-LICHNEROWICZ-GRAVITY-TERM",
        status=gravity_status, verification={"matches_textbook_quarter": gravity_result.matches_textbook_quarter},
    )
    registries.objects.add_object(lichnerowicz_gravity)

    t_gravity = Transformation(
        id="T-LICHNEROWICZ-GRAVITY-TERM", domain="CONTROL-MANIFOLD-S2", codomain="LICHNEROWICZ-GRAVITY-TERM-S2",
        action="D^2 on round S^2 via Cartan spin connection + Levi-Civita Christoffel symbols, "
               "coefficient of E=c*R solved by direct symbolic composition",
        status=gravity_status, dependencies=["CONTROL-MANIFOLD-S2"],
        proof="sympy: Cartan structure equation for omega^{12}, Christoffel symbols from the metric "
              "(cross-checked vs closed form), Riemann tensor (validated convention reused), "
              "sp.solve for c -- not asserted",
    )
    t_gravity.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", transformation_id=t_gravity.id,
        status=gravity_status, verification={"matches_textbook_quarter": gravity_result.matches_textbook_quarter},
    )
    registries.transformations.add_transformation(t_gravity)

    # ---- combined general identity ----
    dirac_squared_status = gauge_status if gauge_status == Status.FAIL else gravity_status
    dirac_squared = Object(
        id="DIRAC-SQUARED-LICHNEROWICZ-GENERAL", type="lichnerowicz_term", status=dirac_squared_status,
        role="upstream_construction", dependencies=["LICHNEROWICZ-GAUGE-TERM", "LICHNEROWICZ-GRAVITY-TERM-S2"],
        carrier="D_A^2=-(nabla^2+E), E=-R/4*I + i*F_12*gamma^1*gamma^2 (gravity+gauge pieces combined; "
                "verified separately, on separate control manifolds, so neither can mask an error in "
                "the other). GENERAL formula only -- see spectral_action_certification note on scope.",
    )
    dirac_squared.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", object_id=dirac_squared.id,
        status=dirac_squared_status,
        verification={"gauge_term_residual_is_zero": gauge_result.residual_is_zero,
                      "gravity_term_matches_textbook_quarter": gravity_result.matches_textbook_quarter},
    )
    registries.objects.add_object(dirac_squared)

    # ---- Seeley-DeWitt a0, a2, a4 (numeric, reuses S3-MANIFOLD control) ----
    sd_report = verify_seeley_dewitt_E_dependence()
    calculations.append({
        "id": "CALC-SEELEY-DEWITT-A0-A2-A4", "kind": "numeric_heat_trace_fit_E_dependence_s3",
        "inputs": {"E_values": [p.E for p in sd_report.points], "fit_degree": sd_report.fit_degree,
                   "tolerance": sd_report.tolerance},
        "results": {"points": [{"E": p.E, "a0_fit": p.a0_fit, "a1_fit": p.a1_fit, "a2_fit": p.a2_fit,
                                "a0_residual": p.a0_residual, "a1_residual": p.a1_residual,
                                "a2_residual": p.a2_residual} for p in sd_report.points]},
        "verification": {"all_passed": sd_report.all_passed},
        "status": Status.VERIFIED.value if sd_report.all_passed else Status.FAIL.value,
    })
    sd_status = Status.VERIFIED if sd_report.all_passed else Status.FAIL
    seeley_dewitt_a0a2a4 = Object(
        id="SEELEY-DEWITT-A0-A2-A4", type="seeley_dewitt_coefficient", status=sd_status,
        role="upstream_construction", dependencies=["DIRAC-SQUARED-LICHNEROWICZ-GENERAL", "S3-MANIFOLD"],
        carrier=f"Gilkey a0=tr(I)*Vol, a2=tr(E+R/6)*Vol, a4=(1/360)tr[60ER+180E^2+5R^2-2Ric^2+2Riem^2]*Vol "
                f"-- E-dependent terms (60ER, 180E^2, never previously exercised in this project's E=0-only "
                f"S3 control) confirmed numerically at {len(sd_report.points)} distinct E values, max "
                f"residual {max(p.a2_residual for p in sd_report.points):.2e}, tolerance {sd_report.tolerance:.0e}.",
        assumptions=["Degree-3 polynomial fit (existing S3 control default) showed a real, diagnosed "
                     "fit-window bias at large E (2.52e-4 at E=2.5, above tolerance); degree=4 used "
                     "instead, confirmed by degree-sweep convergence (2.52e-4->1.79e-6->1.24e-8 at "
                     "degrees 3,4,5) to be bias, not a formula error."],
    )
    seeley_dewitt_a0a2a4.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py::verify_seeley_dewitt_E_dependence",
        object_id=seeley_dewitt_a0a2a4.id, calculation_id="CALC-SEELEY-DEWITT-A0-A2-A4", status=sd_status,
        verification={"all_passed": sd_report.all_passed,
                      "max_a2_residual": max(p.a2_residual for p in sd_report.points)},
    )
    registries.objects.add_object(seeley_dewitt_a0a2a4)

    t_seeley_dewitt = Transformation(
        id="T-SEELEY-DEWITT-A0-A2-A4-NUMERIC", domain="S3-MANIFOLD", codomain="SEELEY-DEWITT-A0-A2-A4",
        action="shifted operator L=-Delta-E on S^3, exact spectrum, degree-4 heat-trace polynomial "
               "fit vs Gilkey-predicted closed forms, 4 distinct E values",
        status=sd_status, dependencies=["S3-MANIFOLD"],
        proof="reuses this project's own already-verified S3 heat-trace-fit machinery "
              "(compiler/backends/heat_kernel_sphere.py, compiler/verification/heat_kernel_fit.py), "
              "extended to nonzero constant E",
    )
    t_seeley_dewitt.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", transformation_id=t_seeley_dewitt.id,
        status=sd_status, verification={"all_passed": sd_report.all_passed},
    )
    registries.transformations.add_transformation(t_seeley_dewitt)

    # ---- a6: honestly OPEN, no Transformation registered (nothing executed) ----
    seeley_dewitt_a6 = Object(
        id="SEELEY-DEWITT-A6-GENERAL", type="seeley_dewitt_coefficient", status=Status.OPEN,
        role="upstream_construction", dependencies=["SEELEY-DEWITT-A0-A2-A4"],
        carrier="General Gilkey a6 heat-kernel coefficient (position-dependent E(x), nonabelian gauge "
                "curvature Omega_{mu nu}, Delta E, dozen-plus pure-curvature invariants).",
        assumptions=[A6_SCOPE_NOTE],
    )
    seeley_dewitt_a6.provenance = make_provenance(
        source="compiler/backends/lichnerowicz_seeley_dewitt.py", object_id=seeley_dewitt_a6.id,
        status=Status.OPEN, verification={"a6_status": "OPEN", "elementary_consistency_check_only": True},
    )
    registries.objects.add_object(seeley_dewitt_a6)

    # ---- spectral action certification: OPEN, blocked on a6 AND on D_B's own spectral-triple status ----
    spectral_action_cert = Object(
        id="SPECTRAL-ACTION-TR-F-CERTIFICATION", type="spectral_action_certification", status=Status.OPEN,
        role="comparison", dependencies=["SEELEY-DEWITT-A6-GENERAL"],
        carrier="Whether Tr f(D_A/Lambda) can be certified as a physically meaningful spectral action. "
                "OPEN for two independent reasons, both required: (1) a6 is not yet resolved (see "
                "SEELEY-DEWITT-A6-GENERAL); (2) even once the GENERAL formula chain is complete, this "
                "verifies control-manifold mathematics only -- it does NOT certify this project's own "
                "candidate D_B for seit_lang.spectral_action's Tr f(D/Lambda), which has never been "
                "shown to satisfy the full Connes spectral-triple axioms "
                "(seit_lang/spectral_action.py's own module docstring).",
        assumptions=["seit_lang/spectral_action.py already refuses to call its own Tr(D^k) a "
                     "Seeley-DeWitt coefficient for exactly this reason; this record does not "
                     "relax that refusal."],
    )
    spectral_action_cert.provenance = make_provenance(
        source="compiler/ir/seeley_dewitt_verification.py", object_id=spectral_action_cert.id,
        status=Status.OPEN,
    )
    registries.objects.add_object(spectral_action_cert)

    return {"calculations": calculations, "method_summary": METHOD_SUMMARY,
            "errors_found_and_fixed": ERRORS_FOUND_AND_FIXED}
