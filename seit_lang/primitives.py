"""Physics-kernel primitive bindings for `.seit` (Phase 5): connects
`.seit` transformation names to the REAL, already-established Python
implementations in compiler/backends -- read-only imports, no
reimplementation of established calculations, per the brief's own
"expose existing physics modules ... as compiler primitives without
rewriting established calculations."

Scope note: this phase deliberately covers only the GENERIC graph /
Laplacian / spectrum / heat-kernel pipeline (compiler/backends/
graph_laplacian.py, spectral.py, heat_flow.py) plus basic linear
algebra. It does NOT reach into scientific_corpus/derivation/
dirac_candidates.py (incidence-matrix/Clifford constructions -- that is
Phase 6's explicit job), persistence.py (Phase 7), kc003_vr001.py
(Phase 8), ko_dimension.py (Phase 9), clifford_derivation.py
(Phase 10), or gauge_rank.py (Phase 11). Reaching further here would
duplicate scope those later phases own.

Two kinds of primitives are registered:

1. Real execution semantics for the exact 7 transformation signatures
   already DECLARED (type-only, unbound to any implementation) by
   seit_lang.semantic.BUILTIN_TRANSFORMATIONS in Phase 2: transpose,
   symmetric, positive_semidefinite, det, norm, spectrum, heat_kernel.
   Their param/return .seit types are copied 1:1 from
   BUILTIN_TRANSFORMATIONS -- checked equal by a test in this phase's
   test suite, not silently redefined (Phase 2's own docstring warns
   against exactly that). `spectrum` and `heat_kernel` are bound
   directly to the REAL compiler.backends.spectral.spectrum and
   compiler.backends.heat_flow.heat_operator functions. `transpose`/
   `symmetric`/`positive_semidefinite`/`det`/`norm` are basic linear
   algebra (not a physics-specific established RESULT the way the
   spectral/heat-kernel machinery is), implemented directly with numpy;
   `symmetric`'s tolerance (atol=1e-10) and `positive_semidefinite`'s
   tolerance (>= -1e-8) are copied from compiler/backends/heat_flow.py's
   own verify_kernel_convergence() conventions, not independently
   chosen numbers.

2. NEW primitives compiler/backends/ already implements but no `.seit`
   program has ever been able to call: build_graph and graph_adjacency
   (compiler.backends.graph_laplacian), graph_laplacian
   (compiler.backends.graph_laplacian.laplacian), spectral_gap and
   kernel_projector (methods on compiler.backends.spectral.SpectralData).

Deliberately NOT bound: compiler.backends.heat_flow.
verify_kernel_convergence -- its real signature takes a `t_values` list
keyword argument, and the Phase 1 `.seit` grammar has no list-literal
syntax to express one. Binding it with a fabricated single-value
substitute would misrepresent the real function's contract; this is
left unbound and documented rather than faked. A future grammar
extension adding list literals would be the honest way to unblock it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from compiler.backends import graph_laplacian as _graph_laplacian_module
from compiler.backends import heat_flow as _heat_flow_module
from compiler.backends import spectral as _spectral_module

from .semantic import BUILTIN_TRANSFORMATIONS, TransformationSignature


@dataclass(frozen=True)
class PrimitiveBinding:
    name: str
    param_types: list[str]
    return_type: str
    fn: Callable[..., Any]
    source: str  # dotted path to the real implementation, for provenance


def _symmetric(M: np.ndarray) -> bool:
    return bool(np.allclose(M, M.T, atol=1e-10))  # tolerance from heat_flow.py's own convention


def _positive_semidefinite(M: np.ndarray) -> bool:
    return bool(np.all(np.linalg.eigvalsh(M) >= -1e-8))  # tolerance from heat_flow.py's own convention


def _build_graph(topology: str, n: float) -> _graph_laplacian_module.Graph:
    return _graph_laplacian_module.build_graph(topology, int(n))


_BINDINGS_LIST: list[PrimitiveBinding] = [
    # -- Phase 2's 7 pre-declared signatures, now with real execution --
    PrimitiveBinding("transpose", ["Matrix"], "Matrix",
                      lambda M: np.asarray(M).T, "numpy.ndarray.T"),
    PrimitiveBinding("symmetric", ["Matrix"], "Scalar",
                      _symmetric, "numpy (tolerance per compiler/backends/heat_flow.py)"),
    PrimitiveBinding("positive_semidefinite", ["Matrix"], "Scalar",
                      _positive_semidefinite, "numpy (tolerance per compiler/backends/heat_flow.py)"),
    PrimitiveBinding("det", ["Matrix"], "Scalar",
                      lambda M: float(np.linalg.det(M)), "numpy.linalg.det"),
    PrimitiveBinding("norm", ["Vector"], "Scalar",
                      lambda v: float(np.linalg.norm(v)), "numpy.linalg.norm"),
    PrimitiveBinding("spectrum", ["Matrix"], "Spectrum",
                      _spectral_module.spectrum, "compiler.backends.spectral.spectrum"),
    PrimitiveBinding("heat_kernel", ["Matrix", "Scalar"], "Operator",
                      _heat_flow_module.heat_operator, "compiler.backends.heat_flow.heat_operator"),
    # -- new primitives compiler/backends/ already implements --
    PrimitiveBinding("build_graph", ["Scalar", "Scalar"], "Graph",
                      _build_graph, "compiler.backends.graph_laplacian.build_graph"),
    PrimitiveBinding("graph_adjacency", ["Graph"], "Matrix",
                      lambda g: g.adjacency(), "compiler.backends.graph_laplacian.Graph.adjacency"),
    PrimitiveBinding("graph_laplacian", ["Matrix"], "Laplacian",
                      _graph_laplacian_module.laplacian, "compiler.backends.graph_laplacian.laplacian"),
    PrimitiveBinding("spectral_gap", ["Spectrum"], "Scalar",
                      lambda s: s.spectral_gap, "compiler.backends.spectral.SpectralData.spectral_gap"),
    PrimitiveBinding("kernel_projector", ["Spectrum"], "Projector",
                      lambda s: s.kernel_projector(), "compiler.backends.spectral.SpectralData.kernel_projector"),
]

PHYSICS_KERNEL_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}

PHYSICS_KERNEL_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}

# The 7 signatures shared with Phase 2 must match BUILTIN_TRANSFORMATIONS
# EXACTLY -- enforced here at import time, not left to a test to
# eventually notice, since a silent mismatch would mean the type
# checker and the evaluator disagree about what a call means.
for _name in BUILTIN_TRANSFORMATIONS:
    assert PHYSICS_KERNEL_TRANSFORMATIONS[_name] == BUILTIN_TRANSFORMATIONS[_name], (
        f"seit_lang.primitives redefines {_name!r} away from "
        f"seit_lang.semantic.BUILTIN_TRANSFORMATIONS -- not allowed, see module docstring")
