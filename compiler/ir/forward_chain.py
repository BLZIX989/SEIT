"""Canonical forward architecture (spec section 6): a DEPENDENCY TEMPLATE,
not a proof. Every arrow is registered as its own Transformation with its
own status; nothing here is force-closed.

Two branches are kept explicitly separate, per spec sections 10 and 31:

1. The FULL template (Foundation -> ... -> Observables) stays OPEN past
   the Selection node, because Sigma : M -> {0,1} is registered as an
   unresolved compiler component (spec section 10) -- no admissible,
   non-arbitrary derivation of Sigma exists in this build.
2. The EXECUTABLE TEST branch (spec section 31/32) starts from a directly
   postulated mathematical object ("a graph G"), exactly as the spec's own
   initial-test instruction frames it, and is NOT claimed to descend from
   the (still-open) Selection/Vacuum chain. This keeps the executed,
   verified results honest about what they do and do not depend on.
"""
from __future__ import annotations

from compiler.core.ir import Object, Transformation
from compiler.core.status import Status
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

# (id, description) -- the section-6 chain, registered as OPEN objects.
TEMPLATE_CHAIN: list[tuple[str, str]] = [
    ("FOUNDATION", "F0 = (Logic, in, Axioms), parameterizable formal foundation"),
    ("EMPTYSET", "F1 = the empty set, constructed within F0"),
    ("MATH-UNIVERSE", "the mathematical universe M of candidate structures"),
    ("PHYSICAL-CANDIDATE-SET", "P = {M in Mathset | Sigma(M) = 1}"),
    ("VACUUM", "Omega_0, no definition assumed (spec section 11)"),
    ("DISTINCTION", "D(Omega_1, Omega_0)"),
    ("RELATION", "R(Omega_i, Omega_j)"),
    ("TRANSFORMATION-NODE", "f: Omega_i -> Omega_j"),
    ("CONSTRAINT", "C = Adm(T)"),
    ("PERSISTENCE-NODE", "I[Phi_t Omega] = I[Omega]"),
    ("OPERATOR-NODE", "L, derived from D,R,T,C,Pi if admissible (spec section 13)"),
    ("SPECTRUM-NODE", "Spec(L) = {lambda_n}"),
    ("GEOMETRY-NODE", "Spec(L) -> d -> g -> nabla -> Riemann -> Ricci -> ... "),
    ("VARIATIONAL-NODE", "S, delta S = 0, Euler-Lagrange, Hamiltonian"),
    ("QUANTUM-NODE", "Hilbert space, observables, quantization map"),
    ("GAUGE-NODE", "A_mu, F_munu, gauge algebra (never SU(3)xSU(2)xU(1) as input)"),
    ("MATTER-NODE", "fermions, representations, chirality, masses"),
    ("THERMODYNAMICS-NODE", "U, S, Z, F, entropy production"),
    ("COSMOLOGY-NODE", "vacuum energy, Lambda, H, a(t)"),
    ("OBSERVABLES-NODE", "validation-only comparison to observed physics"),
]

TEMPLATE_EDGES: list[tuple[str, str]] = [
    ("EMPTYSET", "FOUNDATION"),
    ("MATH-UNIVERSE", "EMPTYSET"),
    ("PHYSICAL-CANDIDATE-SET", "MATH-UNIVERSE"),  # via Sigma: unresolved (spec 10)
    ("VACUUM", "PHYSICAL-CANDIDATE-SET"),
    ("DISTINCTION", "VACUUM"),
    ("RELATION", "DISTINCTION"),
    ("TRANSFORMATION-NODE", "RELATION"),
    ("CONSTRAINT", "TRANSFORMATION-NODE"),
    ("PERSISTENCE-NODE", "CONSTRAINT"),
    ("OPERATOR-NODE", "PERSISTENCE-NODE"),
    ("SPECTRUM-NODE", "OPERATOR-NODE"),
    ("GEOMETRY-NODE", "SPECTRUM-NODE"),
    ("VARIATIONAL-NODE", "SPECTRUM-NODE"),
    ("QUANTUM-NODE", "VARIATIONAL-NODE"),
    ("GAUGE-NODE", "QUANTUM-NODE"),
    ("MATTER-NODE", "GAUGE-NODE"),
    ("THERMODYNAMICS-NODE", "MATTER-NODE"),
    ("COSMOLOGY-NODE", "THERMODYNAMICS-NODE"),
    ("OBSERVABLES-NODE", "COSMOLOGY-NODE"),
]

SELECTION_NODE_ID = "SELECTION-SIGMA"


def register_template_chain(registries: MDCLRegistries) -> None:
    edge_map: dict[str, list[str]] = {}
    for child, parent in TEMPLATE_EDGES:
        edge_map.setdefault(child, []).append(parent)

    sigma = Transformation(
        id=SELECTION_NODE_ID,
        domain="MATH-UNIVERSE", codomain="PHYSICAL-CANDIDATE-SET",
        action="Sigma : M -> {0,1}",
        status=Status.OPEN,
        role="upstream_construction",
        proof="",
        assumptions=[
            "Registered as an UNRESOLVED compiler component (spec section 10): no "
            "non-arbitrary, unique, representation-invariant derivation of Sigma is "
            "registered in this build. A selector that uses the desired answer is "
            "invalid and none is substituted here.",
        ],
    )
    sigma.provenance = make_provenance(source="spec section 10", transformation_id=sigma.id, status=Status.OPEN)
    registries.transformations.add_transformation(sigma)

    for node_id, description in TEMPLATE_CHAIN:
        deps = edge_map.get(node_id, [])
        obj = Object(
            id=node_id, type="forward_chain_template", status=Status.OPEN,
            role="upstream_construction",
            dependencies=list(deps) + ([SELECTION_NODE_ID] if node_id == "PHYSICAL-CANDIDATE-SET" else []),
            carrier=description,
            assumptions=[
                "Dependency template only (spec section 6): not a proof. Remains OPEN "
                "until its own transformation is independently registered and executed.",
            ],
        )
        obj.provenance = make_provenance(source="spec section 6 (forward architecture template)",
                                          object_id=obj.id, status=Status.OPEN)
        registries.objects.add_object(obj)
