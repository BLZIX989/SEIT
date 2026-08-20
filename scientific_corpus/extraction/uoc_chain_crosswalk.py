"""UOC_CHAIN_LITERATURE_CROSSWALK (brief section XXII): checks each
object in the target structural chain

    Delta -> Gamma -> G -> L -> Spec(L) -> g_{mu nu} -> nabla -> R
    -> G_{mu nu} -> S -> delta S = 0

against what this repository's real compiler actually implements and
what the extracted literature/discovered-source corpus actually
contains -- never assuming the chain is proved by either. Per brief
section XXXVI: this measures what the sources contain, it does not
force agreement.

Compiler-support lookups are read-only queries against the real,
current status_matrix.json/master_mdcl.json -- exact node ids and
statuses, not remembered/assumed values (checked live at the time this
module was written: SELECTION-SIGMA=OPEN, GRAPH-G-SEED=PROPOSED,
OPERATOR-L=CALCULATED, SPECTRUM-L=VERIFIED, METRIC-CANDIDATE=CONDITIONAL,
CURVATURE-OLLIVIER-RICCI=CALCULATED, SEMICLASSICAL-EINSTEIN-EQUATION=
PROPOSED -- but this module re-reads the live files rather than hard-
coding those, so a future compiler change is reflected automatically).
"""
from __future__ import annotations

from scientific_corpus.extraction.schema import ChainCrosswalkRow

# (chain_position, canonical_object, compiler_node_id_or_None, note_if_no_direct_node)
_CHAIN_COMPILER_MAP = [
    ("1", "Delta (selection functional)", "SELECTION-SIGMA", None),
    ("2", "Gamma (distinction/transformation/constraint composition)", None,
     "no direct compiler IR node; PROTOCOL-GRAPH-SPECTRAL-DERIVATION (protocol_registry.json) "
     "implements the G->L->Spec(L) segment without an explicit Gamma-labeled object"),
    ("3", "G (graph)", "GRAPH-G-SEED", None),
    ("4", "L (graph Laplacian operator)", "OPERATOR-L", None),
    ("5", "Spec(L) (spectrum)", "SPECTRUM-L", None),
    ("6", "g_{mu nu} (metric)", "METRIC-CANDIDATE",
     "compiler's own METRIC-CANDIDATE is a diffusion-distance metric CANDIDATE (never exact, "
     "always non_unique per Test 2) -- not asserted to be a Lorentzian spacetime metric"),
    ("7", "nabla (connection)", None, "no direct compiler IR node"),
    ("8", "R (curvature)", "CURVATURE-OLLIVIER-RICCI",
     "compiler's node is discrete Ollivier-Ricci curvature (Phase 12), a different mathematical "
     "object from the Riemannian scalar curvature R the chain position names -- related by "
     "analogy only, not asserted equivalent"),
    ("9", "G_{mu nu} (Einstein tensor)", "SEMICLASSICAL-EINSTEIN-EQUATION", None),
    ("10", "S (action)", None, "no direct compiler IR node; the compiler has no action-functional backend"),
    ("11", "delta S = 0 (Euler-Lagrange / stationarity)", None,
     "no direct compiler IR node; no variational-calculus backend exists"),
]

# Literature keyword patterns -- checked against each of the 25 real
# string-theory equation records' own MATHEMATICAL_OBJECT/SOURCE_NOTATION
# fields. A hit means the LITERAL text names or notates something in
# this family; it does NOT mean the literature equation is the same
# object as the compiler's chain position (e.g. a string worldsheet
# metric g_{alpha beta} is a different object from spacetime g_{mu nu}
# -- flagged explicitly below, never silently equated).
_CHAIN_LITERATURE_KEYWORDS = {
    "1": [], "2": [], "3": [], "4": [], "5": [],
    "6": ["g_{\\alpha\\beta}", "g_{\\alpha \\beta}", "\\gamma_{\\alpha\\beta}", "metric"],
    "7": ["\\partial_\\alpha", "\\partial_\\beta", "covariant"],
    "8": ["curvature", "R_{", "\\det\\gamma"],
    "9": ["Einstein", "G_{\\mu\\nu}"],
    "10": ["S=", "S =", "S_{NG}", "S_P", "action"],
    "11": ["\\delta L", "Euler", "Lagrange", "e.o.m.", "equation of motion"],
}


