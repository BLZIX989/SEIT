# Compiler Architecture

```
compiler/
  core/
    ir.py            Object, Transformation, Equation, Provenance, IRNode
    status.py        Status enum, legal-transition table, legacy-label mapping
  ir/
    registry.py       ObjectRegistry / TypeRegistry / TransformationRegistry /
                       EquationRegistry / MDCLRegistries (bundle + JSON dump)
    forward_chain.py  spec-section-6 dependency TEMPLATE (Foundation..Observables)
    executable_tests.py  wires Test 1 & Test 2 results into IR nodes
  dependencies/
    graph.py          DependencyGraph (DAG, cycle rejection), ExecutionGuard
  backends/
    graph_laplacian.py    graph construction (7 topologies) + L = D - A
    spectral.py            Spec(L): eigenvalues/vectors/gap/kernel projector
    heat_flow.py            R(t) = e^{-tL}, kernel-convergence hypothesis checks
    pipeline_graph_heatflow.py   Test 1 orchestration + sweep
    diffusion_metric.py     Spec(L) -> diffusion distance -> metric candidate;
                             Test 2 orchestration + refinement sweep
  verification/
    verify.py          symbolic_verify (sympy), numeric_verify, sweep_verify
    self_audit.py       the 8 self-audits (spec section 36)
  falsification/
    protocols.py         4 named falsification protocols (spec section 25)
    target_independence.py  forbidden-term scanner + role allowlist
  provenance/
    provenance.py       Provenance record builder (git commit, env, timestamp)
  historical/
    register.py          T2 / NCG bridge historical nodes (spec sections 33-34)
  workbook/
    build_workbook.py    Master Calculation Workbook.xlsx (16 required sheets)
  tests/
    test_ir_and_status.py
    test_dependency_graph.py
    test_verification.py
    test_falsification.py
    test_pipeline_graph_heatflow.py
    test_pipeline_diffusion_metric.py
    test_run_compiler_integration.py
  run_compiler.py       orchestrator: build MDCL -> run tests -> self-audit -> dump
  requirements.txt
```

## Data flow

```
run_compiler.build_and_run()
  |
  |-- register_template_chain(registries)        # spec section 6 (all OPEN)
  |-- register_executable_tests(registries)       # Test 1 + Test 2, executed
  |     |-- pipeline_graph_heatflow.run_sweep()    -> graph_laplacian, spectral, heat_flow
  |     |-- diffusion_metric.refinement_sweep()    -> spectral, diffusion_metric
  |-- register_historical_nodes(registries)       # spec sections 33-34, role=comparison
  |-- representation_invariance falsification test # spec section 25
  |
  |-- registries.dump_all() -> type/object/transformation/equation_registry.json,
  |                              status_matrix.json
  |-- proof_registry.json, calculation_registry.json, falsification_registry.json,
  |     provenance_registry.json, target_independence.json, master_mdcl.json
  |
  |-- verification.self_audit.run_self_audit()    # 8 audits -> self_audit_report.json
  |-- workbook.build_workbook()                    # Master Calculation Workbook.xlsx
  |
  +-- terminal status: never CLOSED (Sigma remains OPEN) -> CONDITIONALLY_CLOSED
      or PARTIALLY_CLOSED if any audit fails
```

## Why two separate node families exist for the "graph" branch

`compiler/ir/forward_chain.py` registers the full spec-section-6 template
(`FOUNDATION -> ... -> OBSERVABLES-NODE`), which is a dependency
*template*, not a proof, and stays `OPEN` past `SELECTION-SIGMA` because
no admissible selector is registered.

`compiler/ir/executable_tests.py` registers a **separate** branch rooted
at `GRAPH-G-SEED`, a directly postulated mathematical object — exactly
how spec section 31 itself frames the first executable test ("make the
compiler execute: Ø → mathematical object → graph G → ..."). This branch
is executed, verified, and does **not** claim descent from the
still-open Selection/Vacuum chain. Conflating the two would have silently
promoted an OPEN selection problem to CLOSED by fiat, which spec section
5 forbids ("never force CLOSED").

## Extending the compiler

Each backend module is independently testable and has no import-time
side effects; `compiler/run_compiler.py` is the only place that wires
everything together and writes files. To activate the geometry,
variational, quantum, gauge, matter, thermodynamic, or cosmological
engines named in spec sections 16-23, add a new `compiler/backends/*.py`
module following the same shape (pure functions + a dataclass result +
an explicit hypothesis-check before any convergence/correspondence claim
is made), wire its IR registration into `run_compiler.build_and_run`,
and extend `compiler/verification/self_audit.py` if a new audit class is
needed. Do not skip the self-audit gate (spec section 41).
