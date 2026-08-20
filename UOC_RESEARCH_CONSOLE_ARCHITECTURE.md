# UOC Research Console — Architecture Specification (Phase 1)

Internal identifier: `uoc-research-console`. This document is the Phase 1 deliverable: it fixes
technology choices, directory layout, data model, API contract, and execution model before any
Phase 2+ code is written. Everything here is additive to the existing repository — nothing in
`compiler/` is renamed, rewritten, or altered by this spec.

**Scope note:** per the Phase 0 reconnaissance finding, the DER Registry / UOC synchronization
corpus from the parallel research thread is out of scope for this build. It is not committed to
this repository and this spec does not import it. If that changes, it is a separate, explicitly
scoped decision — not an implicit side effect of building this console.

---

## 1. System architecture

```
                         ┌────────────────────────────┐
                         │   uoc-research-console      │
                         │   (console/web, React SPA)  │
                         └──────────────┬───────────────┘
                                        │ HTTPS/JSON, read-mostly
                         ┌──────────────▼───────────────┐
                         │   console/api (FastAPI)       │
                         │   — the ONLY process allowed  │
                         │     to touch console state     │
                         └───────┬───────────────┬───────┘
                                 │               │
              ┌──────────────────┘               └──────────────────┐
              ▼                                                     ▼
  ┌────────────────────────┐                          ┌────────────────────────────┐
  │ Canonical State Adapter │                          │ Research Orchestrator       │
  │ (console/api/canonical) │                          │ (console/api/research)      │
  │  - read-only parsers    │                          │  - hypothesis engine        │
  │    for *_registry.json, │                          │  - literature workspace     │
  │    master_mdcl.json,    │                          │  - candidate generation     │
  │    status_matrix.json,  │                          │  - NEVER writes canonical   │
  │    self_audit_report,   │                          │    registries directly      │
  │    fc005_result.json    │                          └──────────────┬─────────────┘
  │  - execution trigger:   │                                         │
  │    subprocess call to   │                                         │
  │    compiler/run_        │                                         │
  │    compiler.py          │                                         │
  └───────────┬─────────────┘                                         │
              │ subprocess / in-process call, never a rewrite         │
              ▼                                                        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  EXISTING COMPILER (compiler/) — UNTOUCHED, remains sole source of        │
  │  physics/math truth. Status.can_transition() remains the only state      │
  │  machine. *_registry.json / master_mdcl.json remain the only canonical   │
  │  state files.                                                            │
  └─────────────────────────────────────────────────────────────────────────┘
              │
              ▼
  ┌─────────────────────────┐   ┌──────────────────────────┐   ┌───────────────────────┐
  │ console_runs/            │   │ console_research/          │   │ (no "UI state" store — │
  │ RUN-XXXX.json snapshots  │   │ hypotheses.jsonl,          │   │  UI state lives only   │
  │ + ledger.jsonl           │   │ ledger.jsonl,               │   │  in the browser)       │
  │ (NEW, append-only)       │   │ literature_cache.jsonl (NEW)│   │                        │
  └─────────────────────────┘   └──────────────────────────┘   └───────────────────────┘
```

Four state categories (per brief §XXIX), four physically separate storage locations:

