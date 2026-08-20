"""Gauge branch as executable `.seit` primitives (Phase 11): exposes
the existing gauge-symmetry derivations, building on -- not modifying
-- scientific_corpus/derivation/gauge_rank.py. Per the brief's explicit
instruction: do NOT insert SU(3)xSU(2)xU(1) as a TARGET CONDITION;
record the actual derivation path only.

su3_in_g2_check(), su2xu1_in_spin8_check(), and h4c_missing_link_report()
are exposed unchanged -- they already record real, standard external
Lie-theory facts (SU(3) subset G2) and honest necessary-not-sufficient
rank/dimension checks (SU(2)xU(1) inside Spin(8)), never claiming full
embedding construction, and gauge_rank.py's own H4C finding is already
explicit that no rule exists anywhere in the corpus for which graph
construction is supposed to represent "the physical vacuum state."

WHAT THIS PHASE ADDS, AND WHY IT IS NOT TARGET-CONDITIONING:
gauge_rank.py's own missing_link_to_compiler_spectrum() (H4C) states
that once a graph is specified, checking its eigenvalue-multiplicity
pattern against SEIT-7's required (3,2,1) degeneracy "IS directly
computable with the compiler's existing eigh()-based spectral backend
... not a conceptual obstacle." This module builds exactly that
MEASUREMENT tool: eigenvalue_multiplicity_pattern() reports the actual
multiplicities of a GIVEN graph's Laplacian spectrum (via the real
compiler.backends.spectral.spectrum backend), and
h4c_pattern_match_report() compares that observed pattern against
(3,2,1). Neither function chooses, searches over, or biases toward any
particular graph -- the caller supplies an independently-constructed L
(e.g. via seit_lang.primitives.build_graph, chosen for its own
graph-theoretic properties), and the report is explicit that a match
would not establish SEIT-7 (no rule exists for which graph is the
"right" one) and a non-match would not falsify it either (no specific
graph has been asserted as required). Building a function that instead
SEARCHED over graphs for one producing (3,2,1) would be exactly the
"insert SU(3)xSU(2)xU(1) as a target condition" the brief forbids --
this module deliberately does not do that.
"""
from __future__ import annotations

import numpy as np

from compiler.backends import spectral
from scientific_corpus.derivation import gauge_rank

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def su3_in_g2_check() -> dict:
    return gauge_rank.su3_in_g2_check()


def su2xu1_in_spin8_check() -> dict:
    return gauge_rank.su2xu1_in_spin8_check()


def h4c_missing_link_report() -> dict:
    return gauge_rank.missing_link_to_compiler_spectrum()


def eigenvalue_multiplicity_pattern(L: np.ndarray, n_lowest: float = 6, tol: float = 1e-6) -> list[int]:
    """Multiplicities of the lowest n_lowest DISTINCT eigenvalues of L
    (via the real compiler.backends.spectral.spectrum backend), in
    ascending-eigenvalue order. A pure measurement of whatever graph is
    passed in -- see module docstring."""
    n_lowest_i, tol_f = int(n_lowest), float(tol)
    spec = spectral.spectrum(L)
    vals = np.sort(spec.eigenvalues)
    groups: list[int] = []
    i = 0
    while i < len(vals) and len(groups) < n_lowest_i:
        count = 1
        while i + count < len(vals) and abs(vals[i + count] - vals[i]) < tol_f:
            count += 1
        groups.append(count)
        i += count
    return groups


def h4c_pattern_match_report(L: np.ndarray) -> dict:
    pattern = eigenvalue_multiplicity_pattern(L, n_lowest=3)
    required = [3, 2, 1]
    matches = pattern == required
    return {
        "claim_id": "H4C",
        "observed_multiplicity_pattern_lowest_3": pattern,
        "required_pattern_per_SEIT_7": required,
        "matches": matches,
        "caveat": (
            "This checks whether a GIVEN, independently-constructed graph's spectrum "
            "happens to exhibit the (3,2,1) pattern -- it does not search for, select, "
            "or bias toward a graph that would (that would be exactly the "
            "target-conditioning this module's docstring says Phase 11 forbids). Per "
            "gauge_rank.missing_link_to_compiler_spectrum()'s own finding, no rule "
            "exists anywhere in the corpus for WHICH graph is supposed to represent "
            "'the physical vacuum state', so a match here would not by itself "
            "establish SEIT-7, and a non-match would not falsify it -- no specific "
            "graph has been asserted as the required one."),
    }


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("su3_in_g2_check", [], "Dataset",
                      su3_in_g2_check,
                      "seit_lang.gauge_branch.su3_in_g2_check (calls "
                      "scientific_corpus.derivation.gauge_rank.su3_in_g2_check)"),
    PrimitiveBinding("su2xu1_in_spin8_check", [], "Dataset",
                      su2xu1_in_spin8_check,
                      "seit_lang.gauge_branch.su2xu1_in_spin8_check (calls "
                      "scientific_corpus.derivation.gauge_rank.su2xu1_in_spin8_check)"),
    PrimitiveBinding("h4c_missing_link_report", [], "Dataset",
                      h4c_missing_link_report,
                      "seit_lang.gauge_branch.h4c_missing_link_report (calls "
                      "scientific_corpus.derivation.gauge_rank.missing_link_to_compiler_spectrum)"),
    PrimitiveBinding("eigenvalue_multiplicity_pattern", ["Matrix", "Scalar"], "Dataset",
                      lambda L, n_lowest: eigenvalue_multiplicity_pattern(L, n_lowest),
                      "seit_lang.gauge_branch.eigenvalue_multiplicity_pattern"),
    PrimitiveBinding("h4c_pattern_match_report", ["Matrix"], "Dataset",
                      h4c_pattern_match_report,
                      "seit_lang.gauge_branch.h4c_pattern_match_report"),
]

GAUGE_BRANCH_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
GAUGE_BRANCH_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