def build_uoc_chain_crosswalk(status_matrix: list[dict], literature_items: list[dict],
                               discovered_sources: list[dict]) -> list[ChainCrosswalkRow]:
    status_by_id = {r["id"]: r["status"] for r in status_matrix}
    rows: list[ChainCrosswalkRow] = []

    for position, obj, node_id, note in _CHAIN_COMPILER_MAP:
        if node_id and node_id in status_by_id:
            rows.append(ChainCrosswalkRow(
                chain_position=position, canonical_object=obj, source_id="UOC-COMPILER",
                source_equation_id=None, source_structure_id=node_id,
                relationship="IMPLEMENTED_AS_COMPILER_NODE",
                evidence=f"status_matrix.json: {node_id} status={status_by_id[node_id]}",
                status="COMPILER_ONLY", provenance=note or "",
            ))
        else:
            rows.append(ChainCrosswalkRow(
                chain_position=position, canonical_object=obj, source_id="UOC-COMPILER",
                source_equation_id=None, source_structure_id=None,
                relationship="NOT_IMPLEMENTED", evidence="no matching id in status_matrix.json",
                status="OPEN", provenance=note or "",
            ))

        keywords = _CHAIN_LITERATURE_KEYWORDS.get(position, [])
        lit_hits = 0
        for item in literature_items:
            haystack = f"{item.get('MATHEMATICAL_OBJECT', '')} {item.get('SOURCE_NOTATION', '')}"
            if any(kw in haystack for kw in keywords):
                lit_hits += 1
                rows.append(ChainCrosswalkRow(
                    chain_position=position, canonical_object=obj, source_id=item["SOURCE_ID"],
                    source_equation_id=item["STRING_ITEM_ID"], source_structure_id=None,
                    relationship="KEYWORD_MATCH_LITERAL_TEXT",
                    evidence=f"{item['MATHEMATICAL_OBJECT']} ({item['EQUATION_NUMBER']})",
                    status="SOURCE_SUPPORT",
                    provenance="keyword match against literal source text only -- not a claim "
                               "that this is the SAME object as the compiler's chain position "
                               "(see module docstring on worldsheet vs. spacetime metric etc.)",
                ))
        if lit_hits == 0 and keywords:
            rows.append(ChainCrosswalkRow(
                chain_position=position, canonical_object=obj, source_id="LITERATURE_CORPUS",
                source_equation_id=None, source_structure_id=None,
                relationship="NO_MATCH", evidence="no keyword hit in the 25 extracted "
                "string-theory equations", status="UNRESOLVED",
            ))

        arxiv_hits = 0
        for src in discovered_sources:
            haystack = f"{src.get('title', '')} {src.get('abstract', '')}".lower()
            if any(kw.lower().strip("\\{}") in haystack for kw in keywords if len(kw) > 3):
                arxiv_hits += 1
        rows.append(ChainCrosswalkRow(
            chain_position=position, canonical_object=obj, source_id="ARXIV_DISCOVERY_CORPUS",
            source_equation_id=None, source_structure_id=None,
            relationship="TITLE_ABSTRACT_KEYWORD_MATCH_COUNT",
            evidence=f"{arxiv_hits} of {len(discovered_sources)} discovered sources' "
                     f"title/abstract mention a related keyword",
            status="UNRESOLVED" if arxiv_hits == 0 else "SOURCE_SUPPORT",
            provenance="title/abstract only -- full text was NOT extracted for these sources "
                       "this phase, so this is weak topical evidence, not equation-level support",
        ))

    return rows
