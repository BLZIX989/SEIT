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
"""
