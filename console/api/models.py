"""Pydantic response models for the UOC Research Console API.

Every model here mirrors a real compiler schema field-for-field rather
than inventing a new one (per UOC_RESEARCH_CONSOLE_ARCHITECTURE.md
section 4.1) — the intent is that these models are load-bearing
documentation of `compiler/core/ir.py`'s dataclasses and the on-disk
registry shapes, not an independent design.

Phases 2-5 are read-only. Phase 6 (RunSnapshot/RunDiff/LedgerEvent
below) introduces the one and only write path in the whole API:
`POST /api/runs`, which does nothing but invoke the real
`compiler.run_compiler.build_and_run()` and record what actually
changed on disk -- see console/api/execution/executor.py.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

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
    circular_dependency: "CircularDependencyCheck"


class FalsificationMatch(BaseModel):
    record: dict[str, Any]
    match_confidence: str  # "exact_id" | "prefix_match" | "substring_match"


class CircularDependencyCheck(BaseModel):
    """Proof Workspace (Phase 8): "Conclusion(T) in Premises(T)" check --
    a live DFS through the node's own transitive dependency closure
    looking for itself. Should always be False given the compiler's own
    cycle-rejection guard, but is computed independently here rather
    than assumed (see console/api/canonical/proof_check.py)."""
    is_circular: bool
    cycle_path: Optional[list[str]] = None


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
    historical_failure_rate: Optional[float] = None   # from real Hypothesis records (Phase 7);
                                                        # None (not 0.0) if no terminal hypothesis exists yet


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


class NodeStatusChange(BaseModel):
    id: str
    old_status: Optional[str]   # null if the node did not exist before this run
    new_status: str


class RunDiff(BaseModel):
    """Computed by re-reading the registry files before and after the
    run and comparing actual content -- never from what the run
    "intended" to do (architecture doc section 6, point 3)."""
    nodes_added: list[str] = []
    nodes_status_changed: list[NodeStatusChange] = []
    nodes_unchanged: int = 0
    new_falsifications: list[str] = []
    new_calculations: list[str] = []
    audit_deltas: list[str] = []   # audit names whose passed/failed flipped


class RunSnapshot(BaseModel):
    """One row of GET /api/runs -- written once at completion to
    console_runs/{run_id}.json and never edited afterward (architecture
    doc section 4.2: 'never overwrite prior states', enforced by the
    store refusing to overwrite an existing run_id)."""
    run_id: str
    started_at: str    # ISO 8601
    completed_at: Optional[str] = None
    trigger: Literal["full_rebuild"] = "full_rebuild"
    scope: Literal["full_rebuild"] = "full_rebuild"   # see architecture doc section 6, point 2:
                                                        # no scoped single-node execution exists in
                                                        # the compiler yet, so every run is a full
                                                        # rebuild and the API says so explicitly
    target_node_ids: list[str] = []   # always [] until a scoped execution function exists
    pre_state_hash: str
    post_state_hash: Optional[str] = None
    diff: Optional[RunDiff] = None
    test_suite_result: Optional[dict[str, Any]] = None   # not run per-request (see executor.py); always null today
    self_audit_result: Optional[list[AuditResultModel]] = None
    terminal_status: Optional[str] = None
    stopped_reason: Optional[Literal[
        "completed", "no_admissible_frontier", "dependency_failed",
        "proof_obligation_unsatisfied", "external_dependency_unavailable",
        "resource_limit", "user_stopped", "error",
    ]] = None
    error: Optional[str] = None   # populated iff stopped_reason == "error"


class LedgerEvent(BaseModel):
    """One append-only line of console_research/ledger.jsonl (brief
    section XII / architecture doc section 4.3). Only RUN_STARTED and
    RUN_COMPLETED are emitted today -- the remaining action types
    (LITERATURE_SEARCH, CANDIDATE_CREATED, PROOF_ATTEMPTED, ...) belong
    to the research engine and proof/falsification workspaces (Phases
    7-8), which do not exist yet, so this module never emits them."""
    event_id: str
    timestamp: str
    run_id: Optional[str] = None
    actor: Literal["system", "user", "research_engine"] = "system"
    node_id: Optional[str] = None
    action: Literal[
        "RUN_STARTED", "NODE_SELECTED", "LITERATURE_SEARCH", "SOURCE_ACQUIRED",
        "CANDIDATE_CREATED", "DERIVATION_EXECUTED", "PROOF_ATTEMPTED",
        "TEST_EXECUTED", "FALSIFICATION", "PROMOTION", "REJECTION",
        "SUPERSESSION", "AUDIT_COMPLETED", "RUN_COMPLETED",
    ]
    inputs: dict[str, Any] = {}
    outputs: dict[str, Any] = {}
    status: str = ""
    provenance: dict[str, Any] = {}
    content_hash: Optional[str] = None


# ---------------------------------------------------------------------
# Phase 7: Hypothesis Engine (brief section XI, architecture doc 4.4).
# Stored in console_research/hypotheses.jsonl -- net-new state, never
# written back into the canonical registries, and a Hypothesis's status
# never promotes the MDCL node it targets (see
# console/api/research/hypothesis_status.py's module docstring).
# ---------------------------------------------------------------------

HYPOTHESIS_STATUSES = Literal[
    "PROPOSED", "TESTING", "SUPPORTED", "DERIVED", "VERIFIED",
    "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED",
]


class EvidenceRef(BaseModel):
    description: str
    kind: Literal["ledger_event", "run", "external", "other"] = "other"
    ref_id: Optional[str] = None   # e.g. a run_id or ledger event_id, when kind supports it


class TestRef(BaseModel):
    description: str
    result: Optional[Literal["pass", "fail", "pending"]] = None


class Hypothesis(BaseModel):
    id: str
    statement: str
    target_node_id: str
    dependencies: list[str] = []
    assumptions: list[str] = []
    evidence: list[EvidenceRef] = []
    tests: list[TestRef] = []
    status: HYPOTHESIS_STATUSES
    created_at: str
    updated_at: str
    provenance: dict[str, Any] = {}
    superseded_by: Optional[str] = None


class PossibleDuplicate(BaseModel):
    id: str
    statement: str
    status: str
    match_confidence: Literal["exact_normalized_match", "word_overlap"]
    similarity: float


class HypothesisCreateRequest(BaseModel):
    statement: str
    target_node_id: str
    dependencies: list[str] = []
    assumptions: list[str] = []
    evidence: list[EvidenceRef] = []
    provenance: dict[str, Any] = {}


class HypothesisCreateResponse(BaseModel):
    hypothesis: Hypothesis
    possible_duplicates: list[PossibleDuplicate] = []


class HypothesisTransitionRequest(BaseModel):
    new_status: HYPOTHESIS_STATUSES
    reason: str
    evidence: list[EvidenceRef] = []
    tests: list[TestRef] = []
    superseded_by: Optional[str] = None


class HypothesisDetail(BaseModel):
    current: Hypothesis
    history: list[Hypothesis]


# ---------------------------------------------------------------------
# Phase 8: Proof / Falsification Workspaces.
# ---------------------------------------------------------------------

class ProtocolReference(BaseModel):
    """One of the compiler's real falsification protocols, pulled live
    via `inspect` from compiler/falsification/protocols.py -- never a
    hand-typed duplicate that could silently drift out of sync."""
    name: str
    summary: str


class ProofRecordDetail(BaseModel):
    """One proof_registry.json entry, enriched with the transformation's
    real preconditions/postconditions/assumptions and the same
    open_obligations computation used by the chainlink view (brief
    section XXIV) -- dependencies not yet in the admissible/closed set,
    i.e. what is genuinely still standing between this proof and
    closure. `circular_dependency` reuses the same per-node self-
    reachability check as GET /api/nodes/:id."""
    id: str
    transformation_id: str
    statement: str
    method: str
    status: str
    preconditions: list[str] = []
    postconditions: list[str] = []
    assumptions: list[str] = []
    dependencies: list[str] = []
    open_obligations: list[str] = []
    circular_dependency: CircularDependencyCheck


class FalsificationsResponse(BaseModel):
    records: list[dict[str, Any]]      # verbatim falsification_registry.json entries
    protocols: list[ProtocolReference]  # the real, available protocol types (reference only)
