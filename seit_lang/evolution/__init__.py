"""Numerical evolution kernel (Step 1 of 2, per explicit instruction):
a standalone, independently testable subsystem for numerically
integrating a state forward in time. Zero coupling to seit_lang's
language layer -- no import here touches lexer.py, parser.py,
ast_nodes.py, semantic.py, dag.py, evaluate.py, cli.py, or manifest.py,
and nothing here is registered as a `.seit` primitive.

WHY THIS IS A SEPARATE PACKAGE, NOT A SEIT PRIMITIVE YET: the governing
instruction is explicit -- do not add a generic imperative loop to
`.seit` merely to support numerical simulation, and preserve the
language's declarative, acyclic-DAG semantics. Time-stepping is
inherently iterative (state_{n+1} depends on state_n, repeated N
times), which a strictly acyclic dependency graph cannot express as N
separate named nodes without literally unrolling the loop into N lines
of source -- impractical for any real simulation. So Step 1 (this
package) builds the numerical stepping machinery in plain Python,
verified on its own terms, before Step 2 designs how a *single*
`.seit` value -- a whole Trajectory, produced by one `derive` statement
calling one primitive that loops internally in Python -- can represent
"evolved across space and time" without the DAG itself needing a cycle
or the grammar needing a loop keyword.

Contents:
  - state.py: EvolutionState (a single (t, y) pair) and Trajectory (the
    full recorded history) -- plain dataclasses, no simulation logic.
  - integrators.py: two standard, externally-established fixed-step
    ODE methods (explicit Euler, classic RK4) and evolve(), the
    stepping driver. Nothing here is a new numerical scheme.
  - rhs_library.py: right-hand-side generators for two standard,
    externally-established systems (the discrete heat equation and the
    discrete wave equation on a graph), built on this repo's own real
    compiler.backends.graph_laplacian.laplacian() output -- not new
    physics claims, and not the same object as
    compiler.backends.heat_flow.heat_operator()'s exact closed-form
    solution, which this package's own tests use purely as an external
    correctness reference (see tests/test_correctness_against_exact_solution.py).

"Space" in this package means whatever finite-dimensional structure
the caller's Laplacian/graph already encodes (this project has never
constructed a continuum limit -- see seit_lang/continuum_bridge.py's
own KC-003a/d findings) -- there is no continuum spatial grid or
manifold here, only the same discrete, graph-based objects the rest of
this project already works with.
"""
