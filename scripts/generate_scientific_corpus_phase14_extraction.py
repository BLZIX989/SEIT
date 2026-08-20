"""Phase 14 (master brief): the mathematical extraction layer. Runs
against the REAL corpus Phase 13 produced -- the 25-item literature
registry (already-extracted, real LaTeX) and the 10 PDFs Phase 13 C/D
actually acquired from the live arXiv API. No synthetic data substitutes
for the real corpus (synthetic equations are used only in this repo's
test suite, never written into these registries).

--output-root works exactly as in scripts/generate_scientific_corpus_
phase_cd.py: default is the real repository, tests override it to an
isolated tmp_path so no test run can touch real data or canonical state.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.extraction.literature_extractor import extract_from_literature_registry
from scientific_corpus.extraction.pdf_extractor import extract_pdf_review_candidates
from scientific_corpus.extraction.structure_extractor import extract_structures_from_literature
from scientific_corpus.extraction.uoc_chain_crosswalk import build_uoc_chain_crosswalk

LITERATURE_REGISTRY_PATH = ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json"
STATUS_MATRIX_PATH = ROOT / "status_matrix.json"
DISCOVERED_SOURCES_PATH = ROOT / "data" / "scientific_corpus" / "sources" / "discovery" / "SCIENTIFIC_SOURCE_DISCOVERY_REGISTRY.jsonl"
RAW_PDF_DIR = ROOT / "data" / "scientific_corpus" / "sources" / "raw"

CANONICAL_FILES = [
    "equation_registry.json", "transformation_registry.json", "object_registry.json",
    "master_mdcl.json", "self_audit_report.json", "chainlink_registry.json",
    "protocol_registry.json", "status_matrix.json", "provenance_registry.json",
    "falsification_registry.json", "proof_registry.json", "calculation_registry.json",
]


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _write_jsonl(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r.to_dict(), sort_keys=True) + "\n")


def _write_csv_and_xlsx(records: list, fieldnames: list[str], csv_path: Path, xlsx_path: Path,
                         sheet_name: str) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [r.to_dict() for r in records]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = {k: (";".join(v) if isinstance(v, list) else v) for k, v in row.items()}
            writer.writerow(flat)

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(fieldnames)
    for row in rows:
        ws.append([";".join(row[k]) if isinstance(row.get(k), list) else row.get(k, "") for k in fieldnames])
    wb.save(xlsx_path)


def main(*, output_root: Path = ROOT, max_pdf_pages: int = 10, max_pdfs: int | None = None) -> dict:
    corpus_dir = output_root / "data" / "scientific_corpus"

    literature_items = json.loads(LITERATURE_REGISTRY_PATH.read_text())
    status_matrix = json.loads(STATUS_MATRIX_PATH.read_text())
    discovered_sources = _read_jsonl(DISCOVERED_SOURCES_PATH)

    equations, variables, operators, relations, review = extract_from_literature_registry(literature_items)
    structures = extract_structures_from_literature(literature_items)

    pdf_stats = {}
    pdf_files = sorted(RAW_PDF_DIR.glob("*.pdf"))
    if max_pdfs is not None:
        pdf_files = pdf_files[:max_pdfs]
    for pdf_path in pdf_files:
        items, stats = extract_pdf_review_candidates(pdf_path, pdf_path.stem, max_pages=max_pdf_pages)
        review.extend(items)
        pdf_stats[pdf_path.stem] = stats

    crosswalk = build_uoc_chain_crosswalk(status_matrix, literature_items, discovered_sources)

    equations_dir = corpus_dir / "equations"
    variables_dir = corpus_dir / "variables"
    operators_dir = corpus_dir / "operators"
    relations_dir = corpus_dir / "relations"
    structures_dir = corpus_dir / "structures"
    crosswalk_dir = corpus_dir / "crosswalk"
    review_dir = corpus_dir / "review"
    for d in (equations_dir, variables_dir, operators_dir, relations_dir, structures_dir,
              crosswalk_dir, review_dir):
        d.mkdir(parents=True, exist_ok=True)

    _write_jsonl(equations, equations_dir / "equation_registry.jsonl")
    _write_jsonl(variables, variables_dir / "variable_registry.jsonl")
    _write_jsonl(operators, operators_dir / "operator_registry.jsonl")
    _write_jsonl(relations, relations_dir / "relation_registry.jsonl")
    _write_jsonl(structures, structures_dir / "structure_registry.jsonl")

    eq_fields = ["equation_id", "source_id", "source_version", "document_id", "location", "page",
                 "section", "equation_label", "extraction_method", "extraction_quality",
                 "source_status", "exact_representation", "surrounding_text", "variable_ids",
                 "operator_ids", "structure_ids", "assumptions", "dimensional_information",
                 "provenance", "equation_hash"]
    _write_csv_and_xlsx(equations, eq_fields, output_root / "SCIENTIFIC_EQUATION_CORPUS.csv",
                        output_root / "SCIENTIFIC_EQUATION_CORPUS.xlsx", "equations")

    var_fields = ["variable_id", "equation_id", "literal_symbol", "local_definition", "role",
                  "mathematical_type", "source_id", "source_location", "extraction_method", "confidence"]
    _write_csv_and_xlsx(variables, var_fields, output_root / "SCIENTIFIC_VARIABLE_CORPUS.csv",
                        output_root / "SCIENTIFIC_VARIABLE_CORPUS.xlsx", "variables")

    op_fields = ["operator_id", "equation_id", "symbol", "source_id", "source_location", "definition",
                 "extraction_method", "confidence", "algebraic_properties"]
    _write_csv_and_xlsx(operators, op_fields, output_root / "SCIENTIFIC_OPERATOR_CORPUS.csv",
                        output_root / "SCIENTIFIC_OPERATOR_CORPUS.xlsx", "operators")

    struct_fields = ["structure_id", "structure_type", "source_id", "source_location",
                      "equation_ids", "definition", "evidence", "provenance"]
    _write_csv_and_xlsx(structures, struct_fields, output_root / "SCIENTIFIC_STRUCTURE_CORPUS.csv",
                        output_root / "SCIENTIFIC_STRUCTURE_CORPUS.xlsx", "structures")

    crosswalk_fields = ["chain_position", "canonical_object", "source_id", "source_equation_id",
                         "source_structure_id", "relationship", "evidence", "status", "provenance"]
    _write_csv_and_xlsx(crosswalk, crosswalk_fields, output_root / "UOC_CHAIN_LITERATURE_CROSSWALK.csv",
                        output_root / "UOC_CHAIN_LITERATURE_CROSSWALK.xlsx", "crosswalk")

    review_csv = output_root / "EXTRACTION_REVIEW_QUEUE.csv"
    review_fields = ["review_id", "equation_id", "issue", "source_location", "machine_proposal",
                      "unresolved_question", "status"]
    with review_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=review_fields)
        writer.writeheader()
        for r in review:
            writer.writerow(r.to_dict())

    relations_fieldnames_for_xlsx = ["relation_id", "relation_type", "lhs", "rhs", "source_id",
                                      "equation_id", "assumptions", "provenance"]
    _write_csv_and_xlsx(relations, relations_fieldnames_for_xlsx,
                        relations_dir / "relation_registry.csv", relations_dir / "relation_registry.xlsx",
                        "relations")

    return {
        "equations": equations, "variables": variables, "operators": operators,
        "relations": relations, "structures": structures, "crosswalk": crosswalk,
        "review": review, "pdf_stats": pdf_stats, "n_literature_sources": len(
            {i["SOURCE_ID"] for i in literature_items}),
        "n_pdf_documents": len(pdf_files), "n_discovered_sources": len(discovered_sources),
    }


def write_reports(result: dict, output_root: Path) -> None:
    eq = result["equations"]
    review = result["review"]
    pdf_review = [r for r in review if r.issue == "PDF_TEXT_CANDIDATE_NOT_STRUCTURED"]
    lit_review = [r for r in review if r.issue != "PDF_TEXT_CANDIDATE_NOT_STRUCTURED"]

    by_method = {}
    by_quality = {}
    for e in eq:
        by_method[e.extraction_method] = by_method.get(e.extraction_method, 0) + 1
        by_quality[e.extraction_quality] = by_quality.get(e.extraction_quality, 0) + 1

    crosswalk_by_status = {}
    for row in result["crosswalk"]:
        crosswalk_by_status[row.status] = crosswalk_by_status.get(row.status, 0) + 1

    lines = [
        "# Phase 14: Mathematical Extraction Layer",
        "",
        "Governing principle enforced throughout: EXTRACT FIRST, INTERPRET SECOND, VALIDATE THIRD, "
        "PROMOTE LAST. Nothing in this phase performs semantic equivalence, canonicalization, "
        "cross-domain unification, UOC translation, theorem promotion, or physical validation.",
        "",
        "## Counts",
        "",
        f"- Sources processed: {result['n_literature_sources']} literature sources "
        f"(LIT-TONG-ST, LIT-KIRITSIS-SST) + {result['n_pdf_documents']} acquired PDF documents",
        f"- Documents processed: {result['n_literature_sources'] + result['n_pdf_documents']}",
        f"- Equations extracted: {len(eq)} (all from the literature registry -- PDF text extraction "
        "produced review-queue candidates only, never structured equation records; see below)",
        f"- Variables extracted: {len(result['variables'])}",
        f"- Operators extracted: {len(result['operators'])}",
        f"- Relations extracted: {len(result['relations'])}",
        f"- Structures extracted: {len(result['structures'])}",
        f"- Review queue total: {len(review)} ({len(lit_review)} literature-side ambiguities, "
        f"{len(pdf_review)} PDF-text candidate equation lines not promoted to structured records)",
        f"- Requiring human review: {len(review)} (100% of review-queue items -- none were "
        "auto-resolved)",
        "",
        "## Extraction methods used",
        "",
    ]
    for method, count in sorted(by_method.items()):
        lines.append(f"- {method}: {count}")
    lines += ["", "## Extraction quality", ""]
    for quality, count in sorted(by_quality.items()):
        lines.append(f"- {quality}: {count}")

    lines += [
        "",
        "## PDF extraction (real pypdf text extraction against the 10 real Phase 13 C/D PDFs)",
        "",
        f"- Pages processed per document (capped): {list(result['pdf_stats'].values())[0]['pages_processed'] if result['pdf_stats'] else 0} "
        "or fewer (min of 10-page cap and actual page count)",
        f"- Candidate equation-bearing lines found: {len(pdf_review)}",
        "- None of these were converted into equation_registry.jsonl records: rendered PDF text "
        "has no reliable LaTeX/MathML structure, so promoting them would mean fabricating "
        "confidence this phase does not have (brief section VII). All are in EXTRACTION_REVIEW_QUEUE.csv.",
        "",
        "## UOC chain literature crosswalk",
        "",
    ]
    for status, count in sorted(crosswalk_by_status.items()):
        lines.append(f"- {status}: {count} rows")
    lines += [
        "",
        "Full detail in UOC_CHAIN_LITERATURE_CROSSWALK.csv/.xlsx. Summary: of the chain's 11 "
        "positions, this repository's compiler directly implements 6 as real IR nodes (Delta, G, "
        "L, Spec(L), a metric CANDIDATE, and a discrete curvature analogue); Gamma, nabla, S, and "
        "delta S = 0 have no direct compiler node. The 25-equation string-theory literature corpus "
        "supports the action-functional position (S) directly (Nambu-Goto/Polyakov actions) but "
        "its worldsheet metric is explicitly NOT claimed equivalent to the chain's spacetime "
        "g_{mu nu}, and its discrete curvature analogue is explicitly NOT claimed equivalent to "
        "Riemannian scalar curvature R -- both flagged in the crosswalk's own provenance field "
        "rather than silently conflated.",
        "",
        "## Canonical compiler status",
        "",
        "UNCHANGED. This phase reads status_matrix.json read-only for the UOC chain crosswalk and "
        "writes nothing to any canonical registry (see brief section XXVIII; verified by a real "
        "subprocess test comparing every canonical file's bytes before and after a full extraction "
        "run).",
        "",
        "## Test status",
        "",
        "See commit message / PHASE14_EXTRACTION_AUDIT.json for exact pass counts at commit time.",
        "",
        "## What this phase does NOT claim",
        "",
        "- It does not claim these are \"all equations in physics\" or even all equations in the "
        "acquired PDFs -- see brief section II/XXVII. Coverage is exactly: the 25 literature "
        "equations already transcribed in a prior phase, plus PDF-text candidate lines from the "
        "first 10 pages of 10 real acquired papers.",
        "- Source occurrence is not mathematical derivation, formal proof, or empirical validation "
        "(brief section XXXIV). Every equation record's source_status is SOURCE_EXTRACTED, never "
        "VERIFIED.",
        "- A repeated equation is not a theorem; a mathematically-plausible equivalence is not a "
        "canonical identity -- no equivalence analysis was attempted (Phase 15+, not started).",
    ]
    (output_root / "PHASE14_EXTRACTION_REPORT.md").write_text("\n".join(lines) + "\n")

    provenance = {
        "phase": "Phase 14: Mathematical Extraction Layer",
        "sources": {
            "literature_registry": str(LITERATURE_REGISTRY_PATH.relative_to(ROOT)),
            "pdf_documents": [p for p in result["pdf_stats"].keys()],
            "status_matrix_snapshot": str(STATUS_MATRIX_PATH.relative_to(ROOT)),
        },
        "counts": {
            "equations": len(eq), "variables": len(result["variables"]),
            "operators": len(result["operators"]), "relations": len(result["relations"]),
            "structures": len(result["structures"]), "review_queue": len(review),
            "crosswalk_rows": len(result["crosswalk"]),
        },
        "extraction_methods": by_method, "extraction_quality": by_quality,
        "pdf_extraction_stats": result["pdf_stats"],
    }
    (output_root / "PHASE14_PROVENANCE.json").write_text(json.dumps(provenance, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--max-pdf-pages", type=int, default=10)
    parser.add_argument("--max-pdfs", type=int, default=None)
    args = parser.parse_args()

    result = main(output_root=args.output_root, max_pdf_pages=args.max_pdf_pages, max_pdfs=args.max_pdfs)
    write_reports(result, args.output_root)
    print(f"equations={len(result['equations'])} variables={len(result['variables'])} "
          f"operators={len(result['operators'])} relations={len(result['relations'])} "
          f"structures={len(result['structures'])} review={len(result['review'])} "
          f"crosswalk_rows={len(result['crosswalk'])}")
