"""Decomposes literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json
(25 real records, already extracted with page/section/equation-number
provenance and real LaTeX in an earlier phase -- see that file's own
EXTRACTION_TIMESTAMP/SOURCE_STATUS fields) into the Phase 14 equation/
variable/operator/relation registries. This is genuine EXACT_LATEX
extraction quality: the LaTeX itself was already transcribed by a human/
AI reading the actual PDF pages in a prior phase, not re-derived here --
what THIS module adds is the structural decomposition (symbol/operator/
relation occurrences) that Phase 13's ingestion never attempted.

The STRING-ITEM's own SOURCE_STATUS field ("textbook-established",
"derived from (1.1)...", etc.) is preserved verbatim in provenance;
this module never converts it into a stronger claim (brief section
XXXIV/XXXV: source occurrence != derivation != proof != validation).
"""
from __future__ import annotations

from scientific_corpus.extraction.schema import (
    ChainCrosswalkRow, EquationRecord, OperatorOccurrence, RelationRecord,
    ReviewItem, SymbolOccurrence, stable_id,
)
from scientific_corpus.extraction.tokenizer import (
    extract_bracket_relations, extract_operators, extract_symbols,
)


def _relation_type(bracket: dict) -> str:
    if bracket["subscript"].replace("_", "").strip("{}") == "PB":
        return "POISSON_BRACKET"
    if bracket["open"] == "\\{":
        return "ANTICOMMUTATOR"
    if bracket["open"] == "[":
        return "COMMUTATOR"
    return "UNRESOLVED"


def extract_from_literature_registry(items: list[dict]) -> tuple[
    list[EquationRecord], list[SymbolOccurrence], list[OperatorOccurrence],
    list[RelationRecord], list[ReviewItem],
]:
    equations: list[EquationRecord] = []
    variables: list[SymbolOccurrence] = []
    operators: list[OperatorOccurrence] = []
    relations: list[RelationRecord] = []
    review: list[ReviewItem] = []

    for item in items:
        source_id = item["SOURCE_ID"]
        location = f"p.{item.get('PAGE', '?')}, eq.{item.get('EQUATION_NUMBER', '?')}"
        equation_id = stable_id("SCIEQ14", source_id, str(item["EQUATION_NUMBER"]),
                                 item["STRING_ITEM_ID"])
        latex = item["SOURCE_NOTATION"]

        eq = EquationRecord(
            equation_id=equation_id, source_id=source_id, source_version=None,
            document_id=source_id, location=location, page=str(item.get("PAGE")),
            section=item.get("SECTION"), equation_label=str(item.get("EQUATION_NUMBER")),
            extraction_method="LATEX_SOURCE", extraction_quality="EXACT_LATEX",
            source_status="SOURCE_EXTRACTED", exact_representation=latex,
            surrounding_text=item.get("DERIVATION_CONTEXT", "UNKNOWN"),
            assumptions=[item["ASSUMPTIONS"]] if item.get("ASSUMPTIONS") else [],
            provenance=(
                f"literature_item={item['STRING_ITEM_ID']}; "
                f"mathematical_object={item.get('MATHEMATICAL_OBJECT', 'UNKNOWN')}; "
                f"source_status_verbatim={item.get('SOURCE_STATUS', 'UNKNOWN')}"
            ),
        )

        # Multiple equations are sometimes packed into one SOURCE_NOTATION
        # string separated by ";" (the literature registry's own convention,
        # e.g. ST-003, ST-012) -- tokenize each clause separately so a
        # symbol/operator's location stays attributable within the record,
        # while the equation record itself keeps the exact combined text.
        clauses = [c.strip() for c in latex.split(";") if c.strip()]

        eq_vars: list[SymbolOccurrence] = []
        eq_ops: list[OperatorOccurrence] = []
        for clause in clauses:
            eq_vars.extend(extract_symbols(clause, equation_id, source_id, location, "LATEX_SOURCE"))
            eq_ops.extend(extract_operators(clause, equation_id, source_id, location, "LATEX_SOURCE"))
            for bracket in extract_bracket_relations(clause):
                rtype = _relation_type(bracket)
                rel = RelationRecord(
                    relation_id=stable_id("SCIREL", source_id, equation_id, bracket["matched_text"]),
                    relation_type=rtype, lhs=bracket["lhs"], rhs=bracket["rhs"],
                    source_id=source_id, equation_id=equation_id,
                    provenance=f"detected in clause: {clause[:80]}",
                )
                relations.append(rel)
                if rtype == "UNRESOLVED":
                    review.append(ReviewItem(
                        review_id=stable_id("REV", equation_id, bracket["matched_text"]),
                        equation_id=equation_id, issue="AMBIGUOUS_BRACKET_RELATION_TYPE",
                        source_location=location, machine_proposal=str(bracket),
                        unresolved_question="bracket shape does not clearly indicate "
                                             "COMMUTATOR/ANTICOMMUTATOR/POISSON_BRACKET",
                    ))

        # dedupe within this equation (a symbol appearing in 2 clauses of
        # the same packed equation is still one occurrence for this record)
        eq_vars_by_symbol = {v.literal_symbol: v for v in eq_vars}
        eq_ops_by_symbol = {o.symbol: o for o in eq_ops}
        eq.variable_ids = [v.variable_id for v in eq_vars_by_symbol.values()]
        eq.operator_ids = [o.operator_id for o in eq_ops_by_symbol.values()]

        equations.append(eq)
        variables.extend(eq_vars_by_symbol.values())
        operators.extend(eq_ops_by_symbol.values())

        if len(eq.variable_ids) == 0 and len(eq.operator_ids) == 0:
            review.append(ReviewItem(
                review_id=stable_id("REV", equation_id, "no_tokens"),
                equation_id=equation_id, issue="NO_SYMBOLS_OR_OPERATORS_DETECTED",
                source_location=location, machine_proposal="(none)",
                unresolved_question="tokenizer found nothing extractable in this equation's LaTeX",
            ))

    return equations, variables, operators, relations, review
