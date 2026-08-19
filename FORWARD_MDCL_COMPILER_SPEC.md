# Forward-MDCL Universal Theory Compiler — Specification

## What this is

This is an execution and verification system, not a system for assuming
that a desired physical theory exists. It represents mathematical/physical
constructions as a typed intermediate representation (IR), tracks
dependencies as a directed acyclic graph (DAG), assigns each construction
an auditable status, and requires every nontrivial claim to carry
provenance and a failure condition.

**Governing principle:** no downstream structure may be used as an
upstream selector. Observed physics — gauge groups, particle masses,
cosmological parameters — may enter only as an explicitly labeled
validation, comparison, or falsification target, never as an input to an
upstream construction. This is enforced mechanically by the
target-independence firewall (`compiler/falsification/target_independence.py`),
not just asserted in prose.

This build does **not** attempt to derive the Standard Model, General
Relativity, QFT, or cosmology. It builds the compiler and runs the two
initial executable tests the build command specifies, then self-audits.

## Canonical status system

```
VERIFIED | DERIVED | CALCULATED | CONDITIONAL | PROPOSED | OPEN | FAIL | FALSIFIED
```

- `CALCULATED != DERIVED`: a number coming out of code is not a theorem.
- `VERIFIED` numerical reproduction `!= ` theoretical derivation.
- Prose claims in source documents (labels like "CERTIFIED", "PROVEN",
  "DERIVED" written in a `.docx`/`.pdf`) are never taken at face value —
  `compiler/core/status.py::map_legacy_status` maps every such label to
  `PROPOSED` regardless of what the document itself claims. Only an
  executed, provenance-carrying calculation inside this compiler may
  assign `VERIFIED`, `DERIVED`, or `CALCULATED`.
- Legal status transitions are enforced (`compiler/core/status.py`);
  e.g. `FALSIFIED` is terminal, `VERIFIED` cannot silently revert to `OPEN`.

Terminal states for the whole build: `CLOSED | PARTIALLY_CLOSED |
CONDITIONALLY_CLOSED | FALSIFIED`. `CLOSED` is never forced — see
`compiler/run_compiler.py::build_and_run`, which computes the terminal
state from actual audit/status outcomes rather than asserting one.

## Intermediate representation (spec section 8)

Three IR node kinds, all sharing `id`, `status`, `dependencies`,
`assumptions`, `provenance`, and a declared `role` for the
target-independence firewall (`compiler/core/ir.py`):

- **Object**: `type`, `carrier`, `operations`, `relations`, `constraints`.
- **Transformation**: `domain`, `codomain`, `action`, `preconditions`,
  `postconditions`, `proof`.
- **Equation**: `lhs`, `rhs`, `domain`, `derivation`, `verification`.

Every node's `provenance` record (`compiler/core/ir.py::Provenance`)
carries source document/version, dependency ids, git commit, code
version, numerical environment (python/numpy/scipy/sympy versions),
execution timestamp, status, and verification evidence.

## Dependency engine (spec section 9)

`compiler/dependencies/graph.py::DependencyGraph` is a DAG over node ids.
`add_dependency(a, b)` (a depends on b) is rejected with `CycleError` if
it would make `a` an ancestor of `b`. `ExecutionGuard.check(node_id)`
implements the pre-execution protocol: resolve dependencies, verify
every upstream dependency's status is one of
`{VERIFIED, DERIVED, CALCULATED, CONDITIONAL}` (an `OPEN`/`FAIL`/
`FALSIFIED` upstream dependency raises `DependencyError` and stops the
branch — spec sections 5 and 39), verify assumptions are explicit, and
run a full-graph cycle check.

## Selection engine (spec section 10)

`SELECTION-SIGMA` is registered as a `Transformation` with status `OPEN`
and an explicit assumption that no non-arbitrary, unique,
representation-invariant derivation of `Sigma : M -> {0,1}` is registered
in this build. Everything downstream of it in the canonical forward chain
(`compiler/ir/forward_chain.py`) stays `OPEN` as a direct, mechanical
consequence — not an assertion.

## The two initial executable tests

**Test 1** (spec section 31): `graph G -> L = D - A -> Spec(L) -> e^{-tL}
-> P_ker(L)`, swept across 14 (topology, size) cases — path, cycle,
complete, star, 2D grid, Erdos-Renyi — with an exact-arithmetic
(sympy characteristic polynomial) cross-check against the numeric
(`numpy.linalg.eigh`) solver on every graph with ≤ 8 vertices. See
`compiler/backends/pipeline_graph_heatflow.py`.

