"""UOC Research Console API -- Phase 2: read-only canonical-state adapters.

Run with:  uvicorn console.api.main:app --reload --port 8000  (from repo root)

Phase 2 scope, per UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 9: read
endpoints only. There is intentionally no route anywhere in this module
that can set a node's status, write a registry file, or otherwise
mutate canonical state -- that capability does not exist yet (Phase 6),
and when it is added it will only ever be a thin wrapper that invokes
the real `compiler.run_compiler` and reports the resulting diff, never
a direct write.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from console.api.canonical import adapter, chainlink as chainlink_mod, frontier as frontier_mod
from console.api.models import (
    AuditResultModel, ChainlinkView, FrontierNode, NodeDetail, NodeSummary, StateRollup,
)

app = FastAPI(
    title="UOC Research Console API",
    description="Read-only interface over the Forward-MDCL compiler's canonical state. "
                "The compiler and its registries remain the sole source of truth.",
    version="0.1.0-phase2",
)

# Permissive CORS for local dev only (console/web running on a separate
# Vite dev-server port). Tightened in Phase 12 (production build).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
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
        superseding_nodes=[],
    )


@app.get("/api/frontier", response_model=list[FrontierNode])
def get_frontier() -> list[FrontierNode]:
    """F_t = {x not in C_t : Pred(x) subset C_t} -- brief section VII.
    C_t reuses compiler/dependencies/graph.py's own admissible-status set."""
    _load_or_503()
    nodes = adapter.get_all_nodes_merged()
    reverse = adapter.build_reverse_dependency_index(nodes)
    return [FrontierNode(**e) for e in frontier_mod.compute_frontier(nodes, reverse)]


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
    for arrow in arrows:
        arrow["proof"] = adapter.find_proofs_for_node(arrow["to_id"], reg["proofs"])
        arrow["calculations"] = adapter.find_calculations_for_node(
            arrow["to_id"], reg["provenance"], reg["calculations"]
        )
    return ChainlinkView(arrows=arrows)


@app.get("/api/fc005")
def get_fc005() -> dict:
    """Verbatim fc005_result.json -- the actual current status (brief
    section XXII: never imply DESI closure where the compiler reports
    failure/retriable/open)."""
    reg = _load_or_503()
    return reg["fc005_result"]
