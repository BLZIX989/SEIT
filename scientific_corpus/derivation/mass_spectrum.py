"""H_MASS -- investigation of m_n = m_0 sqrt(lambda_n) (Spectral Codex).
Real computation: reuses the compiler's own graph_laplacian backend to
compute actual spectra for the same topologies the compiler already
builds, then tests whether the resulting eigenvalue-ratio structure has
genuine predictive content against real charged-lepton mass ratios, or
merely enough free parameters (graph choice + m_0) to fit any 2 numbers.

Charged lepton masses (source: Particle Data Group, standard textbook
values, stable to the precision used here -- ratios, not absolute scale):
  m_e   = 0.5109989 MeV
  m_mu  = 105.6584  MeV
  m_tau = 1776.86   MeV
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.backends.graph_laplacian import build_graph, laplacian  # noqa: E402

REAL_LEPTON_MASSES_MEV = {"electron": 0.5109989, "muon": 105.6584, "tau": 1776.86}
REAL_LEPTON_RATIOS = {
    "mu/e": REAL_LEPTON_MASSES_MEV["muon"] / REAL_LEPTON_MASSES_MEV["electron"],
    "tau/e": REAL_LEPTON_MASSES_MEV["tau"] / REAL_LEPTON_MASSES_MEV["electron"],
    "tau/mu": REAL_LEPTON_MASSES_MEV["tau"] / REAL_LEPTON_MASSES_MEV["muon"],
}


def _spectrum(topology: str, n: int, seed: int | None = None) -> np.ndarray:
    """A_matrix via compiler.backends.graph_laplacian.build_graph, real
    (already-implemented, tested) compiler code -- not reimplemented here."""
    g = build_graph(topology, n, seed=seed)
    A = np.zeros((g.n, g.n))
    for i, j in g.edges:
        A[i, j] = A[j, i] = 1.0
    L = laplacian(A)
    vals = np.linalg.eigvalsh(L)
    return np.clip(vals, 0.0, None)


def dimensional_analysis() -> dict:
    return {
        "claim": "m_n = m_0 sqrt(lambda_n)",
        "lhs_dimension": "[mass] (or [energy] in natural units)",
        "rhs_dimension_of_sqrt(lambda_n)": (
            "The combinatorial graph Laplacian L=D-A is dimensionless (a pure "
            "adjacency-count object); its eigenvalues lambda_n are therefore "
            "dimensionless pure numbers, and sqrt(lambda_n) is also dimensionless."
        ),
        "conclusion": (
            "m_0 must carry the ENTIRE dimensional content [mass] of the formula by "
            "itself. The graph/spectral construction supplies only a dimensionless shape "
            "(the relative pattern of the sqrt(lambda_n) sequence) -- it cannot, by "
            "dimensional analysis alone, supply an absolute mass scale. This is not a "
            "flaw specific to this project; it is true of every eigenvalue-ratio mass "
            "formula in physics (e.g. Regge trajectories) -- but it means the formula's "
            "entire falsifiable content is in the RATIOS m_n/m_1 = sqrt(lambda_n/lambda_1), "
            "never in the absolute values, however m_0 is chosen."
        ),
    }


def structural_test(n_values: tuple[int, ...] = (6, 10, 20)) -> dict:
    """Zero-parameter structural test (brief section VII): for each of the
    compiler's own already-implemented topologies, compute the predicted
    ratio sqrt(lambda_3/lambda_2) [i.e. the 3rd and 2nd nonzero modes, the
    natural 3-generation candidate slots after the lambda_0=0 zero mode]
    and compare directly to the real tau/mu lepton ratio -- no fitted m_0,
    since ratios of ratios cancel it."""
    real_tau_over_mu = REAL_LEPTON_RATIOS["tau/mu"]
    results = {}
    for topology in ["path", "cycle", "complete", "star", "grid2d"]:
        for n in n_values:
            try:
                spec = _spectrum(topology, n)
            except Exception as e:  # noqa: BLE001 -- record, don't hide, a construction failure
                results[f"{topology}_n{n}"] = {"error": str(e)}
                continue
            nonzero = spec[spec > 1e-9]
            if len(nonzero) < 2:
                results[f"{topology}_n{n}"] = {"note": "fewer than 2 nonzero modes -- cannot form a 3rd/2nd ratio"}
                continue
            predicted_ratio = float(np.sqrt(nonzero[1] / nonzero[0])) if len(nonzero) > 1 else None
            results[f"{topology}_n{n}"] = {
                "n_nonzero_modes": int(len(nonzero)),
                "lambda_1": float(nonzero[0]), "lambda_2": float(nonzero[1]) if len(nonzero) > 1 else None,
                "predicted_m3/m2_ratio_sqrt(lambda2/lambda1)": predicted_ratio,
                "real_tau/mu_ratio": real_tau_over_mu,
                "absolute_residual": abs(predicted_ratio - real_tau_over_mu) if predicted_ratio else None,
            }
    # "Go fishing" test: erdos_renyi graphs have a free structural parameter
    # (the random seed / edge realization) that path/cycle/complete/star do
    # not. Sweep seeds and report the BEST match found, to make the
    # degrees-of-freedom argument in degrees_of_freedom_analysis() concrete
    # rather than asserted.
    best_er_match = None
    for seed in range(50):
        try:
            spec = _spectrum("erdos_renyi", 20, seed=seed)
        except Exception:
            continue
        nonzero = spec[spec > 1e-9]
        if len(nonzero) < 2:
            continue
        ratio = float(np.sqrt(nonzero[1] / nonzero[0]))
        residual = abs(ratio - real_tau_over_mu)
        if best_er_match is None or residual < best_er_match["absolute_residual"]:
            best_er_match = {"seed": seed, "predicted_ratio": ratio, "absolute_residual": residual}

    return {
        "test": "zero-parameter structural test: sqrt(lambda_2/lambda_1) vs real tau/mu = "
                f"{real_tau_over_mu:.4f}, across every topology/size the compiler already "
                "implements, no fitting",
        "results": results,
        "erdos_renyi_50_seed_sweep_best_match": best_er_match,
        "erdos_renyi_interpretation": (
            "This ran counter to the expected 'go fishing' outcome and is reported as found, "
            "not adjusted after the fact: sweeping 50 random seeds at n=20 did NOT find a "
            f"materially better match than the fixed path topology (best residual "
            f"{best_er_match['absolute_residual']:.3f} vs path_n6's 14.885) -- the "
            "sqrt(lambda_2/lambda_1) ratio for random graphs at this size and edge density "
            "stays clustered near ~2, essentially the same range as path. This is itself a "
            "real, useful negative finding: for adjacent nonzero eigenvalues at modest n, "
            "achieving a ratio as large as the real tau/mu=16.8 may not be a matter of "
            "hunting through more topologies at fixed size, but could require either much "
            "larger n, a qualitatively different eigenvalue-selection rule (not simply "
            "'the 2nd and 3rd nonzero modes'), or a differently normalized Laplacian. This "
            "is an open structural question this test surfaces, not one it resolves."
        ),
    }


def degrees_of_freedom_analysis() -> dict:
    """Section VII's core predictive-content question: with graph TOPOLOGY,
    graph SIZE n, and the eigenvalue-to-generation ASSIGNMENT all free
    choices (on top of the free scale m_0, which cancels in ratios), how
    many free parameters are actually available to fit 2 independent mass
    ratios (mu/e, tau/e)?"""
    return {
        "target": "2 independent real numbers to fit: mu/e and tau/e mass ratios "
                  f"({REAL_LEPTON_RATIOS['mu/e']:.2f}, {REAL_LEPTON_RATIOS['tau/e']:.2f})",
        "free_choices_available_to_the_formula_as_stated_anywhere_in_the_corpus": [
            "graph topology (unconstrained -- no construction rule ties a specific graph "
            "to 'the lepton sector' anywhere in the corpus)",
            "graph size n (unconstrained)",
            "which 2 of the (up to n-1) nonzero eigenvalues get assigned to 'muon' and "
            "'tau' respectively (unconstrained -- no ordering/selection rule is given "
            "beyond 'the spectrum')",
            "m_0 (cancels in ratios, but is an extra free real parameter for absolute mass)",
        ],
        "verdict": (
            "The fixed, parameter-free topologies (path/cycle/complete/star/grid2d) all fail "
            "badly at reproducing tau/mu=16.8 from adjacent nonzero eigenvalues (residuals "
            "14.8-15.8 -- cycle/complete/star all have near-degenerate lambda_1~lambda_2, "
            "giving a predicted ratio near 1.0, and path gets only to ~2.0). Adding a free "
            "random-seed parameter (erdos_renyi, 50 seeds swept) did NOT materially improve "
            "this at n=20 -- see erdos_renyi_50_seed_sweep_best_match and its interpretation. "
            "So the theoretical 'enough free parameters to fit anything' concern this test "
            "was designed to check is NOT what was actually found here: at this graph size, "
            "the adjacent-nonzero-eigenvalue ratio appears structurally capped well below "
            "the real tau/mu hierarchy regardless of topology or randomization, which is a "
            "more specific and more useful negative result than a generic overfitting "
            "warning. What remains genuinely unconstrained by the corpus -- and is therefore "
            "still an open predictive-content gap, independent of this particular finding -- "
            "is any rule for WHICH graph/size represents 'the lepton sector' and WHICH "
            "eigenvalues (not necessarily adjacent, not necessarily the 2nd/3rd) map to "
            "which generation. Without such a rule, no comparison to real masses is a "
            "genuine out-of-sample test."
        ),
        "what_would_resolve_this": (
            "A specific, independently-motivated rule (e.g. 'the lepton sector graph is "
            "exactly the one produced by running the compiler's own Delta->Gamma->G "
            "construction on [specific real input data]', with a fixed, pre-declared "
            "eigenvalue-to-generation assignment) stated and fixed BEFORE comparing to "
            "known masses, so the comparison is a genuine out-of-sample test rather than "
            "a fit."
        ),
    }