**Test 2** (spec section 32): `Spec(L) -> diffusion distance -> metric
candidate`, run as a refinement sweep (graph sizes 8→128) at multiple
diffusion-time scales. The construction is explicitly classified —
`approximate | conditional | divergent | non_unique` — and **never**
`exact`; on every topology tested it comes out `non_unique`, because the
limiting nearest-neighbor diffusion distance depends on the arbitrary
diffusion-time parameter. This is registered as a `FalsificationRecord`
(uniqueness is falsified), not swept under the rug. See
`compiler/backends/diffusion_metric.py`.

## Falsification engine (spec section 25)

Four protocols in `compiler/falsification/protocols.py`: structural
elimination, representation invariance, mathematical invariance, and
observer-independent structural reduction. `run_compiler.py` exercises a
concrete representation-invariance test (the Laplacian spectrum of a
10-cycle must not depend on vertex relabeling) and registers the
diffusion-metric non-uniqueness findings from Test 2. Failed
constructions are written to `falsification_registry.json`, not deleted.

## Target-independence firewall (spec section 26)

`compiler/falsification/target_independence.py` scans every registered
node's text fields for a forbidden-term list (`SU(3)`, `SU(2)`, `U(1)`,
observed masses, CKM, PMNS, DESI, CMB, H0, Ω_m, Ω_Λ, ...) and flags any
occurrence whose node role is not one of `validation | comparison |
falsification | observational_output`. The historical T2/NCG nodes
(spec sections 33–34) are registered with role `comparison` specifically
so their necessarily-downstream vocabulary is visible to the scanner but
never counted as upstream contamination — and `run_compiler.py` asserts
no historical node id ever appears in another node's `dependencies` list.

## Historical T2 / NCG bridge (spec sections 33, 34)

`compiler/historical/register.py` registers prior-project claims found in
this repository's source documents as `PROPOSED`/`OPEN` nodes with
explicit provenance, distinct from — and never wired as a dependency of —
any fresh forward construction:

- `T2-HISTORICAL`: the prose claim (DTC COMPILER.docx, README.md) that
  `G_physical = (1,3) x [SU(3) x SU(2) x U(1)]` is "explicitly derived."
  No supporting executable artifact for this claim exists anywhere in the
  repository (audited: every `.docx` converted to text, first pages of
  every `.pdf`, `README.md`, full git log).
- `T2-REPRODUCTION` / `T2-FORWARD-DERIVATION`: `OPEN` — not attempted in
  this build (gauge engine is gated behind the self-audit).
- `NCG-BRIDGE-EXTERNAL-REFERENCE`: the standard (third-party, published)
  Chamseddine–Connes spectral-action result, registered as a comparison
  target, not a SEIT-original derivation.
- `NCG-ABELIAN-BRIDGE-OBSTRUCTION`, `NCG-ASYMMETRIC-ABELIAN-OBSTRUCTION`,
  `NCG-NONABELIAN-COMMUTANT-OBSTRUCTION`: spec section 34 requires these
  be preserved. **No file matching these names or their content was found
  anywhere in the repository during the audit.** They are registered
  `OPEN` with an explicit missing-artifact note rather than fabricated
  (spec section 39: report the exact obstruction, do not patch around it).
- `DTC-CIRCULARITY-OBSTRUCTION`: a genuine, project-internal statement
  found in `DTC_Formal_Structure.docx` §4.2 that pre-dates this compiler
  and independently states the same circularity risk the
  target-independence firewall now enforces mechanically.

## Self-audit (spec section 36)

`compiler/verification/self_audit.py::run_self_audit` runs eight audits —
dependency, circularity (including a positive control: a synthetic
3-cycle is confirmed rejected), type, provenance, target-independence,
status, numerical-reproducibility (bitwise re-run comparison), and
artifact-completeness. Results are written to `self_audit_report.json`.
See `compiler_test_report.md` for the latest run's outcome.

## Reproducing this build

```
pip install -r compiler/requirements.txt
python3 -m pytest compiler/tests -q
python3 -m compiler.run_compiler
```

The second command regenerates every `*_registry.json`, `master_mdcl.json`,
`status_matrix.json`, `self_audit_report.json`, `target_independence.json`,
and `Master Calculation Workbook.xlsx` at the repository root.
