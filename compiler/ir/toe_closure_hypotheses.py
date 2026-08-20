"""Master SEIT Theory Derivation Campaign: registers the four primary
load-bearing hypotheses (H1-H4) as genuine IR nodes, backed by the real
executed tests in compiler/backends/toe_closure_hypotheses.py.

Per the campaign's governing instruction (Section II, XVII): these nodes
are registered role="comparison" -- decounterfactualization tests of the
axioms COUNTERFACTUAL_MASTER_THEORY_OF_EVERYTHING.docx left unproven --
never as upstream selectors for the canonical forward chain. No node
here is promoted past what its own executed evidence actually earns.
H4's specific "intersection via triality" claim is registered FALSIFIED
(a genuine, proved mathematical impossibility -- rank-counting on
compact Lie groups), matching this project's existing precedent for
EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION. H1-H3 are registered FAIL/OPEN
(real negative evidence, not proven-impossible, per the campaign's own
status discipline: never convert FAIL into FALSIFIED without an actual
impossibility proof).
"""
from __future__ import annotations

from pathlib import Path

from compiler.backends.toe_closure_hypotheses import (
    LIE_GROUP_FACTS, h1_selection_wellposedness_analysis, h2_spectral_triple_locality_check,
    h3_load_correction_test_results, h4_g2_spin8_construction_check,
)
from compiler.core.ir import Equation, Object
from compiler.core.status import Status
from compiler.falsification.protocols import FalsificationRecord
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

TYPE_DEFS_TOE_CLOSURE = [
    ("closure_hypothesis_test", "an executed test of one of the four primary load-bearing "
                                 "hypotheses (H1-H4) required to decounterfactualize the "
                                 "COUNTERFACTUAL_MASTER_THEORY_OF_EVERYTHING manuscript", None),
]


