"""Phase 12: Protocol / Derivation Chainlink Execution Layer.

This package sits ABOVE the existing compiler (compiler/core, compiler/ir,
compiler/backends, compiler/falsification) -- it never replaces, weakens,
or bypasses any of it. Everything here is a read-only PROJECTION over IR
nodes, Transformations, and FalsificationRecords the compiler has already
registered and executed elsewhere; nothing in this package can independently
set a node's canonical Status (see compiler/core/status.py::can_transition,
the one place canonical status is ever assigned).

Scope note: the historical UOCP_Formal_Registry.docx / UDP whitepaper / UCG
Specification v5 / DER Registry v1/v2 source documents referenced by this
project's prior research are NOT present in this repository (confirmed
against source_material/ and RESEARCH_CONSOLE_REPOSITORY_MAP.md section 1 --
that corpus was supplied in a separate, parallel research thread and was
explicitly never committed here). Every Chainlink/Protocol record in this
package that would normally cite historical source text instead carries an
explicit `source_document_status` of "MISSING_SOURCE" -- never a fabricated
recovery.
"""
