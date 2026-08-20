"""Registers the Protocol-level records (master brief section XVII).

Two protocols, both wrapping code that already exists and already runs --
no new physics, no new claims, just formal metadata over what is real:

1. GRAPH-SPECTRAL-DERIVATION: the executable G -> L -> Spec(L) -> R(t) ->
   P_ker(L) and Spec(L) -> diffusion-distance -> metric-candidate chain
   (compiler/backends/pipeline_graph_heatflow.py,
   compiler/backends/diffusion_metric.py), represented as the 6 real
   Chainlinks plus the honest METRIC-CANDIDATE -> CONNECTION frontier
   entry from derivation_chainlinks.py.

2. STRUCTURAL-FALSIFICATION: the 4 real falsification protocols in
   compiler/falsification/protocols.py. The project's historical research
   thread (outside this repository) searched an external corpus for
   protocols named SEP/RIT/MIT/OISR and found MISSING_SOURCE there; this
   registers the plain fact, already noted in
   RESEARCH_CONSOLE_REPOSITORY_MAP.md section 6, that this repository's
   own falsification protocols already implement those same four
   conceptual tests (structural elimination / representation invariance /
   mathematical invariance / observer-independent structural reduction)
   under this repository's own naming -- without claiming this *is* the
   historical SEP/RIT/MIT/OISR specification, since that specification's
   source text is not available here.
"""
from __future__ import annotations

from compiler.protocol.registry import ChainlinkRegistry, ProtocolRegistry
from compiler.protocol.schema import Protocol


def build_protocol_registry(chainlinks: ChainlinkRegistry) -> ProtocolRegistry:
    reg = ProtocolRegistry()

    reg.add(Protocol(
        protocol_id="PROTOCOL-GRAPH-SPECTRAL-DERIVATION",
        version="1.0.0",
        name="Graph -> Laplacian -> Spectrum -> Heat Flow / Diffusion Metric",
        purpose=(
            "Execute the portion of the project's conceptual G -> L -> Spec(L) -> "
            "g_mu_nu chain (master brief section VI) that this compiler can "
            "actually run today, and stop honestly at the first real obstruction."
        ),
        inputs=["a graph G=(V,E) (7 topologies swept, see DEFAULT_SWEEP)"],
        assumptions=["G is directly postulated (spec section 31), not claimed to descend "
                     "from the still-OPEN Selection/Vacuum template chain"],
        primitives=["graph G", "Laplacian L", "spectral decomposition Spec(L)"],
        operators=["D - A", "eigh", "expm", "diffusion-distance kernel"],
        algorithm="see compiler/backends/pipeline_graph_heatflow.py::run_sweep and "
                  "compiler/backends/diffusion_metric.py::refinement_sweep",
        outputs=["OPERATOR-L", "SPECTRUM-L", "HEAT-FLOW-R", "KERNEL-PROJECTOR",
                 "DIFFUSION-DISTANCE", "METRIC-CANDIDATE"],
        invariants=["L @ ones = 0 (EQ-LAPLACIAN-ROW-SUM-ZERO, proved symbolically)",
                    "spectrum invariant under vertex relabeling (FALS-SPECTRUM-RELABELING-INVARIANCE)"],
        proof_obligations=["symbolic proof for L@1=0", "numeric verification with exact "
                            "cross-check (n<=8) for the eigen-equation"],
        falsification_criteria=["representation_invariance_test on Spec(L) under relabeling",
                                 "structural_elimination_protocol on metric-candidate uniqueness"],
        literature=[],
        execution_backend="compiler/backends/pipeline_graph_heatflow.py, "
                           "compiler/backends/diffusion_metric.py",
        chainlinks=[c.chainlink_id for c in chainlinks],
        admissibility_conditions=["EXECUTABLE_UPSTREAM_STATUSES per node "
                                   "(compiler/dependencies/graph.py)"],
        failure_modes=["numeric residual exceeds tolerance", "metric classified non_unique/divergent",
                        "no admissible connection construction registered (current frontier)"],
        registry_bindings=["object_registry.json", "transformation_registry.json",
                            "equation_registry.json", "falsification_registry.json"],
        source_document_status="N/A",
        provenance_note="Wraps only code and results that already existed and already executed "
                         "before Phase 12; Phase 12 added no new numerical claims here, only "
                         "this formal Chainlink/Protocol representation of what was already real.",
    ))

    reg.add(Protocol(
        protocol_id="PROTOCOL-STRUCTURAL-FALSIFICATION",
        version="1.0.0",
        name="Structural Elimination / Representation Invariance / Mathematical Invariance / "
             "Observer-Independent Structural Reduction",
        purpose="The compiler's real falsification machinery (spec section 25).",
        inputs=["a candidate construction (callable) plus the data needed to probe it"],
        assumptions=[],
        primitives=["candidate structure", "predicate", "representation set", "invariant function"],
        operators=["structural_elimination_protocol", "representation_invariance_test",
                   "mathematical_invariance_test", "observer_independent_structural_reduction"],
        algorithm="see compiler/falsification/protocols.py",
        outputs=["FalsificationRecord"],
        invariants=[],
        proof_obligations=[],
        falsification_criteria=["see each protocol's own docstring in "
                                 "compiler/falsification/protocols.py"],
        literature=[],
        execution_backend="compiler/falsification/protocols.py",
        chainlinks=[],
        admissibility_conditions=[],
        failure_modes=["candidate not uniquely selected (SEP)",
                       "invariant differs across representations (RIT)",
                       "invariant broken under an admissible transformation (MIT)",
                       "construction closes over an undeclared observer-dependent input (OISR)"],
        registry_bindings=["falsification_registry.json"],
        source_document_status="MISSING_SOURCE",
        provenance_note=(
            "The project's historical research (outside this repository) refers to protocols "
            "named SEP/RIT/MIT/OISR; that historical specification text is not present in this "
            "repository (see compiler/protocol/__init__.py and "
            "RESEARCH_CONSOLE_REPOSITORY_MAP.md section 6). This registers the fact -- already "
            "noted in that reconnaissance document -- that this repository's own, independently "
            "implemented falsification protocols already realize the same four conceptual tests "
            "under this repository's own naming. This is NOT presented as a recovery of the "
            "historical SEP/RIT/MIT/OISR source text."
        ),
    ))

    return reg
