"""Registers Phase 1 (TFT-002B evaluation/promotion), Phase 2 (coupled
doubled recovery), and Phase 3 (honest sign scan, no forced KO=6 claim)
into the EXISTING MDCL. Must run after
register_finite_spectral_triple_certification (reuses H2-GRAPH-CONTROL)
and register_finite_spectral_triple_recovery (extends its narrative).
"""
from __future__ import annotations

from pathlib import Path

from compiler.backends.finite_spectral_triple_recovery_coupled import (
    run_coupled_recovery_certification,
)
from compiler.backends.finite_spectral_triple_tft002b import evaluate_tft002b
from compiler.core.ir import Object, Transformation
from compiler.core.status import Status
from compiler.historical.finite_spectral_triple_tft002b_and_coupled_recovery import (
    PHASE1_SUMMARY, PHASE2_SUMMARY, PHASE3_EXPLICIT_LIMIT, PHASE3_SUMMARY,
)
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

TYPE_DEFS_TFT002B_COUPLED_RECOVERY = [
    ("evaluated_dirac_candidate", "a Dirac-type operator candidate with explicit invariant "
                                   "checks, promoted to canonical only if the checks pass and "
                                   "no dependency regression is introduced", None),
    ("coupled_recovery_component", "a component of the nontrivially-coupled doubled recovery "
                                    "(Phase 2), extending the uncoupled recovery with a genuine "
                                    "inter-copy coupling", None),
]


