# RESEARCH_CONSOLE_REPOSITORY_MAP

**Phase 0 reconnaissance deliverable for the UOC Research Console.** This document is
descriptive only — nothing in the repository was modified to produce it (verified: `git status`
clean before and after; the compiler was run once to confirm reproducibility, then all
regenerated files were `git checkout`-restored, per the reconnaissance-phase rule against
altering canonical physics state).

Current state at time of this map: branch `claude/forward-mdcl-compiler-build-ng4k2k`, HEAD
`1a3a25e`, working tree clean. `python3 -m pytest compiler/tests -q` → **95 passed**.
`python3 -m compiler.run_compiler` → terminal status **CONDITIONALLY_CLOSED**, **10/10 self-audits
PASS**, bitwise-reproducible re-run confirmed.

---

## 1. Repository architecture

```
SEIT/
  compiler/                    the canonical computational substrate (pure Python, no side effects on import)
    core/          ir.py, status.py                 — IR node types, Status enum + legal transitions
    ir/            registry.py, forward_chain.py,
                   executable_tests.py, fc005.py,
                   toe_closure_hypotheses.py         — registration into MDCLRegistries
    dependencies/  graph.py                          — DAG + cycle rejection + ExecutionGuard
    backends/      9 modules                         — the actual executable mathematics
    verification/  verify.py, self_audit.py,
                   heat_kernel_fit.py, fisher_information.py
    falsification/ protocols.py, target_independence.py, eigen_uniqueness.py
    provenance/    provenance.py
    historical/    register.py, fc005_reconciliation.py
    workbook/      build_workbook.py
    tests/         13 test files, 95 tests
    run_compiler.py               — the single orchestrator; only place that writes files
  data/desi/dr1/fc005/           real DESI DR1 LRG SGC catalogue + derived artifacts
  fc005_source_workbooks/        4 supplied historical workbooks (provenance copies)
  literature/                    string-theory literature ingestion (L0-ST phase)
  L0_PROPOSED_RECOVERY_RECORDS/  3 recovery-candidate JSON records
  *_registry.json, master_mdcl.json, status_matrix.json,
  self_audit_report.json, target_independence.json    — regenerated on every run_compiler.py call
  Master Calculation Workbook.xlsx                    — regenerated, 16 required sheets
  ~40 root-level *.md / *.csv / *.json reports         — hand-written or generator-script output
    from 5 prior research campaigns (see §7)
  ~25 root-level .pdf/.docx                            — the pre-compiler historical document corpus
```

**Important finding: there is no DER registry, no UOC/Rosetta-Stone synchronization workbook, and
no PDG/POL/MCT/MCL content anywhere in this git repository.** That entire corpus (DER_Registry.docx
v1/v2, UOCP_Formal_Registry.docx, UDP whitepaper, UCG Specification v5, PDG-001/POL-002, CVR-001,
the 309-sheet and 231-sheet master calculation workbooks, etc.) was supplied as chat uploads in a
parallel research thread this session and audited in a **separate scratchpad location outside this
repository** — it was never committed here, by design (that campaign was explicitly instructed not
to touch this repo). If the Research Console is meant to surface that UOC/DER material, it does not
yet exist as repository state; see §12.

## 2. Canonical state objects and their source of truth

