# Master TOE Compiler Execution Report

Companion to `MASTER_TOE_COMPILER_EXECUTION_TRACE.json`. Per campaign section 37: the compiler
was actually run, not merely described.

## What was run

```
python3 -m compiler.run_compiler
python3 -m pytest compiler/tests -q
```

Both executed at the start of this campaign (to confirm the baseline inherited from the prior
L0-ST/L0-A commit) and again after the corpus-mining pass (to confirm nothing was disturbed).

## Results

- **Terminal status**: `CONDITIONALLY_CLOSED` — unchanged from before this campaign.
- **Self-audits**: all 10 PASS (`dependency_audit`, `circularity_audit`, `type_audit`,
  `provenance_audit`, `target_independence_audit`, `status_audit`, `leakage_control_audit`,
  `numerical_reproducibility_audit`, `artifact_completeness_audit`, `spectral_validation_audit`).
- **Test suite**: 95 passed, 0 failed.

## Why no new backend was added

This campaign's corpus-mining pass produced two categories of finding: (1) comparison-role
historical nodes recorded in `MASTER_TOE_DEPENDENCY_GRAPH.json` (12 new nodes, none wired as a
canonical dependency), and (2) falsification results recorded in
`MASTER_TOE_FALSIFICATION_REPORT.md`. Per the campaign's own promotion discipline (only promote
after independent derivation, verification, dependency audit, provenance, and falsification), none
of the corpus material survived scrutiny well enough to warrant new canonical code. The one
genuinely new external-mathematics result found (`DTC_Formal_Structure.docx`'s Constraint
Necessity Theorem, and the correct recovery of Noether's theorem as a special case) is pure
category theory / already-established physics, not a new computational backend this compiler
needs to execute — it is recorded in `MASTER_TOE_THEOREM.md`/`MASTER_TOE_THEOREM_PROOF.md`
instead.

## Registry integrity

Running the compiler regenerates `object_registry.json`, `transformation_registry.json`,
`equation_registry.json`, `provenance_registry.json`, `master_mdcl.json`, and the Master
Calculation Workbook with fresh `execution_timestamp`/`git_commit` metadata on every node. Per
this project's established discipline (see `CLEAN_ROOM_REPRODUCTION_REPORT.md` and every prior
L0/campaign phase), these timestamp-only diffs are reverted before commit so the canonical state
stays byte-identical to the pre-campaign commit — confirmed via `git diff` before this campaign's
final commit (see `MASTER_TOE_STATUS.json`, `canonical_registries_modified: false`).
