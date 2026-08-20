"""Minimal, keyword-anchored mathematical-structure detection (brief
section XVIII): creates a StructureRecord only when a literature item's
own MATHEMATICAL_OBJECT/DERIVATION_CONTEXT text explicitly names a
structure from the brief's vocabulary -- never inferred from equation
shape alone (brief section XIII: "Do not force category theory onto
ordinary mathematical notation... create a structure record only where
the source provides evidence")."""
from __future__ import annotations

from scientific_corpus.extraction.schema import StructureRecord, stable_id

# (keyword as it might appear in source text, structure_type from brief section XVIII)
_KEYWORD_TO_TYPE = [
    ("Poincare", "LIE_GROUP"),
    ("Virasoro", "ALGEBRA"),
    ("Lie algebra", "LIE_ALGEBRA"),
    ("Lie group", "LIE_GROUP"),
    ("conformal", "MANIFOLD_STRUCTURE"),
    ("worldsheet", "RIEMANNIAN_MANIFOLD"),
    ("Kahler", "MANIFOLD_STRUCTURE"),
    ("Kähler", "MANIFOLD_STRUCTURE"),
]


def extract_structures_from_literature(items: list[dict]) -> list[StructureRecord]:
    structures: list[StructureRecord] = []
    for item in items:
        haystack = f"{item.get('MATHEMATICAL_OBJECT', '')} {item.get('DERIVATION_CONTEXT', '')}"
        for keyword, structure_type in _KEYWORD_TO_TYPE:
            if keyword in haystack:
                equation_id = stable_id("SCIEQ14", item["SOURCE_ID"], str(item["EQUATION_NUMBER"]),
                                         item["STRING_ITEM_ID"])
                structures.append(StructureRecord(
                    structure_id=stable_id("SCISTRUCT", item["SOURCE_ID"], item["STRING_ITEM_ID"], keyword),
                    structure_type=structure_type, source_id=item["SOURCE_ID"],
                    source_location=f"p.{item.get('PAGE', '?')}, eq.{item.get('EQUATION_NUMBER', '?')}",
                    equation_ids=[equation_id], definition=item.get("MATHEMATICAL_OBJECT", "UNKNOWN"),
                    evidence=haystack[:200],
                    provenance=f"literature_item={item['STRING_ITEM_ID']}; keyword_match={keyword!r}",
                ))
    return structures