| Object | File | Written by | Read by |
|---|---|---|---|
| Types | `type_registry.json` | `MDCLRegistries.dump_all()` | workbook, self-audit |
| Objects | `object_registry.json` | same | same |
| Transformations | `transformation_registry.json` | same | same |
| Equations | `equation_registry.json` | same | same |
| Status matrix (flattened id/kind/status/deps) | `status_matrix.json` | `MDCLRegistries.status_matrix()` | dashboard-equivalent consumers |
| Full MDCL (types+objects+transformations+equations+status_matrix) | `master_mdcl.json` | `run_compiler.build_and_run()` | everything downstream |
| Proofs | `proof_registry.json` | `run_compiler.py` (from `Transformation.proof`) | workbook |
| Calculations | `calculation_registry.json` | `run_compiler.py` (aggregated from `register_executable_tests`/`register_fc005`/`register_toe_closure_hypotheses`) | workbook, self-audit |
| Falsifications | `falsification_registry.json` | `run_compiler.py` (`FalsificationRecord.to_dict()`) | leakage-control audit |
| Provenance | `provenance_registry.json` | `run_compiler.py` (every node's `.provenance`) | provenance audit |
| Target-independence findings | `target_independence.json` | `compiler/falsification/target_independence.py::scan_registries` | target-independence audit |
| Self-audit results | `self_audit_report.json` | `compiler/verification/self_audit.py::run_self_audit` | terminal-status computation |
| FC-005 stage-gate summary | `fc005_result.json` | `run_compiler.py` (FC-005-specific block) | FC-005 UI panel |
| Workbook | `Master Calculation Workbook.xlsx` | `compiler/workbook/build_workbook.py` | human/Excel consumers only — not re-parsed by the compiler |

**Every one of these is fully regenerated, not incrementally patched, on each `run_compiler.py`
call.** There is no incremental-update API in the compiler today — this is the single largest gap
the web layer must bridge (see §11 execution model).

## 3. IR node schema (`compiler/core/ir.py`)

Three node kinds, all sharing a common base (`id`, `status: Status`, `dependencies: list[str]`,
`assumptions: list[str]`, `provenance: Provenance`, `role: str`):

- **Object**: `+ type, carrier, operations, relations, constraints`
- **Transformation**: `+ domain, codomain, action, preconditions, postconditions, proof`
- **Equation**: `+ lhs, rhs, domain, derivation, verification`

`Provenance` (`compiler/provenance/provenance.py::make_provenance`): `source, source_version,
object_id, equation_id, dependency_ids, transformation_id, calculation_id,
execution_timestamp, git_commit, code_version, numerical_environment, status, verification`.

`Status` (`compiler/core/status.py`): `VERIFIED | DERIVED | CALCULATED | CONDITIONAL | PROPOSED |
OPEN | FAIL | FALSIFIED`, with an explicit `ALLOWED_TRANSITIONS` table and `can_transition(old,
new)` — **this is the real, already-implemented state machine** Section XVII of the brief asks
for. `map_legacy_status()` forces every prose "CERTIFIED"/"PROVEN"/etc. label from a source
document down to `PROPOSED` — no UI action should ever be able to bypass this.

`TerminalStatus`: `CLOSED | PARTIALLY_CLOSED | CONDITIONALLY_CLOSED | FALSIFIED`, computed (never
asserted) in `run_compiler.build_and_run()` from actual audit results and whether any upstream
template node is still `OPEN`.

## 4. Current MDCL snapshot (live numbers, not hard-coded)

105 total nodes (62 `Object`, 35 `Equation`, 8 `Transformation`).

| Status | Count |
|---|---|
| OPEN | 37 |
| PROPOSED | 35 |
| VERIFIED | 12 |
| CALCULATED | 10 |
| FAIL | 5 |
| CONDITIONAL | 3 |
| FALSIFIED | 2 |
| DERIVED | 1 |

Terminal status: **CONDITIONALLY_CLOSED** (never forced `CLOSED` — `SELECTION-SIGMA` and the
spec-section-6 template chain remain `OPEN` by design; `H1-SELECTION-WELLPOSEDNESS` independently
confirms why). All 10 self-audits `PASS`, 0 issues each.

The console's job is to compute and re-derive every number above **live from these files**, per
Section VI of the brief — never hard-code them.

## 5. Executable backends (`compiler/backends/`) — what actually runs vs. what is metadata

| Module | Executes real math? | What it does |
|---|---|---|
| `graph_laplacian.py` | YES | 7 graph topologies, `L = D - A` |
| `spectral.py` | YES | eigen-decomposition, spectral gap, kernel projector |
| `heat_flow.py` | YES | `R(t) = e^{-tL}`, convergence-to-kernel checks |
| `pipeline_graph_heatflow.py` | YES | Test 1 orchestration + 14-case sweep, exact-arithmetic cross-check (sympy) for n≤8 |
| `diffusion_metric.py` | YES | Test 2: diffusion distance, metric-candidate classification (never `exact`, empirically always `non_unique`) |
| `heat_kernel_sphere.py` | YES | S³ analytic heat-kernel control (regression test) |
| `desi_graph.py` | YES (code + synthetic tests); real-data execution lives in the root-level `run_desi_*.py` scripts | discrete-observation → continuum bridge primitives |
| `desi_sparse.py` | YES | sparse kernel graph, ARPACK low-eigenmode solver, N-scaling machinery — this is what actually ran against real DESI data |
| `desi_fc005_pipeline.py` | YES | the three-stage (convergence → curvature → validation) procedure, each stage independently gated |
| `desi_diagnostics.py` | YES | bandwidth/N sweeps, boundary/mask diagnostics |
| `toe_closure_hypotheses.py` | YES | H1-H4 closure-hypothesis tests (selection well-posedness, spectral-triple locality, FC-005 correction test, G2/Spin(8) rank argument) |

**Nothing in `compiler/backends/` is a stub or mock.** Every module is pure functions + a
dataclass result + an explicit hypothesis check before any convergence/correspondence claim,
per `compiler_architecture.md`'s own extension contract.

**What is metadata only:** the spec-section-6 template chain in `compiler/ir/forward_chain.py`
(`Δ→Γ→G→L→...`) is a *dependency template*, explicitly documented as "not a proof" — it registers
`OPEN` nodes with no executable backend behind most of them. This is the single most important
distinction the console's Derivation Lab (§IX of the brief) must surface: **template node ≠
executed node**, even when both appear in the same MDCL.

## 6. Falsification & audit machinery

- `compiler/falsification/protocols.py`: 4 protocols (structural elimination, representation
  invariance, mathematical invariance, observer-independent structural reduction) —
  **these are the real originals of RIT/MIT/SEP/OISR**, the acronyms the parallel UOC/DER research
  thread searched for and found `MISSING_SOURCE` in that *other* corpus. They already exist here,
  fully implemented, under this repo's own naming. This is worth flagging explicitly since it
  resolves part of that other investigation's open question, without conflating the two projects.
- `compiler/falsification/target_independence.py`: forbidden-term scanner (`SU(3)`, observed
  masses, DESI, CMB, H0, ...) + role allowlist (`upstream_construction` default vs.
  `validation|comparison|falsification|observational_output`). This is the mechanical enforcement
  of "no downstream structure may be used as an upstream selector."
- `compiler/verification/self_audit.py`: **10** audits (not 8 — `leakage_control_audit` and
  `spectral_validation_audit` were added during the FC-005 extension): `dependency_audit`,
  `circularity_audit` (positive control: synthetic 3-cycle confirmed rejected),
  `type_audit`, `provenance_audit`, `target_independence_audit`, `status_audit`,
  `leakage_control_audit` (no FALSIFIED/FAIL node may be a transitive ancestor of an active
  VERIFIED/DERIVED/CALCULATED node), `numerical_reproducibility_audit` (bitwise re-run
  comparison), `artifact_completeness_audit`, `spectral_validation_audit`.

## 7. Research artifacts already on record (5 prior campaigns, this repository)

1. **Core build** (commits through `9ec8fd4`): compiler skeleton, Test 1/2, self-audit, FC-005
   infrastructure through the sparse N-scaling investigation and checkpoint freeze.
2. **Master Physics Validation Campaign** (`30ddeb4`..`743d902`): clean-room reproduction,
   invariant audit, sign-convention registry, 27-section validation report,
   `MASTER_PHYSICS_CLOSURE_MATRIX.csv`.
3. **L0 literature ingestion** (`bd6349a`, `791d8b0`): historical-corpus audit, string-theory
   literature acquisition (`literature/`), MDCL/branch-recovery/SM/spectral/GR crosswalks.
4. **Master TOE Derivation Campaign** (`84461a2`): full 37-document corpus index, falsification
   report (2 falsified claims: DTC COMPILER.docx's fine-structure-constant and electron-mass
   derivations), partial-closure theorem, `MASTER_THEORY_OF_EVERYTHING.docx/pdf` (concludes no
   TOE derived).
5. **Counterfactual simulation** (`01f70d9`): explicitly labeled fictional alternate-universe
   manuscript + real-vs-fiction gap matrix — never promoted into canonical status.
6. **Master SEIT Theory Derivation Campaign / H1-H4** (`1a3a25e`, current HEAD): real hypothesis
   tests for selection well-posedness (OPEN — undefined, not just unproven), spectral-triple
   locality of `D+=sqrt(L)` (FAIL — structurally non-local), FC-005 kernel-correction candidates
   (FAIL — 2 non-circular corrections tested against real DESI data, ruled out), and the
   G2/Spin(8) gauge-closure claim (FALSIFIED — rank-counting proof). Final manuscript honestly
   titled `SEIT_MASTER_THEORY_CANDIDATE` (not `MASTER_THEORY_OF_EVERYTHING`), per the campaign's
   own naming rule since no branch achieved closure.

An **external, non-committed research thread** (this same chat session, files kept in scratchpad,
never touched this repo) ran two further campaigns not reflected in git history: (a) an
independent literature-research campaign on H1-H4 closure candidates (Hodge-Dirac operators,
NCG spectral triples, causal fermion systems, etc.), and (b) a protocol-recovery/certification
audit of a separate personal document corpus (DER Registry, UOCP/UDP/UCG specs, PDG-001/POL-002,
CVR-001). Neither altered this repository. See §12 for how the console should treat that material.

## 8. FC-005 current state (must not be reopened/relabeled — brief §XXII)

- **Frozen checkpoint**: `FC005_CHECKPOINT.md` — real DESI DR1 LRG SGC catalogue (160,150 points
  post redshift-cut), sparse N-scaling to N=32000→64000.
- **Gate status**: Stage 1 (mathematical convergence) — best case 4 of 15 tested modes converge;
  Stage 2 (curvature closure) and Stage 3 (physical validation) never entered — each is an
  independently gated `stage_gate` IR node (`MATHEMATICAL-CONVERGENCE-DESI`,
  `CURVATURE-CLOSURE-DESI`, `PHYSICAL-VALIDATION-DESI`), all currently `OPEN`.
- **This session's H3 extension** (`run_fc005_h3_correction_test.py`,
  `FC005_H3_CORRECTION_TEST_RESULTS.json`): tested 2 non-circular correction candidates (tighter
  ARPACK tolerance; bandwidth sweep) against the frozen result — both fail to rescue higher-mode
  convergence; a 3rd candidate (curvature-dependent kernel correction) was ruled out analytically
  as circular, never attempted numerically. This **extends**, and does not overwrite, the frozen
  checkpoint.
