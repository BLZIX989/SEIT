# MDCL Dependency Closure Audit

Node-level audit (Part IX) of every Object and Transformation in the live registries.
Raw data: `DEPENDENCY_CLOSURE_AUDIT.csv` (66 rows — one per registered node), produced by
`generate_dependency_closure_audit.py` directly from `object_registry.json` /
`transformation_registry.json`. A complementary branch-level summary (mapping FC-005's
downstream chain specifically) is in `BRANCH_FC005_DEPENDENCY_SUMMARY.csv`.

## Method and a bug found and fixed during this audit

A node "depends on" another via the `dependencies` field in the exported registry JSON.
**An earlier draft of the audit script read a different, wrong key (`dependency_ids`, which
only exists nested inside each node's `provenance` block and is unrelated) and silently
produced an empty dependency graph** — 0 `closed_intermediate` nodes, 0 `blocked` nodes, every
node misclassified as an independent leaf. This was caught by manually cross-checking a known
case (`T-OPERATOR-TO-SPECTRUM` should depend on `OPERATOR-L`) against the raw JSON before
trusting the audit's own output — exactly the discipline this campaign requires of every other
result. Fixed by reading the correct `dependencies` field; the corrected audit is what follows.

## Category counts (66 nodes total: Objects + Transformations combined)

| Category | Count |
|---|---|
| `closed_leaf` (VERIFIED/DERIVED/CALCULATED, nothing depends on it) | 9 |
| `closed_intermediate` (VERIFIED/DERIVED/CALCULATED, has dependents) | 10 |
| `open` | 35 |
| `conditional` | 3 |
| `failed_retriable` (`FAIL`) | 3 |
| `falsified` (node-level `Status.FALSIFIED`) | 0 |
| `proposed` | 6 |
| `superseded` | 0 |
| **`blocked`** (closed-like status but an unresolved ancestor exists) | **15** |

## `falsified: 0` and `superseded: 0` — explained, not omitted

**No Object or Transformation in this compiler carries node-level `Status.FALSIFIED`.** The
two correct, permanent falsifications this project has produced (Fisher-Rao≠Lorentzian,
spectrum-does-not-determine-operator) are tracked in a **separate** registry —
`falsification_registry.json` (`FalsificationRecord` entries, `passed: false`) — not as
`Status.FALSIFIED` IR nodes. This is a real architectural fact, not a gap: falsification
records and node statuses are two different tracking mechanisms in this compiler, and
`leakage_control_audit`'s forbidden-ancestor set (`{FALSIFIED, FAIL}`) checks node status, so
it structurally cannot see falsification-registry entries directly — it relies instead on
those rejected propositions never having been given an active downstream node in the first
place (confirmed true here: neither Fisher-Rao-as-Lorentzian nor the spectrum-determines-
operator claim has any node that inherits from it).

**`Status.SUPERSEDED` does not exist in `compiler/core/status.py`'s `Status` enum at all** —
only `VERIFIED, DERIVED, CALCULATED, CONDITIONAL, PROPOSED, OPEN, FAIL, FALSIFIED`. No node can
carry it by construction. This campaign's instruction anticipated a `SUPERSEDED` category;
this compiler's schema does not implement one. Reported explicitly rather than silently
dropped from the matrix.

## `blocked: 15` — a real, important, non-alarming finding

All 15 blocked nodes belong to exactly two pipelines, blocked by exactly two root nodes:

| Root node | Status | Blocks |
|---|---|---|
| `GRAPH-G-SEED` | `PROPOSED` | `OPERATOR-L`, `SPECTRUM-L`, `HEAT-FLOW-R`, `KERNEL-PROJECTOR`, `DIFFUSION-DISTANCE` (Objects) + `T-GRAPH-TO-OPERATOR`, `T-OPERATOR-TO-SPECTRUM`, `T-SPECTRUM-TO-HEATFLOW`, `T-HEATFLOW-TO-KERNEL`, `T-SPECTRUM-TO-DIFFUSION` (Transformations) — the entire Test 1 / Test 2 pipeline |
| `S3-MANIFOLD` | `PROPOSED` | `S3-SPECTRUM`, `S3-HEAT-TRACE`, `S3-HEAT-COEFFICIENTS`, `S3-CURVATURE-CLOSURE` (Objects) + `T-FC005-S3-CONTROL-CHAIN` (Transformation) — the entire S³ control |

This is not a defect. `compiler/ir/forward_chain.py`'s own module docstring explains it
directly: the executable test branch *"starts from a directly postulated mathematical object
('a graph G'), exactly as the spec's own initial-test instruction frames it, and is NOT
claimed to descend from the (still-open) Selection/Vacuum chain."* `GRAPH-G-SEED` ("a graph
G") and `S3-MANIFOLD` ("the S³ manifold") are honestly registered `PROPOSED` — asserted
starting objects, not derived from anything — precisely so that everything downstream is never
mistaken for having descended from a resolved first-principles selection. This satisfies this
campaign's own governing rule (Part I.1): *"all required upstream dependencies CLOSED or
independently justified as external inputs"* — the postulated starting object is exactly that
kind of declared, non-hidden external input, not a concealed dependency.

**Practical consequence**: no node in this compiler can be honestly described as *fully*
closed in an unconditional, foundation-to-leaf sense — every closed-like result in branches 8
and 9 is closed *conditional on accepting its directly postulated starting object*. This is the
correct, honest state of the project, not a shortfall introduced by this audit.

## The FC-005 chain, seen through this lens

`CONTINUUM-LIMIT-L-DESI`, `DESI-SPECTRUM`, `MATHEMATICAL-CONVERGENCE-DESI` are the three
`failed_retriable` nodes. `DESI-CATALOGUE`, `GRAPH-G-DESI`, `OPERATOR-L-DESI` are
`closed_intermediate` (`CALCULATED`) and — unlike the Test 1/S3 pipelines — **not** blocked:
`DESI-CATALOGUE` has no dependencies (it is itself a directly acquired, real-data root, not a
postulated mathematical object), so the DESI graph-construction chain is closed on its own
terms without an upstream `PROPOSED` gap. The break in the DESI chain is entirely at
`CONTINUUM-LIMIT-L-DESI` itself (frozen `FAIL/RETRIABLE`, per `FC005_CHECKPOINT.md`), not at
any hidden earlier dependency.

## Conclusion

Zero nodes are falsely marked closed. `leakage_control_audit` (which checks the narrower,
correct-for-its-purpose condition — no `FAIL`/`FALSIFIED` ancestor of an active node) continues
to pass, and remains the authoritative build-blocking check; this broader audit is a
supplementary transparency report, not a replacement. The 15 `blocked` nodes are all honestly
and correctly disclosed as conditional on a directly postulated starting object, not a hidden
gap.
