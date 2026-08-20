"""UOC Research Console API.

Run with:  uvicorn console.api.main:app --reload --port 8000  (from repo root)

Phases 2-5 are read-only. Phase 6 adds the one and only write route in
the whole API -- `POST /api/runs` -- and it is a thin wrapper that does
nothing but invoke the real `compiler.run_compiler.build_and_run()` and
report the resulting diff (see console/api/execution/executor.py).
There is still no route anywhere that can set a node's status directly
or write a registry file itself: every other route remains GET.
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from console.api.canonical import (
    adapter, chainlink as chainlink_mod, frontier as frontier_mod, proof_check,
)
from console.api.execution import executor, ledger_store, runs_store
from console.api.literature import adapter as literature_adapter
from console.api.models import (
    AuditResultModel, ChainlinkView, CircularDependencyCheck, FalsificationsResponse,
    FrontierNode, Hypothesis, HypothesisCreateRequest, HypothesisCreateResponse,
    HypothesisDetail, HypothesisTransitionRequest, LedgerEvent, LiteratureCrosswalkEntry,
    LiteratureItem, LiteratureRecovery, NodeDetail, NodeSummary, PossibleDuplicate,
    ProofRecordDetail, ProtocolReference, RunSnapshot, StateRollup,
)
from console.api.research import hypothesis_status, hypothesis_store

app = FastAPI(
    title="UOC Research Console API",
    description="Interface over the Forward-MDCL compiler's canonical state. The compiler "
                "and its registries remain the sole source of truth; POST /api/runs only ever "
                "invokes the compiler itself, and the Hypothesis Engine (POST /api/hypotheses*) "
                "writes only to console_research/hypotheses.jsonl, never to a registry.",
    version="0.1.0-phase7",
)

# Permissive CORS for local dev only (console/web running on a separate
# Vite dev-server port). Tightened in Phase 12 (production build).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _load_or_503() -> dict[str, Any]:
    try:
        return adapter.load_all()
    except adapter.RegistryNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "uoc-research-console-api", "phase": 2}


@app.get("/api/state", response_model=StateRollup)
def get_state() -> StateRollup:
    """Everything the Overview screen needs (brief section VI), computed
    live -- every number here is derived from the registry files on this
    request, never cached across requests and never hard-coded."""
    reg = _load_or_503()
    status_matrix = reg["status_matrix"]
    nodes = adapter.get_all_nodes_merged()
    reverse = adapter.build_reverse_dependency_index(nodes)
    frontier = frontier_mod.compute_frontier(nodes, reverse)

    by_status: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for row in status_matrix:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1

    audits_raw = reg["self_audit"]
    audits = [AuditResultModel(**a) for a in audits_raw]
    all_passed = all(a.passed for a in audits)

    fc005 = reg["fc005_result"]

    return StateRollup(
        total_nodes=len(status_matrix),
        by_status=by_status,
        by_kind=by_kind,
        terminal_status=fc005.get("terminal_status"),
        all_audits_passed=all_passed,
        audits=audits,
        fc005_terminal_status=fc005.get("terminal_status"),
        frontier_size=len(frontier),
        generated_from={
            "status_matrix": "status_matrix.json",
            "self_audit_report": "self_audit_report.json",
            "fc005_result": "fc005_result.json",
        },
    )


@app.get("/api/mdcl")
def get_mdcl() -> dict:
    """Verbatim master_mdcl.json."""
    reg = _load_or_503()
    return reg["master_mdcl"]


@app.get("/api/nodes", response_model=list[NodeSummary])
def list_nodes() -> list[NodeSummary]:
    _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    out = []
    for nid, n in sorted(nodes.items()):
        out.append(NodeSummary(
            id=nid, kind=n["kind"], status=n.get("status", "UNKNOWN"),
            role=n.get("role", "upstream_construction"),
            dependencies=n.get("dependencies", []),
            type=n.get("type"), domain=n.get("domain"), codomain=n.get("codomain"),
        ))
    return out


@app.get("/api/nodes/{node_id}", response_model=NodeDetail)
def get_node(node_id: str) -> NodeDetail:
    reg = _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail=f"no node with id '{node_id}'")
    node = nodes[node_id]
    reverse = adapter.build_reverse_dependency_index(nodes)

    provenance = reg["provenance"].get(node_id)
    proofs = adapter.find_proofs_for_node(node_id, reg["proofs"])
    calculations = adapter.find_calculations_for_node(node_id, reg["provenance"], reg["calculations"])
    falsifications = adapter.find_falsifications_for_node(node_id, reg["falsifications"])
    circular = CircularDependencyCheck(**proof_check.check_circular_dependency(node_id, nodes))
    lit_crosswalk = [
        LiteratureCrosswalkEntry(**row) for row in literature_adapter.get_crosswalk(nodes)
        if row["mdcl_node_id"] == node_id
    ]

    return NodeDetail(
        id=node_id, kind=node["kind"], status=node.get("status", "UNKNOWN"),
        role=node.get("role", "upstream_construction"),
        raw=node,
        dependencies=node.get("dependencies", []),
        dependents=reverse.get(node_id, []),
        provenance=provenance,
        proofs=proofs,
        calculations=calculations,
        falsifications=falsifications,
        circular_dependency=circular,
        literature_crosswalk=lit_crosswalk,
        superseding_nodes=[],
    )


@app.get("/api/frontier", response_model=list[FrontierNode])
def get_frontier() -> list[FrontierNode]:
    """F_t = {x not in C_t : Pred(x) subset C_t} -- brief section VII.
    C_t reuses compiler/dependencies/graph.py's own admissible-status set.
    `historical_failure_rate` (Phase 7) is the one enrichment layered on
    top of the pure canonical computation: a real rate computed from
    terminal Hypothesis records in console_research/hypotheses.jsonl,
    left null (not 0.0) for a node with no terminal hypothesis yet."""
    _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    reverse = adapter.build_reverse_dependency_index(nodes)
    failure_rates = hypothesis_store.historical_failure_rates()
    entries = frontier_mod.compute_frontier(nodes, reverse)
    for e in entries:
        e["historical_failure_rate"] = failure_rates.get(e["id"])
    return [FrontierNode(**e) for e in entries]


@app.get("/api/audits", response_model=list[AuditResultModel])
def get_audits() -> list[AuditResultModel]:
    reg = _load_or_503()
    return [AuditResultModel(**a) for a in reg["self_audit"]]


@app.get("/api/chainlink", response_model=ChainlinkView)
def get_chainlink() -> ChainlinkView:
    """The Master Chainlink view (brief section XXIV), rendered from the
    real compiler/ir/forward_chain.py::TEMPLATE_CHAIN -- not a
    hand-maintained duplicate."""
    _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    arrows = chainlink_mod.build_chainlink_view(nodes)
    # enrich with real proofs where a proof exists for the target node
    reg = adapter.load_all()
    crosswalk = literature_adapter.get_crosswalk(nodes)
    for arrow in arrows:
        arrow["proof"] = adapter.find_proofs_for_node(arrow["to_id"], reg["proofs"])
        arrow["calculations"] = adapter.find_calculations_for_node(
            arrow["to_id"], reg["provenance"], reg["calculations"]
        )
        arrow["failures"] = adapter.find_falsifications_for_node(arrow["to_id"], reg["falsifications"])
        lit_matches = [row["raw"] for row in crosswalk if row["mdcl_node_id"] == arrow["to_id"]]
        arrow["literature"] = lit_matches
        if lit_matches:
            arrow["literature_note"] = (
                f"{len(lit_matches)} curated crosswalk row(s) name this node as their "
                f"MDCL_NODE_ID (literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv)."
            )
    return ChainlinkView(arrows=arrows)


@app.get("/api/fc005")
def get_fc005() -> dict:
    """Verbatim fc005_result.json -- the actual current status (brief
    section XXII: never imply DESI closure where the compiler reports
    failure/retriable/open)."""
    reg = _load_or_503()
    return reg["fc005_result"]


# ---------------------------------------------------------------------
# Phase 8: Proof / Falsification Workspaces. Both read-only -- neither
# endpoint below can register a proof, mark something falsified, or
# otherwise write a registry; they only surface real proof_registry.json
# / falsification_registry.json content plus the live circular-
# dependency re-check (see console/api/canonical/proof_check.py).
# ---------------------------------------------------------------------

def _build_proof_detail(proof: dict, nodes: dict, closed: set[str]) -> ProofRecordDetail:
    transformation_id = proof["transformation_id"]
    t = nodes.get(transformation_id, {})
    deps = t.get("dependencies", [])
    circular = proof_check.check_circular_dependency(transformation_id, nodes)
    return ProofRecordDetail(
        id=proof["id"],
        transformation_id=transformation_id,
        statement=proof.get("statement", ""),
        method=proof.get("method", ""),
        status=proof.get("status", "UNKNOWN"),
        preconditions=t.get("preconditions", []),
        postconditions=t.get("postconditions", []),
        assumptions=t.get("assumptions", []),
        dependencies=deps,
        open_obligations=[d for d in deps if d not in closed],
        circular_dependency=CircularDependencyCheck(**circular),
    )


@app.get("/api/proofs", response_model=list[ProofRecordDetail])
def list_proofs() -> list[ProofRecordDetail]:
    reg = _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    closed = frontier_mod.compute_closed_set(nodes)
    return [_build_proof_detail(p, nodes, closed) for p in reg["proofs"]]


@app.get("/api/proofs/{node_id}", response_model=ProofRecordDetail)
def get_proof(node_id: str) -> ProofRecordDetail:
    reg = _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    matches = [p for p in reg["proofs"] if p["transformation_id"] == node_id]
    if not matches:
        raise HTTPException(status_code=404, detail=f"no proof record for node '{node_id}'")
    closed = frontier_mod.compute_closed_set(nodes)
    return _build_proof_detail(matches[0], nodes, closed)


@app.get("/api/falsifications", response_model=FalsificationsResponse)
def list_falsifications() -> FalsificationsResponse:
    """Every falsification record, verbatim, including failed ones --
    "failed tests remain permanently attached" (brief: Falsification
    Workspace) is a fact about falsification_registry.json itself
    (compiler/run_compiler.py never filters it), not a UI promise; this
    endpoint just doesn't add a filter that isn't already absent. The
    `protocols` list is the compiler's real, available falsification
    protocol types for reference -- not a menu of runnable actions, since
    each protocol needs real per-node math wired in by hand (Phase 0
    finding: no generic runner exists)."""
    reg = _load_or_503()
    return FalsificationsResponse(
        records=reg["falsifications"],
        protocols=[ProtocolReference(**p) for p in proof_check.falsification_protocol_reference()],
    )


# ---------------------------------------------------------------------
# Phase 9: Literature Workspace, wired to the existing literature/
# ingestion architecture. Read-only, and it makes no network calls --
# external literature search is explicitly out of scope (not requested,
# see console/api/literature/adapter.py's module docstring).
# ---------------------------------------------------------------------

@app.get("/api/literature/sources", response_model=list[dict[str, Any]])
def list_literature_sources() -> list[dict[str, Any]]:
    return literature_adapter.get_sources()


@app.get("/api/literature/items", response_model=list[LiteratureItem])
def list_literature_items() -> list[LiteratureItem]:
    return [LiteratureItem(**item) for item in literature_adapter.get_items()]


@app.get("/api/literature/crosswalk", response_model=list[LiteratureCrosswalkEntry])
def list_literature_crosswalk(node_id: str | None = None) -> list[LiteratureCrosswalkEntry]:
    nodes = adapter.get_all_nodes_merged()
    rows = literature_adapter.get_crosswalk(nodes)
    if node_id:
        rows = [r for r in rows if r["mdcl_node_id"] == node_id]
    return [LiteratureCrosswalkEntry(**r) for r in rows]


@app.get("/api/literature/recoveries", response_model=list[LiteratureRecovery])
def list_literature_recoveries() -> list[LiteratureRecovery]:
    return [LiteratureRecovery(**r) for r in literature_adapter.get_recoveries()]


# ---------------------------------------------------------------------
# Phase 6: Execution Console. POST /api/runs is the only mutating route
# in this API, and it is a thin wrapper around
# compiler.run_compiler.build_and_run() -- see execution/executor.py's
# module docstring for the full contract. A module-level lock rejects a
# second run while one is already in flight, since build_and_run()
# writes the same registry files a concurrent run would also write to.
# ---------------------------------------------------------------------

_run_lock = asyncio.Lock()


@app.post("/api/runs", response_model=RunSnapshot, status_code=201)
async def create_run() -> RunSnapshot:
    if _run_lock.locked():
        raise HTTPException(status_code=409, detail="a run is already in progress")
    async with _run_lock:
        # build_and_run() is synchronous and can take real time (full
        # MDCL rebuild + self-audit) -- run it off the event loop so
        # the API stays responsive to other requests (e.g. GET
        # /api/ledger polling) while it executes.
        snapshot = await run_in_threadpool(executor.execute_full_rebuild_run)
    return RunSnapshot(**snapshot)


@app.get("/api/runs", response_model=list[RunSnapshot])
def list_runs() -> list[RunSnapshot]:
    return [RunSnapshot(**s) for s in runs_store.load_all()]


@app.get("/api/runs/{run_id}", response_model=RunSnapshot)
def get_run(run_id: str) -> RunSnapshot:
    snapshot = runs_store.load(run_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"no run with id '{run_id}'")
    return RunSnapshot(**snapshot)


@app.get("/api/ledger", response_model=list[LedgerEvent])
def get_ledger(limit: int = 50) -> list[LedgerEvent]:
    """Tail of the append-only research ledger, newest last. Empty (not
    an error) until the first run has happened."""
    return [LedgerEvent(**e) for e in ledger_store.tail(limit)]


# ---------------------------------------------------------------------
# Phase 7: Hypothesis Engine. Writes only to
# console_research/hypotheses.jsonl -- never to a canonical registry.
# A Hypothesis's status is informational: nothing here can promote the
# MDCL node it targets (see console/api/research/hypothesis_status.py's
# module docstring, architecture doc section 4.4).
# ---------------------------------------------------------------------

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


@app.post("/api/hypotheses", response_model=HypothesisCreateResponse, status_code=201)
def create_hypothesis(req: HypothesisCreateRequest) -> HypothesisCreateResponse:
    nodes = adapter.get_all_nodes_merged()
    if req.target_node_id not in nodes:
        raise HTTPException(
            status_code=400,
            detail=f"no such node '{req.target_node_id}' in the current MDCL -- a hypothesis "
                   f"must target a real, currently-registered node",
        )
    possible_duplicates = hypothesis_store.find_possible_duplicates(req.target_node_id, req.statement)

    now = _now_iso()
    record = {
        "id": hypothesis_store.next_hypothesis_id(),
        "statement": req.statement,
        "target_node_id": req.target_node_id,
        "dependencies": req.dependencies,
        "assumptions": req.assumptions,
        "evidence": [e.model_dump() for e in req.evidence],
        "tests": [],
        "status": "PROPOSED",
        "created_at": now,
        "updated_at": now,
        "provenance": req.provenance,
        "superseded_by": None,
    }
    hypothesis_store.append(record)
    return HypothesisCreateResponse(
        hypothesis=Hypothesis(**record),
        possible_duplicates=[PossibleDuplicate(**d) for d in possible_duplicates],
    )


@app.post("/api/hypotheses/{hypothesis_id}/transition", response_model=Hypothesis)
def transition_hypothesis(hypothesis_id: str, req: HypothesisTransitionRequest) -> Hypothesis:
    current = hypothesis_store.load_current(hypothesis_id)
    if current is None:
        raise HTTPException(status_code=404, detail=f"no hypothesis with id '{hypothesis_id}'")
    if not hypothesis_status.can_transition(current["status"], req.new_status):
        raise HTTPException(
            status_code=409,
            detail=f"cannot transition {hypothesis_id} from {current['status']} to {req.new_status} "
                   f"(allowed: {sorted(hypothesis_status.ALLOWED_TRANSITIONS.get(current['status'], set()))})",
        )

    record = dict(current)
    record["status"] = req.new_status
    record["updated_at"] = _now_iso()
    if req.evidence:
        record["evidence"] = list(current.get("evidence", [])) + [e.model_dump() for e in req.evidence]
    if req.tests:
        record["tests"] = list(current.get("tests", [])) + [t.model_dump() for t in req.tests]
    if req.superseded_by is not None:
        record["superseded_by"] = req.superseded_by
    # The reason is preserved permanently -- it's never lost, because
    # every prior line (with its own provenance) stays in the jsonl
    # history forever; this just records the reason for *this* line.
    record["provenance"] = {**current.get("provenance", {}), "last_transition_reason": req.reason}

    hypothesis_store.append(record)
    return Hypothesis(**record)


@app.get("/api/hypotheses", response_model=list[Hypothesis])
def list_hypotheses(target_node_id: str | None = None, status: str | None = None) -> list[Hypothesis]:
    """Current (latest) state of every hypothesis, optionally filtered.
    Answers the brief's "what have we already tried for this node"
    question directly: GET /api/hypotheses?target_node_id=X."""
    records = hypothesis_store.load_current_all()
    if target_node_id:
        records = [r for r in records if r["target_node_id"] == target_node_id]
    if status:
        records = [r for r in records if r["status"] == status]
    return [Hypothesis(**r) for r in records]


@app.get("/api/hypotheses/{hypothesis_id}", response_model=HypothesisDetail)
def get_hypothesis(hypothesis_id: str) -> HypothesisDetail:
    history = hypothesis_store.load_history(hypothesis_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"no hypothesis with id '{hypothesis_id}'")
    return HypothesisDetail(
        current=Hypothesis(**history[-1]),
        history=[Hypothesis(**h) for h in history],
    )
