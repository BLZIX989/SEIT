"""FMUTC / SEIT language kernel (Forward-MDCL Universal Theory Compiler,
brief "Proceed with the FMUTC / SEIT executable compiler architecture").

This package is an EXECUTION INTERFACE to the existing mathematics in
`compiler/` and `scientific_corpus/derivation/`. It is not a replacement
ontology and does not re-derive or re-decide any physics. Concretely:

  - It never imports-to-modify, and never writes to, `compiler/core`,
    `compiler/dependencies`, `compiler/backends`, `compiler/falsification`,
    `compiler/verification`, `compiler/ir`, `run_compiler.py`, or any
    canonical registry (equation_registry.json, object_registry.json,
    transformation_registry.json, master_mdcl.json, status_matrix.json,
    calculation_registry.json, provenance_registry.json,
    proof_registry.json, falsification_registry.json,
    chainlink_registry.json, protocol_registry.json).
  - It exposes those existing systems -- the `Status` state machine
    (compiler/core/status.py), the dependency DAG
    (compiler/dependencies/graph.py), and the derivation modules under
    scientific_corpus/derivation/ -- through a `.seit` source language, a
    lexer/parser/AST, a semantic type system, and (eventually) a CLI.

Build order (per the governing brief, Phase 15 -- test incrementally):
  Phase 1  lexer / parser / AST           <- this phase
  Phase 2  semantic type system
  Phase 3  state machine (reconciled with compiler.core.status.Status)
  Phase 4  dependency graph compilation   (reconciled with
                                            compiler.dependencies.graph)
  Phase 5+ physics kernel bindings, CLI, reproducibility, milestone program

Phase 1 status: lexer, parser, AST are implemented
(seit_lang/lexer.py, seit_lang/ast_nodes.py, seit_lang/parser.py). The
formal grammar is documented in seit_lang/GRAMMAR.md. This exact grammar
is NOT asserted to be canonical or final -- it is the working definition
this phase builds and tests against, and later phases may extend it (the
brief's own Phase 16 example program already needs one extension beyond
the literal Phase 1 keyword list -- see GRAMMAR.md).

Phase 2 status: the semantic type system is implemented
(seit_lang/types.py: the brief's fixed 24-type vocabulary plus a minimal
subtype hierarchy; seit_lang/semantic.py: a single-pass type checker that
rejects invalid operations at compile time while leaving calls to
unregistered transformations explicitly Unresolved rather than silently
accepting them). Running the checker against the brief's own literal
Phase 16 milestone example (spectral_test.seit) surfaces a real gap in
that example -- it calls heat_kernel(L, beta) without ever declaring
beta -- which is recorded as an expected, intentional test result
(seit_lang/tests/test_semantic.py) rather than patched silently; a
corrected fixture (spectral_test_complete.seit) exists alongside it.

Phase 3 status: the state machine is implemented (seit_lang/state.py):
SeitState with the brief's 11 states (DECLARED, RESOLVED, CALCULATED,
VERIFIED, DERIVED, CERTIFIED, OPEN, FAILED, FALSIFIED, SUPERSEDED,
BLOCKED), a transition graph that structurally prevents rung-skipping
(CALCULATED cannot jump to DERIVED, VERIFIED cannot jump to CERTIFIED),
bidirectional reconciliation functions with compiler.core.status.Status
that are honest about which mappings are lossy (CERTIFIED and SUPERSEDED
have no compiler-side equivalent; CONDITIONAL and PROPOSED have no
FMUTC-side equivalent) and about a real ordering discrepancy between the
two systems' VERIFIED/DERIVED sequencing (documented in state.py's
module docstring, not silently harmonized), and a SeitStateMachine that
enforces dependency validity by reusing
compiler/dependencies/graph.py's own EXECUTABLE_UPSTREAM_STATUSES
constant rather than redefining what "ready" means.

Phase 4 status: dependency-graph compilation is implemented
(seit_lang/dag.py): compile_dag() walks a checked Program, builds
implicit edges from every derive/calculate/definition/constant/
equation/theorem/lemma/assumption target to the free identifiers in its
expression, adds explicit `dependency` statement edges, and feeds all
of it into a real compiler.dependencies.graph.DependencyGraph (cycle
rejection is the real DependencyGraph's, not reimplemented) while
driving each produced node through seit_lang.state.SeitStateMachine.
Each edge is annotated with source/target/transformation/proof
obligation (cross-referenced from the program's own `verify`
statements, or explicitly marked UNSTATED when none exist)/status/
provenance. Running this against the brief's own milestone example
honestly reports L as BLOCKED, not CALCULATED: B is only ever
`variable`-declared, never assigned a value by any derive/calculate/
definition statement, so it never leaves SeitState.DECLARED -- supplying
real input data is Phase 5's job (physics-kernel bindings), and Phase 4
does not fabricate a placeholder to make the example look further along.

Phase 5 status: physics-kernel primitive bindings are implemented
(seit_lang/primitives.py: real execution semantics for the 7
transformation signatures Phase 2 declared type-only -- transpose,
symmetric, positive_semidefinite, det, norm, spectrum, heat_kernel --
plus 5 new primitives, build_graph/graph_adjacency/graph_laplacian/
spectral_gap/kernel_projector, all bound directly to real
compiler/backends/graph_laplacian.py, spectral.py, and heat_flow.py
functions, never reimplemented) and a value-level evaluator
(seit_lang/evaluate.py: evaluate_program() executes a compiled DAG's
producing statements in topological order with real numpy values). A
program that constructs its own graph (build_graph("cycle", 6); ...)
has no unset leaf inputs and now computes end to end with zero
externally supplied values -- the first genuinely complete Phases-1-5
run in this package. Fixed a real bug caught by writing this test: `*`
between two Matrix-family values must be matrix multiplication (B @ B.T
for the milestone's own `B * transpose(B)`), not numpy's default
elementwise `*`, which would have silently computed the wrong physics.
Running the milestone example itself still honestly raises
UnboundInputError for B when evaluated with no supplied input,
consistent with Phase 4's BLOCKED finding -- and computes correctly once
a real B is supplied.
"""
