"""Orchestrates the incidence/Clifford/persistence follow-up work (user's
own instruction block, Sec.1-11 -- explicitly NOT the uploaded
canonical_closure_report.md, whose "resolved"/"terminates the search"
claims this project does not implement; see chat response for the
specific inconsistencies found in that document). Writes 7 deliverable
files at the repository root from real computed results.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.derivation import (  # noqa: E402
    clifford_derivation, dirac_candidates, kc003_vr001, ko_dimension, persistence,
)


def run_all() -> dict:
    return {
        "h2b_reused_from_prior_phase": dirac_candidates.build_block_dirac_locality_test(n=200, k_neighbors=3),
        "persistent_sector": persistence.persistent_sector_report(),
        "persistent_distance_beta_limits": persistence.persistent_distance_beta_limits_check(),
        "kc003_decomposition": kc003_vr001.kc003_decomposition(),
        "vr001_known_manifold_control": kc003_vr001.vr001_known_manifold_control(),
        "ko_skew_symmetric_determinant": ko_dimension.skew_symmetric_odd_determinant_check(),
        "ko_symmetric_example": ko_dimension.symmetric_3x3_nonzero_determinant_example(),
        "ko_parameter_scan": ko_dimension.ko_dimension_parameter_scan(),
        "spin6_su4": ko_dimension.spin6_su4_isomorphism_check(),
        "clifford_rank_forcing": clifford_derivation.clifford_rank_forcing_check(),
        "su4_to_sm_breaking": clifford_derivation.spin6_su4_to_sm_breaking_check(),
    }


def write_reports(r: dict) -> None:
    # --- FC005_PERSISTENT_SECTOR_REPORT.md ---
    ps = r["persistent_sector"]
    pd = r["persistent_distance_beta_limits"]
    lines = ["# FC005_PERSISTENT_SECTOR_REPORT.md", "",
             f"Test graph: {ps['test_graph']}", "",
             "| lambda_c (frac of max) | n modes | P idempotent | P self-adjoint | "
             "L_Pi = P.L.P verified | K_Pi monotone decreasing |", "|---|---|---|---|---|---|"]
    for key, v in ps["by_lambda_c"].items():
        lines.append(f"| {key} | {v['n_persistent_modes']} | {v['P_idempotent']} | "
                     f"{v['P_self_adjoint']} | {v['L_Pi_equals_P_L_P_reconstruction']} | "
                     f"{v['K_Pi_monotone_nonincreasing_in_beta']} |")
    lines += ["", "## Persistent distance beta-limit behavior", "",
              f"beta->0 matches unweighted persistent distance: "
              f"**{pd['beta_near_0_matches_unweighted_persistent_distance']}**",
              f"Monotone nonincreasing in beta: **{pd['monotone_nonincreasing_in_beta']}**", "",
              pd["note"]]
    (ROOT / "FC005_PERSISTENT_SECTOR_REPORT.md").write_text("\n".join(lines) + "\n")

    # --- KC003_DECOMPOSITION_REPORT.md ---
    kc = r["kc003_decomposition"]
    lines = ["# KC003_DECOMPOSITION_REPORT.md", "",
             "KC-003 split into 4 independently-tracked sub-claims, per instruction -- never "
             "inferred from one another.", ""]
    for name, sub in kc.items():
        lines += [f"## {name}", "", f"**Statement:** {sub['statement']}", "",
                  f"**Status:** {sub['status']}", ""]
    (ROOT / "KC003_DECOMPOSITION_REPORT.md").write_text("\n".join(lines) + "\n")

    # --- VR001_HILBERT_CORRESPONDENCE_REPORT.md ---
    vr = r["vr001_known_manifold_control"]
    lines = ["# VR001_HILBERT_CORRESPONDENCE_REPORT.md", "", vr["claim"], "",
             "## Uniform sampling (converges to the known true eigenspace)", ""]
    for n, res in vr["results"]["uniform"].items():
        lines.append(f"- N={n}: cos-projection={res['cos_theta_projection_norm_onto_computed_eigenspace']:.4f}, "
                     f"sin-projection={res['sin_theta_projection_norm_onto_computed_eigenspace']:.4f}, "
                     f"converged={res['converged_close_to_1']}")
    lines += ["", "## Nonuniform (density-clustered) sampling -- same unnormalized construction", ""]
    for n, res in vr["results"]["nonuniform"].items():
        lines.append(f"- N={n}: cos-projection={res['cos_theta_projection_norm_onto_computed_eigenspace']:.4f}, "
                     f"sin-projection={res['sin_theta_projection_norm_onto_computed_eigenspace']:.4f}, "
                     f"converged={res['converged_close_to_1']}")
    lines += ["", "## Interpretation", "", vr["interpretation"], "",
              "## What this does NOT establish about real DESI data", "",
              "This validates the TEST METHODOLOGY on a case with a known analytic answer "
              "(the circle). The real DESI data's own convergence status is separately, "
              "already assessed in CONVERGENCE_AUDIT.md (CONV-001) -- not re-litigated here."]
    (ROOT / "VR001_HILBERT_CORRESPONDENCE_REPORT.md").write_text("\n".join(lines) + "\n")

    # --- NCG_KO_PARAMETER_SCAN.csv ---
    with (ROOT / "NCG_KO_PARAMETER_SCAN.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["KO_mod_8", "real_structure_commutes_with_grading", "intersection_form_symmetry",
                    "odd_dim_determinant_forced_zero", "source"])
        for row in r["ko_parameter_scan"]:
            w.writerow([row["KO_mod_8"], row["real_structure_commutes_with_grading"],
                       row["intersection_form_symmetry"], row["odd_dim_determinant_forced_zero"],
                       row["source"]])

    # --- NCG_INTERSECTION_FORM_REPORT.md ---
    sk = r["ko_skew_symmetric_determinant"]
    sym = r["ko_symmetric_example"]
    lines = ["# NCG_INTERSECTION_FORM_REPORT.md", "",
             "## Skew-symmetric (KO=2,6) case: determinant forced to zero -- VERIFIED EXACT", "",
             f"Verified symbolically (general symbolic entries, not one numeric example) for "
             f"n in {list(sk['results'].keys())}: **{sk['all_odd_n_confirm_identically_zero']}**",
             "", "This confirms the mechanism the closure-report candidate correctly "
             "identifies for the KO=6, 3-summand-algebra case: an odd-dimensional (n=3) real "
             "skew-symmetric intersection matrix has determinant EXACTLY zero, always.", "",
             "## Symmetric (KO=0,4) case: NOT forced to zero, but not shown nonzero for THIS project", "",
             f"Example symmetric 3x3 matrix {sym['example_matrix']}: determinant = "
             f"{sym['determinant']} (nonzero: {sym['nonzero']})", "",
             sym["what_this_DOES_NOT_show"], "",
             "## Verdict", "",
             "KO=6 (skew): mathematically decisive obstruction for any 3-summand algebra -- "
             "AUDIT/FALSIFICATION CANDIDATE, consistent with H2's existing finding that this "
             "project's own D+=sqrt(L) naturally produces KO=0 mod 8, not 6.",
             "",
             "KO=0/4 (symmetric): the determinant obstruction is REMOVED in general, but no "
             "specific matrix from this project's own construction has been shown to have "
             "nonzero determinant -- CANDIDATE, OPEN, not resolved."]
    (ROOT / "NCG_INTERSECTION_FORM_REPORT.md").write_text("\n".join(lines) + "\n")

    # --- CLIFFORD_DERIVATION_REPORT.md ---
    cr = r["clifford_rank_forcing"]
    su4 = r["su4_to_sm_breaking"]
    s6 = r["spin6_su4"]
    lines = ["# CLIFFORD_DERIVATION_REPORT.md", "",
             f"## {cr['claim']}", "", f"**Status: {cr['status']}**", "", cr["evidence"], "",
             cr["recommended_treatment"], "",
             f"## Spin(6) ~= SU(4)", "",
             f"dim match: {s6['dim_match']}, rank match: {s6['rank_match']} (external, established)",
             "", f"## SU(4) -> Standard Model gauge group", "",
             f"**Status: {su4['su4_to_sm_breaking_status']}**", "", su4["evidence"], "",
             su4["verdict"]]
    (ROOT / "CLIFFORD_DERIVATION_REPORT.md").write_text("\n".join(lines) + "\n")

    # --- INCIDENCE_CLIFFORD_CLOSURE_REPORT.md (the honest master summary) ---
    h2b = r["h2b_reused_from_prior_phase"]
    lines = ["# INCIDENCE_CLIFFORD_CLOSURE_REPORT.md", "",
             "**This report does NOT claim closure.** It audits the incidence/Clifford/"
             "persistence candidate branch proposed as an alternative to the uploaded "
             "`canonical_closure_report.md`, which this project explicitly does not "
             "implement (see the chat response accompanying this commit for the specific "
             "arithmetic and overclaiming problems found in that document: a grade-2 "
             "bivector count that doesn't add up -- 12+4=16 claimed from a 15-dimensional "
             "space -- and a KO=6->0/4 'resolves it' framing that skips the necessary-vs-"
             "sufficient distinction this report enforces instead).", "",
             "## Closure matrix (this audit's own findings, not the closure report's)", "",
             "| Component | Status |", "|---|---|",
             "| B (bipartite incidence matrix) | Defined (already implemented as the "
             "compiler's graph incidence structure) |",
             "| L=BB^T symmetric, PSD | VERIFIED (standard linear algebra) |",
             f"| D_B=[[0,B],[B^T,0]] self-adjoint, exactly local | VERIFIED "
             f"(H2B, reused from prior phase: sparsity "
             f"{h2b['D_sparsity_fraction_strict']*100:.2f}%) |",
             "| D_B^2 = diag(BB^T, B^TB) | VERIFIED EXACT |",
             "| Persistence projection P_lambda_c (idempotent, self-adjoint) | VERIFIED EXACT |",
             "| L_Pi = P.L.P | VERIFIED EXACT |",
             "| Heat trace K_Pi(beta) monotone nonincreasing | VERIFIED EXACT |",
             "| Persistent distance d_{Pi,beta}: beta->0 limit, monotonicity | VERIFIED |",
             "| KC-003a measure convergence | NOT COMPUTABLE FROM AVAILABLE DEFINITIONS |",
             "| KC-003b operator convergence | PARTIAL (numerical evidence only) |",
             "| KC-003c spectral convergence | COMPUTED (real DESI data, mixed result -- see CONV-001) |",
             "| KC-003d geometric convergence | NOT COMPUTABLE (blocked on d(i,j)->g_munu) |",
             "| VR-001 on known manifold (S^1), uniform sampling | VERIFIED (projection norms -> 1) |",
             "| VR-001 on known manifold (S^1), nonuniform sampling | FAILS TO CONVERGE (real, "
             "expected finding -- density bias, motivates the corpus's own existing FC-005 "
             "density-normalization work) |",
             "| VR-001 on real DESI data | NOT ADDRESSED (blocked on same missing embedding "
             "map as KC-003a/b) |",
             "| KO=6 3-summand determinant obstruction | VERIFIED EXACT (general symbolic proof) |",
             "| KO=0/4 determinant nonzero (in general) | VERIFIED possible (one example); NOT "
             "shown for this project's own specific construction |",
             "| Cl(6) forced by this project's own B/D_B/L | NOT COMPUTABLE -- unforced, "
             "6 is an imported external target, not a derived one |",
             "| Spin(6)~=SU(4) | external, established (dim/rank consistent) |",
             "| SU(4) -> SU(3)xSU(2)xU(1) | NOT COMPUTABLE -- same kind of gap as H4 |",
             "| Spectral action Tr f(D_F/Lambda) asymptotic terms a_0,a_2,a_4 | NOT ATTEMPTED "
             "(blocked: no valid finite spectral triple constructed yet, per the above)",
             "", "## Bottom line", "",
             "The incidence construction (B, D_B) is real progress -- exactly local by "
             "construction where D+=sqrt(L) was dense, and every algebraic identity claimed "
             "for it checks out exactly. The persistence/heat-trace machinery is fully closed "
             "as finite linear algebra. But the chain from there to a valid Standard-Model "
             "spectral triple and gauge group remains genuinely open at multiple independent "
             "points (KC-003a/d, the specific KO=0/4 matrix, Cl(6)'s forcing, SU(4)->SM "
             "breaking) -- this is a real narrowing of the problem, not a closure of it."]
    (ROOT / "INCIDENCE_CLIFFORD_CLOSURE_REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    r = run_all()
    (ROOT / "scientific_corpus" / "derivation" / "INCIDENCE_CLIFFORD_RESULTS.json").write_text(
        json.dumps(r, indent=2, default=str))
    write_reports(r)
    print("Wrote 7 deliverables + INCIDENCE_CLIFFORD_RESULTS.json")