- Real DESI data lives at `data/desi/dr1/fc005/{raw,derived,validated,metadata}/` with a full
  provenance manifest (`FC005_DESI_CATALOG_MANIFEST.json`, `FC005_DESI_PROVENANCE.json`).
  `FC005_CONTINUUM_FAILURE_MATRIX.csv`, `FC005_N_SCALING_REPORT.md`, `FC005_OPERATOR_LIMIT_
  DIAGNOSTIC.csv`, `FC005_POINT_PROCESS_COMPARISON.csv`, `FC005_SPARSE_SPECTRAL_RESULTS.csv` are
  all real, already-generated diagnostic artifacts the console can surface directly, unmodified.

## 9. CLI entry points (everything currently executable)

```
python3 -m pytest compiler/tests -q          # 95 tests, ~67s
python3 -m compiler.run_compiler              # full rebuild: registries, MDCL, self-audit, workbook, ~seconds
python3 run_fc005_h3_correction_test.py       # standalone; real DESI data; ~66s
python3 run_desi_pilot.py / run_desi_gate1*.py / run_desi_diagnostics.py /
        run_desi_operator_and_knn.py / run_desi_sparse_n_scaling.py /
        run_desi_alpha_normalization.py       # standalone DESI investigation scripts, not
                                               # invoked by run_compiler.py itself, write their
                                               # own artifacts, some multi-minute
download_desi_fc005.py / validate_desi_fc005.py  # data acquisition, one-time
apply_spectral_validation_rule.py             # one-time registry patch script (already applied)
generate_*.py (8 scripts)                     # one-shot report/matrix generators for the 5 prior
                                               # campaigns — NOT part of the regular build; each
                                               # writes specific named artifacts and is not
                                               # idempotent against the live compiler state
```