def register_tft002b_and_coupled_recovery(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []

    # ---- Phase 1: TFT-002B evaluation ----
    tft = evaluate_tft002b()
    calculations.append({
        "id": "CALC-TFT002B-EVALUATION", "kind": "dirac_candidate_invariant_evaluation",
        "inputs": {"n_triangles": tft.n_triangles},
        "results": {"self_adjoint": tft.self_adjoint, "grading_axioms_hold":
                    tft.grading_squares_to_identity and tft.anticommutes_with_grading,
                    "squares_to_full_hodge_laplacian": tft.squares_to_full_hodge_laplacian,
                    "edge_block_max_abs_difference": tft.edge_block_max_abs_difference,
                    "spectrum_range": [tft.spectrum_min, tft.spectrum_max]},
        "verification": {"promote_to_canonical": tft.promote_to_canonical},
        "status": Status.VERIFIED.value if tft.promote_to_canonical else Status.FAIL.value,
    })
    tft_status = Status.VERIFIED if tft.promote_to_canonical else Status.FAIL

    tft002b_candidate = Object(
        id="TFT-002B-CANDIDATE", type="evaluated_dirac_candidate", status=tft_status,
        role="upstream_construction", dependencies=["H2-GRAPH-CONTROL"],
        carrier=f"D=[[0,d1,0],[d1^T,0,d2],[0,d2^T,0]] on C0(+)C1(+)C2, n_triangles={tft.n_triangles}. "
                + PHASE1_SUMMARY,
        assumptions=[tft.promotion_rationale],
    )
    tft002b_candidate.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_tft002b.py::evaluate_tft002b",
        object_id=tft002b_candidate.id, calculation_id="CALC-TFT002B-EVALUATION", status=tft_status,
        verification={"promote_to_canonical": tft.promote_to_canonical,
                      "edge_block_differs_from_2block": tft.edge_block_differs_from_2block_up_term},
    )
    registries.objects.add_object(tft002b_candidate)

    t_tft002b = Transformation(
        id="T-TFT002B-EVALUATION", domain="H2-GRAPH-CONTROL", codomain="TFT-002B-CANDIDATE",
        action="build the 3-graded Hodge-Dirac operator at full scale (n=200) and check "
               "self-adjointness, grading axioms, exact square, and comparison against D_B",
        status=tft_status, dependencies=["H2-GRAPH-CONTROL"],
        proof="numpy exact linear algebra at n=200, all invariants checked directly",
    )
    t_tft002b.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_tft002b.py", transformation_id=t_tft002b.id,
        status=tft_status, calculation_id="CALC-TFT002B-EVALUATION",
        verification={"promote_to_canonical": tft.promote_to_canonical},
    )
    registries.transformations.add_transformation(t_tft002b)

    # ---- Phase 2: coupled recovery ----
    cr = run_coupled_recovery_certification()
    calculations.append({
        "id": "CALC-COUPLED-RECOVERY-CERTIFICATION", "kind": "nontrivially_coupled_doubled_spectral_triple_recovery",
        "inputs": {"mechanism": PHASE2_SUMMARY},
        "results": {"coupling_is_nonzero": cr.coupling_is_nonzero,
                    "coupling_is_not_proportional_to_D": cr.coupling_is_not_proportional_to_D,
                    "self_adjoint": cr.self_adjoint,
                    "grading_axioms_hold": cr.grading_squares_to_identity and cr.anticommutes_with_grading
                                           and cr.algebra_commutes_with_grading,
                    "first_order_condition_holds": cr.first_order_condition_holds_numeric,
                    "first_order_residual_norm": cr.first_order_residual_norm,
                    "real_structure_signs": [cr.real_structure_epsilon, cr.real_structure_epsilon_prime,
                                             cr.real_structure_epsilon_doubleprime]},
        "verification": {"first_order_condition_holds_symbolic_general": cr.first_order_condition_holds_symbolic_general},
        "status": Status.VERIFIED.value if cr.first_order_condition_holds_numeric else Status.FAIL.value,
    })
    cr_status = Status.VERIFIED if cr.first_order_condition_holds_numeric else Status.FAIL

    coupling_matrix = Object(
        id="COUPLING-MATRIX-C", type="coupled_recovery_component", status=Status.CALCULATED,
        role="upstream_construction", dependencies=["TFT-002B-CANDIDATE"],
        carrier=f"C = i*mu*(independently-weighted (d1,d2) incidence pattern), nonzero: "
                f"{cr.coupling_is_nonzero}, not proportional to D: {cr.coupling_is_not_proportional_to_D}, "
                f"anticommutes with grading: {cr.coupling_anticommutes_with_grading} (required for "
                "{D_F'',gamma_F''}=0 to hold at all).",
    )
    coupling_matrix.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_recovery_coupled.py", object_id=coupling_matrix.id,
        status=Status.CALCULATED,
    )
    registries.objects.add_object(coupling_matrix)

    coupled_certification = Object(
        id="COUPLED-RECOVERY-CERTIFICATION", type="coupled_recovery_component", status=cr_status,
        role="comparison", dependencies=["TFT-002B-CANDIDATE", "COUPLING-MATRIX-C"],
        carrier=f"Overall certification of the coupled doubled recovery over TFT-002B: "
                f"{cr_status.value}. " + PHASE2_SUMMARY,
        assumptions=[PHASE3_SUMMARY, PHASE3_EXPLICIT_LIMIT],
    )
    coupled_certification.provenance = make_provenance(
        source="compiler/ir/finite_spectral_triple_tft002b_and_coupled_recovery.py",
        object_id=coupled_certification.id, status=cr_status,
        calculation_id="CALC-COUPLED-RECOVERY-CERTIFICATION",
        verification={"first_order_condition_holds": cr.first_order_condition_holds_numeric,
                      "residual_norm": cr.first_order_residual_norm},
    )
    registries.objects.add_object(coupled_certification)

    t_coupled = Transformation(
        id="T-COUPLED-RECOVERY-AXIOMS", domain="TFT-002B-CANDIDATE", codomain="COUPLED-RECOVERY-CERTIFICATION",
        action="self-adjointness, grading, real-structure-sign, and first-order-condition checks "
               "against the DOUBLED, NONTRIVIALLY-COUPLED candidate over TFT-002B",
        status=cr_status, dependencies=["TFT-002B-CANDIDATE", "COUPLING-MATRIX-C"],
        proof="numpy exact linear algebra at n=200 (genuine complex random f,g,C) plus sympy "
              "symbolic-general confirmation (f,g,coupling weights all free symbols) that "
              "pi(f) C pi(g) vanishes identically",
    )
    t_coupled.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_recovery_coupled.py", transformation_id=t_coupled.id,
        status=cr_status, calculation_id="CALC-COUPLED-RECOVERY-CERTIFICATION",
        verification={"first_order_condition_holds": cr.first_order_condition_holds_numeric},
    )
    registries.transformations.add_transformation(t_coupled)

    # ---- Phase 3: honest sign scan, explicitly not forced to a target ----
    sign_scan = Object(
        id="PHASE3-KO-DIMENSION-SIGN-SCAN", type="coupled_recovery_component", status=Status.CALCULATED,
        role="comparison", dependencies=["COUPLED-RECOVERY-CERTIFICATION"],
        carrier=PHASE3_SUMMARY,
        assumptions=[PHASE3_EXPLICIT_LIMIT],
    )
    sign_scan.provenance = make_provenance(
        source="compiler/historical/finite_spectral_triple_tft002b_and_coupled_recovery.py",
        object_id=sign_scan.id, status=Status.CALCULATED,
        verification={"clean_signature": [1, 1, 1], "asymmetric_conventions_give_undetermined_epsilon_prime": True},
    )
    registries.objects.add_object(sign_scan)

    return {"calculations": calculations, "phase1_summary": PHASE1_SUMMARY,
            "phase2_summary": PHASE2_SUMMARY, "phase3_summary": PHASE3_SUMMARY,
            "phase3_explicit_limit": PHASE3_EXPLICIT_LIMIT}
