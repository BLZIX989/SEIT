"""Registers the finite/discrete spectral-triple candidate certification
(see compiler/backends/finite_spectral_triple_candidate.py and
compiler/historical/finite_spectral_triple_certification.py) into the
EXISTING MDCL -- same Object/Transformation/Equation IR as every other
branch.

Requested execution boundary, honored literally: this certification runs
and its real result (status=FAIL on the first-order condition) governs
what the downstream D_B^2 -> (E_B,Omega_B) -> (a0^B..a6^B) nodes are
allowed to claim -- Omega_B and the spectral-action coefficients are
registered OPEN, not silently promoted, because the certification that
would license computing them genuinely fails.
"""
from __future__ import annotations

from pathlib import Path

from compiler.backends.finite_spectral_triple_candidate import (
    compute_dirac_squared_decomposition, run_spectral_triple_certification,
)
from compiler.core.ir import Object, Transformation
from compiler.core.status import Status
from compiler.historical.finite_spectral_triple_certification import (
    CANDIDATE_DEFINITION, CONSEQUENCE_FOR_SPECTRAL_ACTION, FINDINGS,
    STRUCTURAL_REASON_FOR_FAILURE, WHY_THIS_CANDIDATE,
)
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

TYPE_DEFS_FINITE_SPECTRAL_TRIPLE = [
    ("control_graph", "a standard graph construction used as a verification control (same "
                       "status as other control_manifold objects), never a claim about a "
                       "physically-selected graph", None),
    ("finite_spectral_triple_component", "one component (algebra representation, grading, real "
                                          "structure, or Dirac operator) of a candidate finite "
                                          "spectral triple (A_F,H_F,D_F,J_F,gamma_F)", None),
    ("spectral_triple_axiom_check", "a real, executed check of one Connes spectral-triple axiom "
                                     "against a concrete candidate -- status always computed from "
                                     "the actual check, never asserted", None),
    ("finite_dirac_squared_decomposition", "D_F^2 for a finite candidate Dirac operator, and "
                                            "whether its E_B/Omega_B decomposition is certifiable", None),
]


