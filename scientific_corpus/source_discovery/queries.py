"""Discovery query registry (brief section VI). Queries are built around
mathematical structures, not vague topics, and are explicitly weighted
toward the structural targets the existing UOC/SEIT dependency graph
actually needs (brief section XV) -- graph theory, Laplacians, spectral
theory, differential geometry, curvature, variational calculus, gauge
theory, Lie algebras, Clifford algebras, Dirac operators, quantum
operators, statistical mechanics, information geometry, category/functor
structures -- plus general coverage of the domain list in section III.

This is NOT claimed to be an exhaustive query set (brief section VI:
"Do not claim the query set is exhaustive").
"""
from __future__ import annotations

from scientific_corpus.source_discovery.schema import DiscoveryQuery

# (domain, subdomain, structure_target, query_text, acquisition_priority)
# priority 1 = directly addresses a structure the existing UOC/SEIT
# dependency graph needs (brief section XV); priority 3 = general domain
# coverage (brief section III/XVII), not yet needed by an existing
# compiler node.
_QUERY_SPECS: list[tuple[str, str, str, str, int]] = [
    ("mathematics", "spectral graph theory", "graph Laplacian spectrum",
     "graph Laplacian spectral decomposition", 1),
    ("mathematics", "spectral graph theory", "Laplacian geometry",
     "Laplacian spectrum graph geometry", 1),
    ("mathematics", "noncommutative geometry", "spectral triple",
     "spectral triple Dirac operator noncommutative geometry", 1),
    ("mathematics", "information geometry", "Fisher-Rao metric",
     "Fisher information Riemannian metric statistical manifold", 1),
    ("mathematics", "Lie theory", "gauge structure constants",
     "Lie algebra gauge theory structure constants", 1),
    ("physics", "Hamiltonian mechanics", "symplectic Poisson structure",
     "Hamiltonian symplectic manifold Poisson bracket", 1),
    ("physics", "variational field theory", "Euler-Lagrange field equations",
     "Euler Lagrange variational field theory", 1),
    ("mathematics", "differential geometry", "Einstein tensor curvature",
     "Einstein tensor differential geometry curvature", 1),
    ("physics", "gauge theory", "Yang-Mills connection curvature",
     "Yang Mills curvature connection principal bundle", 1),
    ("mathematics", "Clifford algebra", "Dirac operator spin geometry",
     "Clifford algebra Dirac operator spin geometry", 1),
    ("mathematics", "Hodge theory", "Hodge Laplacian differential forms",
     "Hodge Laplacian differential forms", 1),
    ("mathematics", "category theory", "functor mathematical physics",
     "category theory functor mathematical physics", 1),
    ("physics", "quantum mechanics", "operator algebra commutator",
     "operator algebra quantum mechanics commutator", 1),
    ("physics", "statistical mechanics", "partition function free energy",
     "partition function statistical mechanics free energy", 1),
    ("mathematics", "spectral graph theory", "graph Laplacian eigen-decomposition",
     "graph Laplacian spectral decomposition heat kernel", 1),
    ("physics", "classical mechanics", "Newtonian to Lagrangian formulation",
     "Newtonian mechanics Lagrangian formulation review", 3),
    ("physics", "electromagnetism", "Maxwell equations differential forms",
     "Maxwell equations differential forms gauge", 3),
    ("physics", "general relativity", "Einstein field equations",
     "Einstein field equations general relativity review", 3),
    ("physics", "quantum field theory", "canonical quantization path integral",
     "quantum field theory canonical quantization path integral", 3),
    ("physics", "Standard Model", "SU(3) SU(2) U(1) gauge group",
     "Standard Model gauge group SU(3) SU(2) U(1) representation", 3),
    ("mathematics", "operator theory", "self-adjoint spectral theorem",
     "self-adjoint operator spectral theorem Hilbert space", 3),
    ("mathematics", "probability", "stochastic process generator",
     "Markov process generator Fokker-Planck spectral gap", 3),
    ("physics", "condensed matter", "tight-binding graph spectrum",
     "tight binding lattice graph spectral theory", 3),
    ("mathematics", "algebraic topology", "homology cohomology chain complex",
     "homology cohomology chain complex boundary operator", 3),
]

def build_query_registry() -> list[DiscoveryQuery]:
    queries = []
    for i, (domain, subdomain, target, text, _priority) in enumerate(_QUERY_SPECS, start=1):
        queries.append(DiscoveryQuery(
            query_id=f"QUERY-{i:03d}", domain=domain, subdomain=subdomain,
            structure_target=target, query_text=text, database="arxiv_api",
        ))
    return queries


def query_priorities() -> dict[str, int]:
    """Pure, order-independent mapping of query_id -> acquisition_priority."""
    return {f"QUERY-{i:03d}": priority for i, (*_rest, priority) in enumerate(_QUERY_SPECS, start=1)}
