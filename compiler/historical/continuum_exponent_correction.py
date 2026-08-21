"""Provenance record for the CONTINUUM-LIMIT-L-DESI exponent correction
(eps^(5/2) -> eps^5), same convention as fc005_reconciliation.py: the
finding is recorded as plain data here, then registered as a real Object
in compiler/ir/fc005.py -- never hand-edited into a JSON registry.

History: `compiler/backends/desi_graph.py::normalize_continuum_limit`
was already corrected, with a full derivation of the fix in its own
docstring, during the real CONTINUUM-LIMIT-L-DESI Gate 1 failure
investigation (see FC005_CONTINUUM_DIAGNOSTIC_REPORT.md, git commit
3d593ad). That correction was never propagated to the CONTINUUM-LIMIT-L-
DESI node's own descriptive label in compiler/ir/fc005.py, so the label
(and everything the compiler generates from it -- object_registry.json,
master_mdcl.json) kept restating the superseded eps^(5/2) exponent even
though the actual executed computation had already moved to eps^5.

This discrepancy was found during an external verification pass over an
uploaded document (CANONICAL_DERIVATION_ARCHITECTURE.md) that itself
asserted the now-superseded eps^(5/2) exponent: cross-checking that claim
against this repository's own code surfaced both (a) the document's
exponent as stale relative to this project's own corrected math, and (b)
this project's own registry label as ALSO stale relative to its own
already-corrected code -- two independent staleness findings from one
comparison, recorded here as a single, honest correction event with a new
node id, per this project's "new claim id, never overwrite an existing
record" discipline.
"""
from __future__ import annotations

CORRECTED_EXPONENT = "eps^(d+2)"
CORRECTED_EXPONENT_D3 = "eps^5"
SUPERSEDED_EXPONENT_D3 = "eps^(5/2)"

ROOT_CAUSE = (
    "The workbook's own kernel definition (EQ-013/DC-002) is K(d^2/eps), i.e. a "
    "LENGTH^2-unit eps, whose matching continuum-normalization exponent is "
    "d/2+1 = 5/2 for d=3. compiler/backends/desi_graph.py::build_kernel_graph instead "
    "implements K(d^2/eps^2) -- a LENGTH-unit eps, the more common convention "
    "(Belkin-Niyogi 2005/2008; Coifman-Lafon 2006; Hein, Audibert & von Luxburg 2007; "
    "Singer 2006). Translating the workbook's length^2-unit exponent to this code's "
    "length-unit eps gives eps^(d+2) = eps^5 for d=3, not eps^(5/2)."
)

# Four locations checked directly by this correction pass; "state" is this
# project's own status at the moment this record's Object is generated
# (i.e. as of the source fix in compiler/ir/fc005.py that accompanies this
# module) -- kept as a fixed historical statement, not re-derived at
# runtime, since it describes what WAS found, not the registries' current
# (now-corrected) content.
LOCATIONS_AUDITED = [
    {"location": "compiler/backends/desi_graph.py::normalize_continuum_limit",
     "exponent_found": CORRECTED_EXPONENT_D3,
     "state_at_discovery": "CORRECT -- already fixed during the CONTINUUM-LIMIT-L-DESI "
                            "Gate 1 failure investigation, with its own derivation in the "
                            "function's docstring."},
    {"location": "object_registry.json (CONTINUUM-LIMIT-L-DESI node, generated)",
     "exponent_found": SUPERSEDED_EXPONENT_D3,
     "state_at_discovery": "STALE -- generated from fc005.py's unpatched label; corrected by "
                            "regenerating from the source fix accompanying this record, never "
                            "hand-edited."},
    {"location": "master_mdcl.json (CONTINUUM-LIMIT-L-DESI node, generated)",
     "exponent_found": SUPERSEDED_EXPONENT_D3,
     "state_at_discovery": "STALE -- same root cause and same fix as object_registry.json."},
    {"location": "compiler/ir/fc005.py (CONTINUUM-LIMIT-L-DESI node label, source)",
     "exponent_found": SUPERSEDED_EXPONENT_D3,
     "state_at_discovery": "STALE -- root cause: this source label was never updated when "
                            "desi_graph.py's normalization was fixed. Corrected in the same "
                            "commit as this record."},
]

DISCOVERY_CONTEXT = (
    "Found during an external verification pass over an uploaded document "
    "(CANONICAL_DERIVATION_ARCHITECTURE.md) that itself asserted the superseded "
    f"{SUPERSEDED_EXPONENT_D3} exponent; cross-checking that claim against "
    "compiler/backends/desi_graph.py's own already-corrected implementation surfaced this "
    "project's own registry/source-label staleness as a second, separate finding."
)