| Category | Storage | Mutated by | Read by |
|---|---|---|---|
| **Canonical state** | existing `*_registry.json`, `master_mdcl.json`, `status_matrix.json`, `self_audit_report.json`, `fc005_result.json` at repo root | only `compiler/run_compiler.py` (via the API's execution adapter, which shells out to it — never writes these files itself) | canonical adapter (read-only) |
| **Run state** | new `console_runs/RUN-*.json` (one immutable snapshot per run) + `console_runs/ledger.jsonl` (append-only event log) | API execution adapter, immediately after each `run_compiler.py` invocation | Runs screen, run comparison |
| **Research history** | new `console_research/hypotheses.jsonl`, `console_research/ledger.jsonl`, `console_research/literature_cache.jsonl` | Research Orchestrator only | Research/Hypotheses/Literature screens |
| **UI state** | browser only (React state / URL query params) | frontend only | never persisted server-side, never influences canonical state |

## 2. Technology stack

| Layer | Choice | Why |
|---|---|---|
| Backend framework | **FastAPI** + **uvicorn** | Structured JSON in/out matches the registry schemas closely (pydantic models mirror the existing dataclasses almost 1:1); auto-generated OpenAPI schema is useful for a data-dense API with ~20 endpoints; async support matters once `POST /api/runs` needs to stream execution-console events (§XIII of the brief) rather than block. Declared in a **new** `console/requirements.txt`, kept separate from `compiler/requirements.txt` so the compiler's own dependency footprint is untouched. |
| Frontend framework | **React + TypeScript + Vite** | Node v22 is already available in this environment; Vite gives fast iteration for a data-dense SPA; TypeScript gives compile-time safety on the registry schemas, which matter here (a typo in a status enum should not silently render wrong). |
| Graph visualization | **React Flow** (`@xyflow/react`) + **dagre** for auto-layout | Purpose-built for typed node/edge graphs with custom node renderers (needed for status-colored nodes, badges for role/type), built-in pan/zoom/minimap/selection, and performs well at 105-node scale with room to grow. `dagre` gives a deterministic layered DAG layout appropriate for a dependency graph (vs. a generic force-directed layout, which would look messier for a strictly-ordered DAG). |
| Server-state management | **TanStack Query** | The frontend must never be a source of truth (brief §IV/§XXIX); TanStack Query enforces a read-through cache pattern where every value is fetched from the API and invalidated on mutation, rather than held in ad hoc component/global state that could drift from canonical truth. |
| UI state management | React context + URL search params for filters/selection | No new state library needed; keeps UI state explicitly out of any persistence layer. |
| Styling | Plain CSS modules / a minimal design-token file | No component-library dependency needed for a bespoke "research workstation" aesthetic (brief §XXVI explicitly wants this to *not* look like a generic admin dashboard, which most component libraries default to). |

No database is introduced. All console-side state (`console_runs/`, `console_research/`) is
flat JSON/JSONL on disk, consistent with how the compiler itself already persists everything —
this avoids infrastructure the brief's "do not introduce unnecessary infrastructure" rule warns
against, and keeps every state file `git diff`-able and auditable the same way the existing
registries are.

## 3. Repository layout (additions only)

```
SEIT/
  compiler/                 UNCHANGED
  console/
    requirements.txt        fastapi, uvicorn, pydantic (already a FastAPI dep)
    api/
      main.py                FastAPI app, route registration
      canonical/
        adapter.py            read-only parsers for the 12 existing state files
        frontier.py            F_t = {x not in C_t : Pred(x) subset C_t} computation
        chainlink.py           master-chainlink view assembly (brief §XXIV)
      execution/
        runner.py              subprocess wrapper around compiler.run_compiler,
                               single-backend-function invocation for scoped runs
        diff.py                before/after registry diff -> run snapshot + ledger events
        snapshot.py             console_runs/ read/write
      research/
        hypotheses.py          hypothesis CRUD (console_research/hypotheses.jsonl)
        ledger.py               append-only event log (shared shape with run ledger)
        literature.py           literature workspace adapter (wraps existing
                               literature/ directory content; new external search
                               is a Phase 9 decision, not assumed here)
      models.py                 pydantic schemas mirroring compiler/core/ir.py's
                               dataclasses field-for-field (never redefining them
                               independently)
      tests/                    API-level tests (Phase 11)
    web/
      package.json, vite.config.ts, tsconfig.json
      src/
        api/                    typed fetch client (generated from OpenAPI or hand-written)
        screens/                one directory per primary-nav item (§V of the brief)
        graph/                  React Flow node/edge renderers, layout, frontier-mode toggle
        components/              shared UI primitives (status badges, evidence panels, etc.)
        state/                   TanStack Query hooks, UI-only context
      tests/                    frontend tests (Phase 11)
  console_runs/                NEW, gitignored by default (see §7); append-only
  console_research/             NEW, gitignored by default; append-only
  UOC_RESEARCH_CONSOLE_ARCHITECTURE.md   this document
  RESEARCH_CONSOLE_REPOSITORY_MAP.md      Phase 0 deliverable (already committed)
```

## 4. Data model

### 4.1 Canonical state (read-only mirror, not redefinition)
The API never invents a new schema for nodes/equations/etc. `console/api/models.py` defines
pydantic models that are **structurally identical** to `compiler/core/ir.py`'s `Object`,
`Transformation`, `Equation`, and `Provenance` dataclasses (same field names, same types) so
that `object_registry.json` etc. can be loaded directly with no field mapping/renaming step —
eliminating an entire class of "the UI drifted from the compiler" bugs by construction.

### 4.2 Run state (new)
```python
class RunSnapshot(BaseModel):
    run_id: str                       # "RUN-0001", monotonic
    started_at: datetime
    completed_at: datetime | None
    trigger: Literal["full_rebuild", "scoped_node", "manual"]
    target_node_ids: list[str]        # empty for full_rebuild
    pre_state_hash: str               # sha256 of the pre-run registry set
    post_state_hash: str | None
    diff: RunDiff | None              # populated on completion
    test_suite_result: TestSuiteResult | None   # pytest summary, if run as part of this run
    self_audit_result: list[AuditResult] | None  # verbatim from self_audit_report.json
    terminal_status: str | None
    stopped_reason: Literal[
        "completed", "no_admissible_frontier", "dependency_failed",
        "proof_obligation_unsatisfied", "external_dependency_unavailable",
        "resource_limit", "user_stopped", "error"
    ] | None

class RunDiff(BaseModel):
    nodes_added: list[str]
    nodes_status_changed: list[NodeStatusChange]   # {id, old_status, new_status}
    nodes_unchanged: int
    new_falsifications: list[str]
    new_calculations: list[str]
    audit_deltas: list[str]           # audits that flipped pass/fail
```
Every `RunSnapshot` is written once, at run completion, to `console_runs/{run_id}.json` and
never edited afterward — "never overwrite prior states" (brief §VIII) enforced by the storage
layer refusing overwrite-on-existing-run-id, not merely by convention.

### 4.3 Research ledger event (append-only, brief §XII)
```python
class LedgerEvent(BaseModel):
    event_id: str                     # uuid4
    timestamp: datetime
    run_id: str | None                # null for research events outside a run
    actor: Literal["system", "user", "research_engine"]
    node_id: str | None
    action: Literal[
        "RUN_STARTED", "NODE_SELECTED", "LITERATURE_SEARCH", "SOURCE_ACQUIRED",
        "CANDIDATE_CREATED", "DERIVATION_EXECUTED", "PROOF_ATTEMPTED",
        "TEST_EXECUTED", "FALSIFICATION", "PROMOTION", "REJECTION",
        "SUPERSESSION", "AUDIT_COMPLETED", "RUN_COMPLETED"
    ]
    inputs: dict
    outputs: dict
    status: str
    provenance: dict
    content_hash: str | None          # sha256 of (action+inputs+outputs), for tamper-evidence
```
Appended, never rewritten, to `console_research/ledger.jsonl`. The API exposes no
delete/update endpoint for ledger entries — only `POST .../events` (append) and `GET`.

### 4.4 Hypothesis (brief §XI)
```python
class Hypothesis(BaseModel):
    id: str                           # "HYP-0001"
    statement: str
    target_node_id: str
    dependencies: list[str]
    assumptions: list[str]
    evidence: list[EvidenceRef]       # links into ledger events / literature cache
    tests: list[TestRef]
    status: Literal[
        "PROPOSED", "TESTING", "SUPPORTED", "DERIVED", "VERIFIED",
        "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED"
    ]
    created_at: datetime
    updated_at: datetime
    provenance: dict
    superseded_by: str | None
```
Stored in `console_research/hypotheses.jsonl`, one line appended per state change (never
mutated in place — "current" state is the latest line for a given `id`, giving the full history
for free, matching the WRITE/MERGE/RECALL/RESOLVE/REJECT/SUPERSEDE model from brief §II.C).
**Critically: a `Hypothesis.status` of `VERIFIED`/`DERIVED` is informational only.** It does
**not** and cannot promote the corresponding canonical MDCL node's status — that only happens
if/when the compiler itself, via a real backend execution, assigns that status through
`Status.can_transition()`. See §6.

## 5. Canonical state adapter — exact mapping

| Endpoint (see §7) | Reads | Computed or verbatim |
|---|---|---|
| `GET /api/state` | `status_matrix.json`, `self_audit_report.json`, `fc005_result.json` | computed rollup (counts by status, audit pass/fail, terminal status) — **never hard-coded**, matches brief §VI |
| `GET /api/mdcl` | `master_mdcl.json` | verbatim |
| `GET /api/nodes` | `object_registry.json` + `transformation_registry.json` + `equation_registry.json` | merged, verbatim per-node |
| `GET /api/nodes/:id` | above + `proof_registry.json`, `calculation_registry.json`, `falsification_registry.json`, `provenance_registry.json` | assembled per node (brief §VII's NODE ID/NAME/TYPE/.../SUPERSEDING NODES panel) |
| `GET /api/frontier` | `master_mdcl.json` | **computed**: `F_t = {x not in C_t : Pred(x) subset C_t}`, `C_t` = nodes with status in `{VERIFIED, DERIVED, CALCULATED, CONDITIONAL}` (matches `ExecutionGuard`'s own admissibility set in `compiler/dependencies/graph.py`, reused not reinvented) |
| `GET /api/chainlink` | `master_mdcl.json` filtered to the spec-section-6 template ids | the Δ→Γ→G→L→...→δS=0 view (brief §XXIV), each arrow resolved against real registry entries — where no executed backend exists behind an arrow, the API returns `"execution_status": "NOT_IMPLEMENTED"` rather than omitting it or inventing a value (brief §XIII/§XXXII) |
| `GET /api/audits` | `self_audit_report.json` | verbatim |
| `GET /api/runs`, `/api/runs/:id` | `console_runs/*.json` | verbatim (new store) |

## 6. Execution model — how "RUN THEORY SEARCH" cannot fabricate closure

This is the part of the system most exposed to the brief's central risk ("the application must
never manufacture closure merely because a UI element says complete"), so the enforcement is
structural, not a UI convention:

1. `POST /api/runs` accepts a `policy` (frontier ranking config, resource limits) and creates a
   `RunSnapshot` in `status="running"`, then invokes the execution adapter.
2. The execution adapter's **only** write path to canonical state is calling
   `compiler.run_compiler.build_and_run()` (full rebuild) — there is currently no scoped
   single-node execution function in the compiler (confirmed in Phase 0), so **until Phase 2
   adds one**, every "run" is a full compiler rebuild, and the API is explicit about this in the
   response (`"scope": "full_rebuild"`) rather than implying a targeted run happened.
3. After the subprocess returns, the adapter re-reads the registry files, computes the `RunDiff`
   against the pre-run snapshot, and writes the completed `RunSnapshot` + appends `LedgerEvent`s.
   **The diff is derived from actual file content, not from what the run "intended" to do.**
4. Any status change in the diff reflects a status the compiler itself assigned via
   `Status.can_transition()` during registration — the API layer has no code path that sets a
   node's status directly. There is no `PATCH /api/nodes/:id/status` endpoint, by design.
5. Administrative override (brief §XVII, last paragraph), if ever needed, is a **separate,
   clearly-labeled** endpoint `POST /api/nodes/:id/override` that writes a
   `LedgerEvent(action="PROMOTION", actor="user", ...)` carrying a mandatory `reason` field and
   the caller's identity, and writes a companion `OVERRIDE_WARNING` audit-log line — but it
   still cannot write to `object_registry.json`/etc. directly; it can only annotate the run
   ledger with a flagged, human-reviewable exception. Canonical files remain compiler-output-only.

## 7. Version control policy for new state directories

`console_runs/` and `console_research/` are **gitignored by default** (append-only operational
logs, not research content — same treatment `data/desi/dr1/fc005/raw/` already gets in
`.gitignore` for large/generated artifacts). If you want run history to be part of the
repository's audit trail rather than local-only, that's a one-line `.gitignore` change — flagging
this as an explicit decision point rather than assuming either way.

## 8. Testing strategy (Phase 11, planned now)

- **Non-regression (must pass before and after every phase, per brief §XXXIII):**
  `python3 -m pytest compiler/tests -q` (95 tests) and `python3 -m compiler.run_compiler`
  (10/10 audits) — CI step run at the end of every phase, diff-checked against a clean
  `git status`.
- **API tests** (`console/api/tests/`): assert every read endpoint's output is byte-identical
  to directly parsing the corresponding registry file; assert `/api/frontier`'s output against
  a hand-computed frontier for a small fixture MDCL; assert no endpoint exists that can set a
  node's status without going through `run_compiler`.
- **Integration tests**: full `POST /api/runs` against the real compiler in a temp copy of the
  repo state, confirming the resulting `RunSnapshot.diff` matches an independently computed
  before/after registry diff.
- **Frontend tests**: React Testing Library for node inspector rendering against real fixture
  JSON (not synthetic "TOE complete" data, per brief §XXXII); Playwright/Cypress smoke test for
  graph render + frontier-mode toggle against the real current MDCL.
- **Explicit brief-mandated tests** (§XXXI items 15-17): a test asserting no API route exists
  that promotes a node directly; a test that a `FAIL`/`FALSIFIED` upstream dependency blocks a
  downstream scoped-execution request (`409` with the exact blocking node id, mirroring
  `ExecutionGuard`'s existing `DependencyError`); a test that rejected/falsified candidates
  remain queryable via `GET /api/nodes/:id` (never deleted) but excluded from `/api/frontier`.

## 9. Phase 2-12 mapping (unchanged from brief §XXXIII, now concretized)

| Phase | Deliverable in this architecture |
|---|---|
| 2 | `console/api` — canonical adapter + `/api/state`, `/api/mdcl`, `/api/nodes*`, `/api/frontier`, `/api/audits`, `/api/chainlink` (read-only, no execution yet) |
| 3 | `console/web` shell: routing for the 15 primary-nav screens, all showing real data or explicit `NOT IMPLEMENTED` |
| 4 | React Flow MDCL graph wired to `/api/nodes` + `/api/mdcl`, frontier-mode toggle |
| 5 | Node/DER inspector panel, chainlink view |
| 6 | Execution console (`POST /api/runs`, full-rebuild only at first) + live ledger tail |
| 7 | Research orchestrator + hypothesis engine (net-new, writes only to `console_research/`) |
| 8 | Proof/falsification workspaces, circular-dependency detector (reuses `compiler.falsification.protocols`) |
| 9 | Literature workspace wired to existing `literature/` directory content; external search is scoped separately if requested |
| 10 | Run history, run comparison, `RunDiff` viewer |
| 11 | Full test suite per §8 above |
| 12 | Production build (`vite build`, `uvicorn` deployment config) |

---

**Open decision before Phase 2 starts writing code:** confirm `console_runs/` /
`console_research/` should be gitignored (§7) rather than committed — proceeding on that default
unless told otherwise.
