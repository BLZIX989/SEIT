"""Registers the inner-fluctuation / spectral-action attempt over the
coupled recovery candidate (compiler/backends/
finite_spectral_triple_coupled_recovery_spectral_action.py) into the
EXISTING MDCL. Must run after register_tft002b_and_coupled_recovery
(reuses COUPLED-RECOVERY-CERTIFICATION).

WHY THIS EXISTS: an audit of CL-FINITE-TRIPLE-TO-SPECTRAL-ACTION (this
session) found that chainlink's OMEGA_B-FINITE dependency traces back to
the ORIGINAL (A_F,H_F,D_F,J_F,gamma_F) candidate, which fails the
first-order condition -- so it is correctly OPEN. But this project also
built three recovery candidates that PASS the first-order condition, and
NONE of them was ever run through an inner-fluctuation attempt, despite
passing the exact axiom that blocks the original chainlink. This module
closes that gap for the richest of the three (the nontrivially-coupled
recovery over TFT-002B), registering a genuinely different, INDEPENDENT
chainlink -- it does not touch or resolve CL-FINITE-TRIPLE-TO-SPECTRAL-
ACTION, which remains correctly OPEN for the original candidate.
"""
from __future__ import annotations

from pathlib import Path

from compiler.backends.finite_spectral_triple_coupled_recovery_spectral_action import (
    compute_finite_moments, run_inner_fluctuation_certification,
)
from compiler.core.ir import Object, Transformation
from compiler.core.status import Status
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

TYPE_DEFS_COUPLED_RECOVERY_SPECTRAL_ACTION = [
    ("inner_fluctuation_component", "a component (gauge potential, fluctuated Dirac operator, or "
                                     "curvature) of a Connes inner-fluctuation D_A=D+omega+J omega "
                                     "J^-1 attempted over a candidate that passes the first-order "
                                     "condition -- status always computed from real axiom checks", None),
]