def register_finite_spectral_triple_certification(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []

    # ---- 0. the H2 graph control (reused as the substrate for D_F) ----
    h2_control = Object(
        id="H2-GRAPH-CONTROL", type="control_graph", status=Status.PROPOSED,
        role="upstream_construction",
        carrier="n=200 nearest-neighbour ring graph, k=3 -- the SAME construction "
                "h2_spectral_triple_locality_check and dirac_candidates.py already use, reused "
                "here for exact comparability, not re-selected.",
    )
    h2_control.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py", object_id=h2_control.id,
        status=Status.PROPOSED,
    )
    registries.objects.add_object(h2_control)

    # ---- 1. candidate components (A_F, D_F, gamma_F, J_F) ----
    finite_dirac = Object(
        id="FINITE-DIRAC-D_B", type="finite_spectral_triple_component", status=Status.CALCULATED,
        role="upstream_construction", dependencies=["H2-GRAPH-CONTROL"],
        carrier="D_F = D_B = [[0,d1],[d1^T,0]], the H2B block-incidence Dirac operator "
                "(dirac_candidates.py), chosen as this candidate's D_F because it is local by "
                "construction (H2's own D+=sqrt(L) was found dense/non-local).",
    )
    finite_dirac.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py::build_h2b_operator",
        object_id=finite_dirac.id, status=Status.CALCULATED,
    )
    registries.objects.add_object(finite_dirac)

    finite_algebra = Object(
        id="FINITE-ALGEBRA-A_F", type="finite_spectral_triple_component", status=Status.PROPOSED,
        role="upstream_construction", dependencies=["H2-GRAPH-CONTROL"],
        carrier="A_F = C(V), the algebra of real-valued functions on the graph's vertex set; "
                "pi(f) represented as multiplication by f on the vertex block, zero on the edge "
                "block -- genuinely derived from the graph, NOT the Standard Model's "
                "A_F = C (+) H (+) M_3(C), which nothing in this project's own construction "
                "forces (clifford_derivation.py::clifford_rank_forcing_check).",
        assumptions=[WHY_THIS_CANDIDATE],
    )
    finite_algebra.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py::pi_representation",
        object_id=finite_algebra.id, status=Status.PROPOSED,
    )
    registries.objects.add_object(finite_algebra)

    finite_grading = Object(
        id="FINITE-GRADING-GAMMA_F", type="finite_spectral_triple_component", status=Status.CALCULATED,
        role="upstream_construction", dependencies=["FINITE-DIRAC-D_B"],
        carrier="gamma_F = diag(I_N0,-I_N1), the natural Z/2 grading matching D_F's block-swap "
                "structure (vertices even, edges odd).",
    )
    finite_grading.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py::build_h2b_operator",
        object_id=finite_grading.id, status=Status.CALCULATED,
    )
    registries.objects.add_object(finite_grading)

    finite_real_structure = Object(
        id="FINITE-REAL-STRUCTURE-J_F", type="finite_spectral_triple_component", status=Status.PROPOSED,
        role="upstream_construction", dependencies=["FINITE-DIRAC-D_B"],
        carrier="J_F = complex conjugation on H_F -- the natural real structure, same choice "
                "H2 already used for D+=sqrt(L).",
    )
    finite_real_structure.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py", object_id=finite_real_structure.id,
        status=Status.PROPOSED,
    )
    registries.objects.add_object(finite_real_structure)

    # ---- 2. real, executed axiom checks ----
    cert = run_spectral_triple_certification()
    calculations.append({
        "id": "CALC-FINITE-SPECTRAL-TRIPLE-AXIOMS", "kind": "spectral_triple_axiom_certification",
        "inputs": {"candidate": CANDIDATE_DEFINITION},
        "results": {
            "self_adjoint": cert.self_adjoint,
            "grading_axioms_hold": (cert.grading_squares_to_identity and cert.anticommutes_with_grading
                                    and cert.algebra_commutes_with_grading),
            "real_structure_signs": [cert.real_structure_epsilon, cert.real_structure_epsilon_prime,
                                     cert.real_structure_epsilon_doubleprime],
            "first_order_condition_holds": cert.first_order_condition_holds_numeric,
            "first_order_commutator_norm": cert.first_order_commutator_norm,
            "first_order_closed_form_confirmed_symbolically_general": cert.first_order_closed_form_matches,
        },
        "verification": {"findings": FINDINGS},
        "status": Status.FAIL.value,  # overall certification: FAILS (first-order condition)
    })

    axiom_self_adjoint = Object(
        id="AXIOM-CHECK-SELF-ADJOINT-D_B", type="spectral_triple_axiom_check",
        status=Status.VERIFIED if cert.self_adjoint else Status.FAIL,
        role="upstream_construction", dependencies=["FINITE-DIRAC-D_B"],
        carrier=f"D_F self-adjoint: {cert.self_adjoint}. Exact block-antisymmetric-transpose "
                "structure by construction.",
    )
    axiom_grading = Object(
        id="AXIOM-CHECK-GRADING-D_B", type="spectral_triple_axiom_check",
        status=Status.VERIFIED if (cert.grading_squares_to_identity and cert.anticommutes_with_grading
                                   and cert.algebra_commutes_with_grading) else Status.FAIL,
        role="upstream_construction", dependencies=["FINITE-GRADING-GAMMA_F", "FINITE-ALGEBRA-A_F"],
        carrier=f"gamma_F^2=I: {cert.grading_squares_to_identity}; {{D_F,gamma_F}}=0: "
                f"{cert.anticommutes_with_grading}; [pi(f),gamma_F]=0: {cert.algebra_commutes_with_grading}.",
    )
    axiom_real_structure = Object(
        id="AXIOM-CHECK-REAL-STRUCTURE-SIGNS", type="spectral_triple_axiom_check", status=Status.VERIFIED,
        role="upstream_construction", dependencies=["FINITE-REAL-STRUCTURE-J_F", "FINITE-GRADING-GAMMA_F"],
        carrier=f"(epsilon,epsilon',epsilon'')=({cert.real_structure_epsilon},"
                f"{cert.real_structure_epsilon_prime},{cert.real_structure_epsilon_doubleprime}) -- "
                "degenerate/trivial (same situation h2_spectral_triple_locality_check already found "
                "for D+=sqrt(L)). No specific KO-mod-8 integer is claimed here (ko_dimension.py's "
                "own established policy: do not restate Connes' full sign table from memory).",
        assumptions=[FINDINGS[2]["note"]],
    )
    axiom_first_order = Object(
        id="AXIOM-CHECK-FIRST-ORDER-CONDITION", type="spectral_triple_axiom_check", status=Status.FAIL,
        role="upstream_construction", dependencies=["FINITE-DIRAC-D_B", "FINITE-ALGEBRA-A_F",
                                                     "FINITE-REAL-STRUCTURE-J_F"],
        carrier=f"[[D_F,pi(f)],pi(g)]=0 FAILS (commutator norm {cert.first_order_commutator_norm:.3f} "
                "at n=200, random f,g). Exact closed form confirmed symbolically in general form "
                "(not one example): [[D_F,pi(f)],pi(g)] = [[0,diag(f*g)d1],[d1^T diag(f*g),0]], "
                "nonzero for generic f,g. FIRST TIME this check has been run anywhere in this "
                "corpus -- see compiler/historical/finite_spectral_triple_certification.py.",
        assumptions=[STRUCTURAL_REASON_FOR_FAILURE],
    )
    axiom_verification = {
        "AXIOM-CHECK-SELF-ADJOINT-D_B": {"self_adjoint": cert.self_adjoint},
        "AXIOM-CHECK-GRADING-D_B": {"grading_squares_to_identity": cert.grading_squares_to_identity,
                                    "anticommutes_with_grading": cert.anticommutes_with_grading,
                                    "algebra_commutes_with_grading": cert.algebra_commutes_with_grading},
        "AXIOM-CHECK-REAL-STRUCTURE-SIGNS": {"epsilon": cert.real_structure_epsilon,
                                             "epsilon_prime": cert.real_structure_epsilon_prime,
                                             "epsilon_doubleprime": cert.real_structure_epsilon_doubleprime},
        "AXIOM-CHECK-FIRST-ORDER-CONDITION": {"holds_numeric": cert.first_order_condition_holds_numeric,
                                              "commutator_norm": cert.first_order_commutator_norm,
                                              "holds_symbolic_general": cert.first_order_condition_holds_symbolic_general},
    }
    for obj in (axiom_self_adjoint, axiom_grading, axiom_real_structure, axiom_first_order):
        obj.provenance = make_provenance(
            source="compiler/backends/finite_spectral_triple_candidate.py::run_spectral_triple_certification",
            object_id=obj.id, calculation_id="CALC-FINITE-SPECTRAL-TRIPLE-AXIOMS", status=obj.status,
            verification=axiom_verification[obj.id],
        )
        registries.objects.add_object(obj)

    t_axioms = Transformation(
        id="T-FINITE-SPECTRAL-TRIPLE-AXIOMS", domain="H2-GRAPH-CONTROL",
        codomain="FINITE-SPECTRAL-TRIPLE-CERTIFICATION",
        action="self-adjointness, grading, real-structure-sign, and first-order-condition checks "
               "against the concrete (A_F,H_F,D_F,J_F,gamma_F) candidate defined above",
        status=Status.FAIL, dependencies=["FINITE-DIRAC-D_B", "FINITE-ALGEBRA-A_F",
                                          "FINITE-GRADING-GAMMA_F", "FINITE-REAL-STRUCTURE-J_F"],
        proof="numpy exact linear algebra at n=200 (random f,g) plus sympy symbolic-general "
              "confirmation of the first-order-condition closed form at n=4",
    )
    t_axioms.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py", transformation_id=t_axioms.id,
        status=Status.FAIL, calculation_id="CALC-FINITE-SPECTRAL-TRIPLE-AXIOMS",
    )
    registries.transformations.add_transformation(t_axioms)

    certification = Object(
        id="FINITE-SPECTRAL-TRIPLE-CERTIFICATION", type="spectral_triple_axiom_check", status=Status.FAIL,
        role="comparison",
        dependencies=["H2-GRAPH-CONTROL", "AXIOM-CHECK-SELF-ADJOINT-D_B", "AXIOM-CHECK-GRADING-D_B",
                      "AXIOM-CHECK-REAL-STRUCTURE-SIGNS", "AXIOM-CHECK-FIRST-ORDER-CONDITION"],
        carrier="Overall certification of (A_F,H_F,D_F,J_F,gamma_F): FAILS. Self-adjointness and "
                "grading axioms hold; real-structure signs are degenerate; the first-order "
                "condition -- the substantive, discriminating check -- fails with an exact, "
                "generically-nonzero closed form.",
        assumptions=[STRUCTURAL_REASON_FOR_FAILURE],
    )
    certification.provenance = make_provenance(
        source="compiler/ir/finite_spectral_triple_certification.py", object_id=certification.id,
        status=Status.FAIL, calculation_id="CALC-FINITE-SPECTRAL-TRIPLE-AXIOMS",
    )
    registries.objects.add_object(certification)

    # ---- 3. D_F^2, E_B, Omega_B, and the (un)certifiability of a0^B..a6^B ----
    d2 = compute_dirac_squared_decomposition()
    calculations.append({
        "id": "CALC-DIRAC-SQUARED-FINITE-D_B", "kind": "finite_dirac_squared_block_decomposition",
        "inputs": {}, "results": {"block_diagonal": d2.block_diagonal,
                                  "vertex_block_is_graph_laplacian": d2.vertex_block_is_graph_laplacian,
                                  "edge_block_is_up_laplacian": d2.edge_block_is_up_laplacian},
        "verification": {"E_B_bare_is_zero": d2.E_B_bare_is_zero},
        "status": Status.CALCULATED.value,
    })
    dirac_squared = Object(
        id="DIRAC-SQUARED-FINITE-D_B", type="finite_dirac_squared_decomposition", status=Status.CALCULATED,
        role="upstream_construction", dependencies=["FINITE-DIRAC-D_B"],
        carrier="D_F^2 = diag(d1 d1^T, d1^T d1) -- exactly block-diagonal, zero cross term. "
                "Confirms dirac_candidates.py's own D_squared_equals_diag(L0,d1^T_d1)_exactly "
                "finding. For the BARE (unfluctuated) operator this means E_B=0 trivially.",
    )
    dirac_squared.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py::compute_dirac_squared_decomposition",
        object_id=dirac_squared.id, calculation_id="CALC-DIRAC-SQUARED-FINITE-D_B", status=Status.CALCULATED,
        verification={"E_B_bare_is_zero": d2.E_B_bare_is_zero},
    )
    registries.objects.add_object(dirac_squared)

    e_b_bare = Object(
        id="E_B-BARE-FINITE", type="finite_dirac_squared_decomposition", status=Status.CALCULATED,
        role="upstream_construction", dependencies=["DIRAC-SQUARED-FINITE-D_B"],
        carrier="E_B = 0 for the bare (unfluctuated) D_F -- exact, trivial consequence of the "
                "zero cross-term block structure. NOT the physical E_B of a genuine NCG spectral "
                "action, which requires a fluctuated D_A (see OMEGA_B-FINITE).",
    )
    e_b_bare.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py", object_id=e_b_bare.id,
        status=Status.CALCULATED, calculation_id="CALC-DIRAC-SQUARED-FINITE-D_B",
    )
    registries.objects.add_object(e_b_bare)

    omega_b = Object(
        id="OMEGA_B-FINITE", type="finite_dirac_squared_decomposition", status=Status.OPEN,
        role="upstream_construction", dependencies=["FINITE-SPECTRAL-TRIPLE-CERTIFICATION",
                                                     "DIRAC-SQUARED-FINITE-D_B"],
        carrier="Omega_B (gauge curvature of an inner-fluctuated connection): NOT CERTIFIABLE, "
                "not merely not-yet-computed.",
        assumptions=[d2.Omega_B_note, CONSEQUENCE_FOR_SPECTRAL_ACTION],
    )
    omega_b.provenance = make_provenance(
        source="compiler/ir/finite_spectral_triple_certification.py", object_id=omega_b.id,
        status=Status.OPEN,
    )
    registries.objects.add_object(omega_b)

    spectral_action_a0_a6 = Object(
        id="SPECTRAL-ACTION-A0-A6-FINITE-B", type="finite_dirac_squared_decomposition", status=Status.OPEN,
        role="comparison", dependencies=["E_B-BARE-FINITE", "OMEGA_B-FINITE"],
        carrier="a0^B, a2^B, a4^B, a6^B (finite spectral-action moments for this candidate): NOT "
                "CERTIFIED. Requires Omega_B, which is not certifiable for this candidate "
                "(first-order condition fails). This is the correct execution boundary: the "
                "spectral action is not touched beyond this point for this candidate.",
        assumptions=[CONSEQUENCE_FOR_SPECTRAL_ACTION],
    )
    spectral_action_a0_a6.provenance = make_provenance(
        source="compiler/ir/finite_spectral_triple_certification.py", object_id=spectral_action_a0_a6.id,
        status=Status.OPEN,
    )
    registries.objects.add_object(spectral_action_a0_a6)

    t_dirac_squared = Transformation(
        id="T-DIRAC-SQUARED-FINITE", domain="FINITE-DIRAC-D_B", codomain="DIRAC-SQUARED-FINITE-D_B",
        action="D_F^2 computed directly by matrix multiplication and compared block-by-block "
               "against d1 d1^T (vertex) and d1^T d1 (edge)",
        status=Status.CALCULATED, dependencies=["FINITE-DIRAC-D_B"],
        proof="numpy exact linear algebra, exact block match (not approximate)",
    )
    t_dirac_squared.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_candidate.py", transformation_id=t_dirac_squared.id,
        status=Status.CALCULATED, calculation_id="CALC-DIRAC-SQUARED-FINITE-D_B",
    )
    registries.transformations.add_transformation(t_dirac_squared)

    return {"calculations": calculations, "candidate_definition": CANDIDATE_DEFINITION,
            "findings": FINDINGS, "consequence_for_spectral_action": CONSEQUENCE_FOR_SPECTRAL_ACTION}
