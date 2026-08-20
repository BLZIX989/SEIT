"""Phase 13: Scientific Equation/Variable/Operator Corpus (master brief
section XXXVII: "a provenance-preserving, machine-readable corpus of
established scientific mathematics").

This package is a RESEARCH DATA LAYER, entirely separate from the
compiler (compiler/core, compiler/dependencies, compiler/backends,
compiler/falsification, compiler/verification) and from the canonical
registries at the repository root. Per the master brief's own compiler
integration rule (section XLVIII): this package may be READ by an
adapter later, but it never writes to canonical VERIFIED/DERIVED/
CALCULATED registry state, and nothing here is imported by compiler/.

Scope honesty (this is Phase A + Phase B of the brief's required
execution order, section LII -- nothing past that has been attempted
yet): this first slice ingests ONLY the mathematical content that
already exists in this repository (equation_registry.json,
literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json,
transformation_registry.json, object_registry.json) into the new
corpus schema, with full provenance back to those real sources. It
performs NO new external literature acquisition, NO equivalence
analysis, NO dimensional analysis, NO cross-domain structure detection,
and NO UOC translation analysis -- those are Phases C through O of the
brief and are explicitly out of scope for this slice. See
data/scientific_corpus/coverage/coverage_report.json and
PHASE13_PHASE_A_B_REPORT.md for the exact, measured coverage this slice
actually achieved (never "every equation in science" -- see brief
section II).
"""