**No HTTP server, no `package.json`, no frontend code, no API layer exists anywhere in this
repository today.** Node v22.22.2 and Python 3.11.15 are both available in this environment.
`compiler/requirements.txt` has no web framework (numpy/scipy/sympy/openpyxl/pytest/astropy/
requests/fsspec/aiohttp/pyyaml only) — a web framework must be added, not assumed.

## 10. What is executable vs. what is represented as metadata only (the console's central distinction)

| Category | Executable today | Metadata/template only |
|---|---|---|
| Test 1 (graph→L→Spec→heat flow) | YES, full sweep | — |
| Test 2 (Spec→diffusion distance→metric) | YES, full sweep, correctly self-falsifying | — |
| Spec-section-6 template chain (Δ→Γ→G→...) | — | YES (dependency template, explicitly not a proof) |
| FC-005 Stage 1 | YES (real DESI data) | — |
| FC-005 Stage 2/3 | — | YES (`OPEN` stage gates, never entered) |
| H1-H4 closure hypotheses | YES (all 4 executed) | — |
| Historical T2/NCG bridge nodes | — | YES (`PROPOSED`/`OPEN`, `role=comparison`, explicitly never a dependency of fresh construction) |
| Geometry/variational/quantum/gauge/matter/thermodynamic/cosmological "engines" named in spec sections 16-23 | — | NOT YET BUILT — `compiler_architecture.md`'s own "Extending the compiler" section describes the contract for adding these, but none exist yet |