def register_toe_closure_hypotheses(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []
    falsifications: list[FalsificationRecord] = []

    # ---- H1 ----
    h1_result = h1_selection_wellposedness_analysis(repo_root)
    h1_obj = Object(
        id="H1-SELECTION-WELLPOSEDNESS", type="closure_hypothesis_test",
        status=Status.OPEN, role="comparison",
        carrier=h1_result["verdict"],
        assumptions=["Tests whether G*=argmax_G Pi(G)/S(G) is a well-posed optimization "
                     "problem given the compiler's own actual definitions (or absence "
                     "thereof) of Mathset, Pi, and S."],
    )
    h1_obj.provenance = make_provenance(
        source="compiler/backends/toe_closure_hypotheses.py::h1_selection_wellposedness_analysis",
        object_id=h1_obj.id, status=Status.OPEN, verification=h1_result,
    )
    registries.objects.add_object(h1_obj)
    calculations.append({"id": "CALC-H1-SELECTION-WELLPOSEDNESS", "kind": "definitional_wellposedness_audit",
                          "inputs": {"repo_root": str(repo_root)}, "status": h1_obj.status.value,
                          "verification": h1_result, **h1_result})

    # ---- H2 ----
    h2_result = h2_spectral_triple_locality_check()
    h2_obj = Object(
        id="H2-SPECTRAL-TRIPLE-LOCALITY", type="closure_hypothesis_test",
        status=Status.FAIL, role="comparison",
        carrier=h2_result["verdict"],
        assumptions=["Tests the structural locality prerequisite for D+=sqrt(L) to serve as "
                     "a genuine Dirac-type operator in a spectral triple; does not attempt "
                     "the full axiom-by-axiom certification (fixing a specific algebra A and "
                     "computing the first-order condition directly), noted as future work."],
    )
    h2_obj.provenance = make_provenance(
        source="compiler/backends/toe_closure_hypotheses.py::h2_spectral_triple_locality_check",
        object_id=h2_obj.id, status=Status.FAIL, verification=h2_result,
    )
    registries.objects.add_object(h2_obj)
    calculations.append({"id": "CALC-H2-SPECTRAL-TRIPLE-LOCALITY", "kind": "spectral_triple_locality_test",
                          "inputs": {"n": 200, "k_neighbors": 3, "seed": 0}, "status": h2_obj.status.value,
                          "verification": h2_result, **h2_result})

    # ---- H3 (reuses the real, already-executed numerical experiment) ----
    h3_result = h3_load_correction_test_results(repo_root)
    h3_obj = Object(
        id="H3-FC005-CORRECTION-TEST", type="closure_hypothesis_test",
        status=Status.FAIL, role="comparison",
        dependencies=["CONTINUUM-LIMIT-L-DESI"],
        carrier=h3_result["verdict"],
        assumptions=["Additional diagnostic evidence extending (not overwriting) the frozen "
                     "FC005_CHECKPOINT.md state. Tested against real DESI DR1 LRG SGC data "
                     "at N=4000->8000, a smaller N pair than the frozen checkpoint's own "
                     "best-case N=32000->64000 result, so this is not a direct re-run of the "
                     "checkpoint's own claim, but an independent test of correction hypotheses."],
    )
    h3_obj.provenance = make_provenance(
        source="run_fc005_h3_correction_test.py -> FC005_H3_CORRECTION_TEST_RESULTS.json",
        object_id=h3_obj.id, status=Status.FAIL, verification=h3_result,
    )
    registries.objects.add_object(h3_obj)
    calculations.append({"id": "CALC-H3-FC005-CORRECTION-TEST", "kind": "discrete_continuum_correction_test",
                          "inputs": {"n_small": 4000, "n_large": 8000, "seed": 20250819}, "status": h3_obj.status.value,
                          "verification": h3_result, **h3_result})

    # ---- H4 ----
    h4_result = h4_g2_spin8_construction_check()
    h4_falsified_eq = Equation(
        id="EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM", status=Status.FALSIFIED, role="comparison",
        lhs="G2 (intersection via triality) Spin(8)", rhs="SU(3) x SU(2) x U(1)",
        domain="compact Lie group theory",
        derivation="claimed in COUNTERFACTUAL_MASTER_THEORY_OF_EVERYTHING.docx section 8; "
                   "disproved by rank-counting -- see FALS-H4-G2-TRIALITY-RANK-OBSTRUCTION",
        verification=h4_result,
        assumptions=["The counterfactual manuscript's specific restatement of the gauge-"
                     "closure claim (COUNTERFACTUAL_MASTER_THEORY_OF_EVERYTHING.docx section 8)."],
    )
    h4_falsified_eq.provenance = make_provenance(
        source="compiler/backends/toe_closure_hypotheses.py::h4_g2_spin8_construction_check",
        object_id=h4_falsified_eq.id, status=Status.FALSIFIED, verification=h4_result,
    )
    registries.equations.add_equation(h4_falsified_eq)

    h4_fals = FalsificationRecord(
        id="FALS-H4-G2-TRIALITY-RANK-OBSTRUCTION",
        protocol="mathematical_invariance_test (rank of compact Lie subgroups)",
        target="EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM",
        passed=False,
        detail=h4_result["rank_argument"]["conclusion"],
        evidence=h4_result,
    )
    falsifications.append(h4_fals)

    h4_original_obj = Object(
        id="H4-DIRECT-PRODUCT-CLAIM-UNCONSTRUCTED", type="closure_hypothesis_test",
        status=Status.OPEN, role="comparison",
        carrier="The repository's own original claim (Aut(octonions) x Spin(8) superset "
                "SU(3)xSU(2)xU(1), a direct product, not an intersection) is NOT ruled out "
                "by the H4 rank argument, but remains completely unconstructed anywhere in "
                "this repository -- no embedding, decomposition, or uniqueness argument exists.",
        assumptions=[h4_result["distinct_from_repository_original_direct_product_claim"]["rank_check_for_this_different_claim"]],
    )
    h4_original_obj.provenance = make_provenance(
        source="compiler/backends/toe_closure_hypotheses.py::h4_g2_spin8_construction_check",
        object_id=h4_original_obj.id, status=Status.OPEN, verification=h4_result,
    )
    registries.objects.add_object(h4_original_obj)
    calculations.append({"id": "CALC-H4-G2-SPIN8-GAUGE-CLOSURE", "kind": "lie_group_rank_dimension_check",
                          "inputs": {"groups_compared": list(LIE_GROUP_FACTS.keys())},
                          "status": h4_original_obj.status.value,
                          "verification": h4_result, **h4_result})

    return {"calculations": calculations, "falsifications": falsifications}