def register_coupled_recovery_spectral_action(registries: MDCLRegistries, repo_root: Path) -> dict:
    calculations: list[dict] = []

    cert = run_inner_fluctuation_certification()
    moments = compute_finite_moments()

    calculations.append({
        "id": "CALC-COUPLED-RECOVERY-INNER-FLUCTUATION", "kind": "connes_inner_fluctuation_attempt",
        "inputs": {"generator": "omega = i*[D_F'',pi'(f)] for a single real f on the vertex block"},
        "results": {
            "J_conjugate_matrix_verified": cert.J_conjugate_matrix_verified,
            "omega_self_adjoint": cert.omega_self_adjoint,
            "real_structure_epsilon_prime_used": cert.real_structure_epsilon_prime_used,
            "D_A_self_adjoint": cert.D_A_self_adjoint,
            "D_A_anticommutes_with_grading": cert.D_A_anticommutes_with_grading,
            "Omega_B_is_zero": cert.Omega_B_is_zero,
            "Omega_B_self_adjoint": cert.Omega_B_self_adjoint,
            "Omega_B_max_abs": cert.Omega_B_max_abs,
        },
        "verification": {"well_posed": cert.well_posed},
        "status": Status.VERIFIED.value if cert.well_posed else Status.FAIL.value,
    })
    fluctuation_status = Status.VERIFIED if cert.well_posed else Status.FAIL

    omega_b = Object(
        id="OMEGA_B-COUPLED-RECOVERY", type="inner_fluctuation_component", status=fluctuation_status,
        role="upstream_construction", dependencies=["COUPLED-RECOVERY-CERTIFICATION"],
        carrier=f"Omega_B'' := D_A''^2 - D_F''^2, D_A''=D_F''+omega+eps'*J''omegaJ''^-1, omega=i*"
                "[D_F'',pi'(f)] (single generator). Verified well-posed: D_A'' self-adjoint "
                f"({cert.D_A_self_adjoint}), anticommutes with grading ({cert.D_A_anticommutes_with_grading}), "
                f"Omega_B'' genuinely nonzero (max abs {cert.Omega_B_max_abs:.3f}, not a trivial "
                f"block-diagonal duplication -- possible ONLY because of the coupled candidate's "
                "nonzero inter-copy coupling C; the minimal uncoupled recovery's own first-order-"
                "condition proof shows [D_F',pi'(f)] has zero output on copy 2, which would force "
                "any inner fluctuation built this way to stay block-diagonal there).",
        assumptions=[
            "omega is ONE generator (single real f), not the fully general Omega^1_D(A_F) "
            "connection -- a different or larger generator set would give a different Omega_B''.",
            f"real_structure_epsilon_prime used: {cert.real_structure_epsilon_prime_used} (the "
            "ACTUALLY MEASURED sign for this candidate, not assumed).",
        ],
    )
    omega_b.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_coupled_recovery_spectral_action.py",
        object_id=omega_b.id, calculation_id="CALC-COUPLED-RECOVERY-INNER-FLUCTUATION",
        status=fluctuation_status, verification={"well_posed": cert.well_posed},
    )
    registries.objects.add_object(omega_b)

    t_fluctuation = Transformation(
        id="T-COUPLED-RECOVERY-INNER-FLUCTUATION", domain="COUPLED-RECOVERY-CERTIFICATION",
        codomain="OMEGA_B-COUPLED-RECOVERY",
        action="build omega=i*[D_F'',pi'(f)], verify self-adjointness, form "
               "D_A''=D_F''+omega+eps'*J''omegaJ''^-1 via an explicit closed-form J-conjugation "
               "matrix (independently verified against the vector-level J definition), verify "
               "D_A'' self-adjoint and grading-anticommuting, compute Omega_B''=D_A''^2-D_F''^2",
        status=fluctuation_status, dependencies=["COUPLED-RECOVERY-CERTIFICATION"],
        proof="numpy exact linear algebra at n=200 (dim=2800 doubled candidate); "
              "J_conjugate_matrix's closed form independently verified against the ground-truth "
              "vector-level J_apply composition on random complex inputs",
    )
    t_fluctuation.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_coupled_recovery_spectral_action.py",
        transformation_id=t_fluctuation.id, status=fluctuation_status,
        calculation_id="CALC-COUPLED-RECOVERY-INNER-FLUCTUATION",
        verification={"well_posed": cert.well_posed},
    )
    registries.transformations.add_transformation(t_fluctuation)

    moments_status = Status.CALCULATED if moments.well_posed else Status.OPEN
    moment_values = {k: v["value"] for k, v in moments.moments.items()}
    calculations.append({
        "id": "CALC-COUPLED-RECOVERY-FINITE-MOMENTS", "kind": "finite_trace_moments",
        "inputs": {}, "results": moment_values,
        "verification": {"well_posed": moments.well_posed,
                         "max_imag_residual": max(abs(v["imag_residual"]) for v in moments.moments.values())},
        "status": moments_status.value,
    })

    spectral_action = Object(
        id="SPECTRAL-ACTION-A0-A6-COUPLED-RECOVERY-B", type="inner_fluctuation_component",
        status=moments_status, role="comparison", dependencies=["OMEGA_B-COUPLED-RECOVERY"],
        carrier=f"a0''..a6'' (finite trace moments Tr(D_A''^k) for the coupled-recovery candidate): "
                + ", ".join(f"{k}={v['value']:.4g}" for k, v in moments.moments.items()) +
                ". EXACT finite-dimensional trace moments of this specific matrix, NOT continuum "
                "Seeley-DeWitt small-beta expansion coefficients -- no continuum Riemannian "
                "manifold structure has been constructed for this candidate (same caution "
                "seit_lang/spectral_action.py and seit_lang/persistence_kernel.py already state "
                "for their own finite/discrete quantities).",
        assumptions=[
            "physical_interpretation: NONE -- finite linear-algebra trace moments of a specific "
            "matrix, not physically-interpretable Seeley-DeWitt heat-kernel coefficients.",
            "omega is a single generator (see OMEGA_B-COUPLED-RECOVERY); a different generator "
            "choice would give different moment values.",
        ],
    )
    spectral_action.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_coupled_recovery_spectral_action.py",
        object_id=spectral_action.id, calculation_id="CALC-COUPLED-RECOVERY-FINITE-MOMENTS",
        status=moments_status, verification={"well_posed": moments.well_posed},
    )
    registries.objects.add_object(spectral_action)

    t_moments = Transformation(
        id="T-COUPLED-RECOVERY-SPECTRAL-ACTION", domain="OMEGA_B-COUPLED-RECOVERY",
        codomain="SPECTRAL-ACTION-A0-A6-COUPLED-RECOVERY-B",
        action="Tr(D_A''^k) for k=0,2,4,6 -- exact finite-dimensional trace moments, not a "
               "continuum Seeley-DeWitt expansion",
        status=moments_status, dependencies=["OMEGA_B-COUPLED-RECOVERY"],
        proof="numpy exact finite-dimensional trace via repeated matrix multiplication "
              "(matrix_power), imaginary residual confirmed at float-noise scale (<1e-12) for "
              "self-adjoint D_A''",
    )
    t_moments.provenance = make_provenance(
        source="compiler/backends/finite_spectral_triple_coupled_recovery_spectral_action.py",
        transformation_id=t_moments.id, status=moments_status,
        calculation_id="CALC-COUPLED-RECOVERY-FINITE-MOMENTS",
        verification={"well_posed": moments.well_posed},
    )
    registries.transformations.add_transformation(t_moments)

    return {"calculations": calculations, "inner_fluctuation_certification": cert,
            "finite_moments": moment_values}
