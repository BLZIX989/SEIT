"""Pydantic response models for the UOC Research Console API.

Every model here mirrors a real compiler schema field-for-field rather
than inventing a new one (per UOC_RESEARCH_CONSOLE_ARCHITECTURE.md
section 4.1) — the intent is that these models are load-bearing
documentation of `compiler/core/ir.py`'s dataclasses and the on-disk
registry shapes, not an independent design.

These are all read models. Nothing in this module, or anywhere in
Phase 2, accepts a payload that could mutate canonical state — Phase 2
is read-only by design (see console/api/main.py's route list).
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ProvenanceModel(BaseModel):
    """Mirrors compiler/core/ir.py::Provenance field-for-field."""
    source: str = ""
    source_version: str = ""
    object_id: str = ""
    equation_id: str = ""
    dependency_ids: list[str] = []
    transformation_id: str = ""
    calculation_id: str = ""
    execution_timestamp: str = ""
    git_commit: str = ""
    code_version: str = ""
    numerical_environment: dict[str, str] = {}
    status: str = "OPEN"
    verification: dict[str, Any] = {}


class NodeSummary(BaseModel):
    """One row of the flattened node list (`GET /api/nodes`).

    `kind` is one of "Object" | "Transformation" | "Equation", exactly
    as compiler/ir/registry.py::MDCLRegistries.status_matrix() emits it.
    """
    id: str
    kind: str
    status: str
    role: str
    dependencies: list[str] = []
    type: Optional[str] = None       # Object only
    domain: Optional[str] = None     # Transformation/Equation
    codomain: Optional[str] = None   # Transformation only


class NodeDetail(BaseModel):
    """Full detail panel for one node (brief section VII).

    Every field here is either a verbatim registry value or an explicit
    cross-reference lookup — never a synthesized/inferred value. Where a
    cross-reference is a best-effort text match rather than a guaranteed
    id link (falsification records store a free-text `target`, not
    always an exact node id), `match_confidence` says so rather than
    presenting the match as certain.
    """
    id: str
    kind: str
    status: str
    role: str
    raw: dict[str, Any]                       # the full registry entry, verbatim
    dependencies: list[str] = []
    dependents: list[str] = []                 # computed: reverse of dependencies
    provenance: Optional[ProvenanceModel] = None
    proofs: list[dict[str, Any]] = []          # proof_registry.json entries with transformation_id == this id
    calculations: list[dict[str, Any]] = []    # calculation_registry.json entries linked via provenance.calculation_id
    falsifications: list[FalsificationMatch] = []
    superseding_nodes: list[str] = []          # NOT YET IMPLEMENTED upstream — always [] (see note)
    superseding_nodes_note: str = (
        "NOT_IMPLEMENTED: the compiler has no supersession-tracking field today; "
        "this list is always empty rather than guessed."
    )


class FalsificationMatch(BaseModel):
    record: dict[str, Any]
    match_confidence: str  # "exact_id" | "prefix_match" | "substring_match"


NodeDetail.model_rebuild()


class AuditResultModel(BaseModel):
    name: str
    passed: bool
    issues: list[str] = []
    details: dict[str, Any] = {}


class StateRollup(BaseModel):
    """`GET /api/state` — computed live from the registries, never hard-coded
    (brief section VI's explicit requirement)."""
    total_nodes: int
    by_status: dict[str, int]
    by_kind: dict[str, int]
    terminal_status: Optional[str]
    all_audits_passed: bool
    audits: list[AuditResultModel]
    fc005_terminal_status: Optional[str]
    frontier_size: int
    generated_from: dict[str, str]   # which files/hashes this rollup was computed from


class FrontierNode(BaseModel):
    """One entry of `GET /api/frontier` -- brief section VII's
    F_t = {x not in C_t : Pred(x) subset C_t}."""
    id: str
    kind: str
    status: str
    unresolved_dependency_count: int  # always 0 for a true frontier node; included for transparency
    resolved_dependencies: list[str]
    downstream_unlock_count: int      # len(descendants(id)) -- transparent "why this node" input,
                                       # per brief section XV; NOT a synthesized significance score


class ChainlinkArrow(BaseModel):
    """One arrow of the master chainlink view (brief section XXIV).

    `from_id`/`to_id` reference real compiler/ir/forward_chain.py
    TEMPLATE_CHAIN node ids. `conceptual_symbol` is a human label only
    (e.g. "Δ", "L", "Spec(L)") -- it does not appear anywhere in the
    compiler's own IR and is provided purely for display, never used
    for lookups.
    """
    from_id: str
    to_id: str
    from_symbol: str
    to_symbol: str
    status: str                 # status of the `to_id` node
    der_id: Optional[str] = None
    der_id_note: str = (
        "NOT_IMPLEMENTED: this compiler has no DER-id concept -- always null."
    )
    proof: list[dict[str, Any]] = []
    dependencies: list[str] = []
    assumptions: list[str] = []
    calculations: list[dict[str, Any]] = []
    failures: list[FalsificationMatch] = []          # falsification_registry.json matches for to_id
    open_obligations: list[str] = []                 # to_id's dependencies not yet in the admissible/closed set
    literature: list[dict[str, Any]] = []             # always [] -- see literature_note
    literature_note: str = (
        "NOT_IMPLEMENTED: LITERATURE_EXTRACTION_REGISTRY.json has no node/equation "
        "linkage field (unlike falsification_registry.json's free-text `target`), so "
        "there is no honest way to match a literature item to this node without "
        "guessing. Left empty rather than fabricating a match."
    )
    execution_status: str       # "EXECUTED" | "NOT_IMPLEMENTED" -- brief section XIII's rule:
                                 # never imply a stage ran when it did not


class ChainlinkView(BaseModel):
    arrows: list[ChainlinkArrow]
    note: str = (
        "This view renders compiler/ir/forward_chain.py's real TEMPLATE_CHAIN "
        "(spec section 6), which is a DEPENDENCY TEMPLATE, not a proof -- every "
        "node here is OPEN by construction until SELECTION-SIGMA (also OPEN) is "
        "independently resolved. The classic notation (Δ→Γ→G→L→"
        "Spec(L)→...) is a conceptual relabeling of these real node ids for "
        "display, not a separate or more-derived chain."
    )
