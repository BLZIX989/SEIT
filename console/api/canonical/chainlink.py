"""Master chainlink view (brief section XXIV).

Renders the REAL compiler/ir/forward_chain.py TEMPLATE_CHAIN -- this
module does not define a second, separate chain. The classic notation
(Δ→Γ→G→L→Spec(L)→g_μν→∇→R→G_μν→S→δS=0) from the brief is provided as a
display-only relabeling of the real node ids, via CONCEPTUAL_SYMBOLS
below, and is never used for any lookup, matching, or status logic.

Import compiler.ir.forward_chain directly (read-only: TEMPLATE_CHAIN
and TEMPLATE_EDGES are module-level constants, not a function that
writes anything) so that if that module's chain is ever edited, this
view updates automatically rather than silently drifting out of sync
with a hand-copied list.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from compiler.ir.forward_chain import (  # noqa: E402
    SELECTION_NODE_ID, TEMPLATE_CHAIN, TEMPLATE_EDGES,
)

# Display-only labels. Not looked up anywhere except by this dict.
# Several TEMPLATE_CHAIN nodes have no single classical-notation
# counterpart (e.g. CONSTRAINT, PERSISTENCE-NODE) -- those get an
# honest descriptive label instead of a fabricated symbol.
CONCEPTUAL_SYMBOLS: dict[str, str] = {
    "FOUNDATION": "F0",
    "EMPTYSET": "∅",
    "MATH-UNIVERSE": "M",
    "PHYSICAL-CANDIDATE-SET": "P",
    SELECTION_NODE_ID: "Σ",
    "VACUUM": "Ω₀",
    "DISTINCTION": "Δ",
    "RELATION": "R(Ωᵢ,Ωⱼ)",
    "TRANSFORMATION-NODE": "Γ",
    "CONSTRAINT": "C",
    "PERSISTENCE-NODE": "Π",
    "OPERATOR-NODE": "L",
    "SPECTRUM-NODE": "Spec(L)",
    "GEOMETRY-NODE": "g_μν, ∇, R, G_μν",
    "VARIATIONAL-NODE": "S, δS=0",
    "QUANTUM-NODE": "Ĥ, |ψ⟩",
    "GAUGE-NODE": "A_μ, F_μν",
    "MATTER-NODE": "ψ (fermions)",
    "THERMODYNAMICS-NODE": "U, S, Z",
    "COSMOLOGY-NODE": "Λ, H, a(t)",
    "OBSERVABLES-NODE": "(validation only)",
}

# Which TEMPLATE_CHAIN ids currently have a real, executed backend
# behind the arrow INTO them, vs. remain purely a dependency template
# entry (brief section XIII: never imply a stage ran when it did not).
# This list is deliberately conservative -- OPERATOR-NODE/SPECTRUM-NODE
# are conceptually close to the executed GRAPH-G-SEED branch
# (compiler/ir/executable_tests.py), but forward_chain.py's own module
# docstring is explicit that the two branches are NOT the same chain
# and must not be conflated (compiler_architecture.md, "Why two
# separate node families exist"). So EXECUTED is reserved for nodes
# that are themselves directly wired to an executed backend, and every
# TEMPLATE_CHAIN node is NOT_IMPLEMENTED unless proven otherwise.
EXECUTED_TEMPLATE_NODE_IDS: set[str] = set()  # empty: verified against forward_chain.py + executable_tests.py


def build_chainlink_view(nodes: dict[str, dict]) -> list[dict[str, Any]]:
    # child -> [parents] as declared in TEMPLATE_EDGES ("child, parent")
    edge_map: dict[str, list[str]] = {}
    for child, parent in TEMPLATE_EDGES:
        edge_map.setdefault(child, []).append(parent)

    ordered_ids = [nid for nid, _ in TEMPLATE_CHAIN]
    arrows: list[dict[str, Any]] = []

    for i in range(1, len(ordered_ids)):
        from_id = ordered_ids[i - 1]
        to_id = ordered_ids[i]
        # only emit an arrow if the template actually declares this edge
        # (TEMPLATE_EDGES is the source of truth, not positional adjacency)
        declared_parents = edge_map.get(to_id, [])
        if from_id not in declared_parents:
            continue
        to_node = nodes.get(to_id, {})
        arrows.append({
            "from_id": from_id,
            "to_id": to_id,
            "from_symbol": CONCEPTUAL_SYMBOLS.get(from_id, from_id),
            "to_symbol": CONCEPTUAL_SYMBOLS.get(to_id, to_id),
            "status": to_node.get("status", "UNKNOWN"),
            "der_id": None,  # NOT_IMPLEMENTED upstream: no DER-id concept in this compiler
            "proof": [],     # populated by the caller via find_proofs_for_node if desired
            "dependencies": to_node.get("dependencies", declared_parents),
            "assumptions": to_node.get("assumptions", []),
            "calculations": [],
            "execution_status": "EXECUTED" if to_id in EXECUTED_TEMPLATE_NODE_IDS else "NOT_IMPLEMENTED",
        })

    # SELECTION-SIGMA is a Transformation gating PHYSICAL-CANDIDATE-SET,
    # not a positional element of TEMPLATE_CHAIN -- surface it as its own
    # arrow rather than silently folding it into MATH-UNIVERSE -> PHYSICAL-CANDIDATE-SET.
    sigma = nodes.get(SELECTION_NODE_ID, {})
    arrows.insert(3, {
        "from_id": "MATH-UNIVERSE",
        "to_id": SELECTION_NODE_ID,
        "from_symbol": CONCEPTUAL_SYMBOLS["MATH-UNIVERSE"],
        "to_symbol": CONCEPTUAL_SYMBOLS[SELECTION_NODE_ID],
        "status": sigma.get("status", "UNKNOWN"),
        "der_id": None,
        "proof": [],
        "dependencies": sigma.get("dependencies", []),
        "assumptions": sigma.get("assumptions", []),
        "calculations": [],
        "execution_status": "NOT_IMPLEMENTED",
    })
    return arrows