## 11. Missing interfaces required by the UI (the real gap list)

1. **No incremental/partial state API.** `run_compiler.py` always rebuilds everything from
   scratch; there is no function that returns "current state" without a full re-run, and no
   function that executes a single node/branch in isolation. The console's `/api/state`,
   `/api/nodes/:id/execute` etc. need thin **read-only** adapters for state (trivial — just parse
   the JSON files) but the **execution** endpoints (`POST /api/nodes/:id/execute`,
   `/api/derivations/:id/test`) have no backend counterpart to call yet; today "execution" means
   "re-run the whole compiler and diff the result."
2. **No run/session concept.** There is no `RUN-XXXX` identifier, no run history, no snapshot
   versioning anywhere in the compiler. Every `run_compiler.py` invocation overwrites the same
   files in place (confirmed: this reconnaissance's own test run was reverted via `git checkout`
   specifically because there is no other way to "undo" a run).
3. **No hypothesis engine, no research ledger, no literature-search integration, no
   candidate/promotion workflow.** These are pure additions — nothing in the compiler
   contradicts them, but nothing provides even a partial implementation. `H1-SELECTION-
   WELLPOSEDNESS` through `H4-DIRECT-PRODUCT-CLAIM-UNCONSTRUCTED` (in
   `compiler/ir/toe_closure_hypotheses.py`) are the closest existing analogue to a "hypothesis"
   object, but they are hard-coded Python functions, not a general persistent hypothesis registry.
4. **No admissibility/promotion API distinct from re-running the whole compiler.** `Status.
   can_transition()` exists and is real, but nothing currently *calls* it interactively — status
   values are set once, at registration time, inside each `register_*` function, not mutated by
   any live process.
5. **No DER/UOC-corpus integration in this repository at all** (see §1, §12).
