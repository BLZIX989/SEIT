"""Semantic type system for `.seit` (Phase 2). Defines the fixed 24-type
vocabulary given by the FMUTC brief and a minimal subtype hierarchy over
it, used by seit_lang/semantic.py to reject invalid operations at compile
time rather than silently accepting them.

The 24 types (exactly the brief's list, no additions, no omissions):
Scalar, Vector, Matrix, Operator, Graph, IncidenceMatrix, Laplacian,
Spectrum, Eigenvector, Projector, Metric, Connection, Curvature, Tensor,
State, DensityMatrix, Algebra, HilbertSpace, CliffordAlgebra,
SpectralTriple, Functional, Equation, Theorem, Dataset.

Hierarchy design note: the brief lists these as a flat set, but several
are self-evidently specializations of others (an IncidenceMatrix *is* a
Matrix; an Eigenvector *is* a Vector). A flat type system would force
`transpose(Matrix) -> Matrix` to reject `transpose(B)` for `B:
IncidenceMatrix`, which is wrong -- so a minimal subtype tree is added
here. This is a Phase 2 modeling decision (not stated verbatim in the
brief), kept as small as the milestone example and the type list itself
actually justify, not extended speculatively.

`Unresolved` is not one of the 24 -- it is a pseudo-type produced by
seit_lang.semantic for the result of a call to an unregistered
transformation ("unregistered transformations remain unresolved rather
than silently succeeding" -- Phase 2 requirement). It is intentionally
excluded from SEIT_TYPES so a `variable`/`constant`/`primitive`
declaration can never declare something as Unresolved -- only inference
can produce it.
"""
from __future__ import annotations

UNRESOLVED = "Unresolved"

# name -> immediate supertype, or None for a hierarchy root.
TYPE_HIERARCHY: dict[str, str | None] = {
    "Scalar": None,
    "Vector": None,
    "Eigenvector": "Vector",
    "Matrix": None,
    "IncidenceMatrix": "Matrix",
    "Laplacian": "Matrix",
    "Metric": "Matrix",
    "Connection": "Matrix",
    "Curvature": "Matrix",
    "Projector": "Matrix",
    "DensityMatrix": "Matrix",
    "Tensor": None,
    "Graph": None,
    "Spectrum": None,
    "Operator": None,
    "State": None,
    "Algebra": None,
    "CliffordAlgebra": "Algebra",
    "HilbertSpace": None,
    "SpectralTriple": None,
    "Functional": None,
    "Equation": None,
    "Theorem": None,
    "Dataset": None,
}

SEIT_TYPES: frozenset[str] = frozenset(TYPE_HIERARCHY)

assert len(SEIT_TYPES) == 24, "the brief specifies exactly 24 types"


def is_known_type(name: str) -> bool:
    return name in SEIT_TYPES


def ancestors(type_name: str) -> list[str]:
    """Strict ancestor chain, root-exclusive of `type_name` itself,
    e.g. ancestors("IncidenceMatrix") == ["Matrix"]."""
    if type_name not in TYPE_HIERARCHY:
        raise KeyError(f"unknown type {type_name!r}")
    chain = []
    current = TYPE_HIERARCHY[type_name]
    while current is not None:
        chain.append(current)
        current = TYPE_HIERARCHY[current]
    return chain


def is_subtype(sub: str, sup: str) -> bool:
    """True if `sub` is `sup` or a (transitive) specialization of `sup`."""
    return sub == sup or sup in ancestors(sub)


def comparable(a: str, b: str) -> bool:
    """True if `a` and `b` are on the same root-to-leaf chain (one is an
    ancestor-or-equal of the other), in either direction. Used for
    declaration/assignment compatibility (`variable L: Laplacian; derive
    L = <expr proving only Matrix>;` is allowed -- the specific-subtype
    claim is a VERIFIED-later matter, not a type error) and for +/-
    operand compatibility."""
    return is_subtype(a, b) or is_subtype(b, a)


def widen(a: str, b: str) -> str:
    """The common, more general type of two comparable types (the one
    that is an ancestor-or-equal of the other). Raises ValueError if a
    and b are not comparable -- callers must check `comparable` first."""
    if is_subtype(a, b):
        return b
    if is_subtype(b, a):
        return a
    raise ValueError(f"{a!r} and {b!r} are not comparable")
