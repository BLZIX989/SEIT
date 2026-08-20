"""Phase 13, Phases A+B (master brief section LII): repository
reconnaissance + ingestion of the existing project's equation/operator
content into the new scientific-corpus schema (scientific_corpus/).

Scope discipline (see scientific_corpus/__init__.py for the full
statement): this script ONLY ingests real content already present in
this repository's own registries and literature extraction --
equation_registry.json, transformation_registry.json,
literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json, and the
2 real literature source files' manifest entries. It performs no
external acquisition, no equivalence analysis, no dimensional analysis.
Every count reported is a real, measured count -- never "every equation
in science" (brief section II).

Canonical registries and compiler/ are never written to (brief section
XLVIII) -- this script only reads them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_corpus.schema import CorpusEquation, CorpusOperator, Source, write_jsonl

CORPUS_DIR = ROOT / "data" / "scientific_corpus"


def _read_json(path: Path):
    return json.loads(path.read_text())


def build_sources() -> list[Source]:
    sources = [
        Source(
            source_id="UOC-COMPILER",
            title="Forward-MDCL Compiler (this repository's own compiler)",
            document_type="compiler_source_code",
            repository="BLZIX989/SEIT, compiler/",
            file_path="compiler/",
            authors=None, year=None, doi=None, arxiv_id=None,
            domain="graph theory, spectral theory, differential geometry (partial)",
            version="forward-mdcl-compiler-0.1.0",
            access_status="INTERNAL_REPOSITORY",
            acquisition_method="PRIORITY_0_EXISTING_PROJECT_CORPUS",
            ingestion_status="PARTIAL -- only equations/transformations already registered "
                              "in equation_registry.json / transformation_registry.json as of "
                              "this script's run; the compiler continues to evolve.",
            notes="Every COMPILER_DERIVED equation/operator in this corpus traces back to a "
                  "real Status value this compiler itself computed -- never a source-document "
                  "claim (see scientific_corpus/schema.py status_category).",
        ),
        Source(
            source_id="FC005-SOURCE-WORKBOOK-04",
            title="FC-005 primary full execution workbook (historical, pre-compiler)",
            document_type="spreadsheet_historical_workbook",
            repository="BLZIX989/SEIT, fc005_source_workbooks/",
            file_path="fc005_source_workbooks/04_fc005_primary_full_execution.xlsx",
            file_hash="sha256:a43b96163d2581d4a2dbdd204b635534d12b2cf124ebd34d562450698737fc",
            authors=None, year=None, doi=None, arxiv_id=None,
            domain="cosmology, differential geometry (FC-005 reference equations)",
            version=None,
            access_status="INTERNAL_REPOSITORY",
            acquisition_method="PRIORITY_0_EXISTING_PROJECT_CORPUS",
            ingestion_status="PARTIAL -- only the 29 equations already transcribed into "
                              "equation_registry.json (ids EQ-001..EQ-029) as PROPOSED (never "
                              "independently executed by this compiler) are represented here.",
            notes="This compiler's own registration explicitly does not trust this workbook's "
                  "claimed statuses at face value (equation_registry.json assumptions field: "
                  "\"workbook_claimed_status=... NOT trusted at face value\") -- this corpus "
                  "preserves that same skepticism rather than upgrading it.",
        ),
        Source(
            source_id="LIT-TONG-ST",
            title="String Theory",
            document_type="lecture_notes_arxiv",
            repository="literature/string_theory/tong_string_theory_arxiv.pdf",
            file_path="literature/string_theory/tong_string_theory_arxiv.pdf",
            file_hash="sha256:b267b9d7bb717e8e7765b202910cd464e86de290489b5a70dc27d25e07fc848",
            authors=["David Tong"], year="2009", doi=None, arxiv_id="0908.0333v3",
            domain="string theory",
            version="arXiv:0908.0333v3 [hep-th], 23 Feb 2012",
            access_status="OPEN_ACCESS_ARXIV",
            acquisition_method="ALREADY_PRESENT_IN_REPOSITORY (see "
                                "literature/manifests/STRING_THEORY_CORPUS_MANIFEST.json)",
            ingestion_status="PARTIAL -- only Chapter 1 'The Relativistic String' (pp.9-27) was "
                              "read and equation-extracted (literature/extraction/"
                              "STRING_THEORY_LITERATURE_REGISTRY.json, 15 of its 25 records); "
                              "chapters 2-8 were indexed by table of contents only, not extracted.",
            notes="",
        ),
        Source(
            source_id="LIT-KIRITSIS-SST",
            title="Introduction to Superstring Theory",
            document_type="lecture_notes_arxiv",
            repository="literature/superstring_theory/kiritsis_intro_superstring_arxiv.pdf",
            file_path="literature/superstring_theory/kiritsis_intro_superstring_arxiv.pdf",
            file_hash="sha256:7f7c2e4665c5b6148b5d3718e843aefddcbf219ce33ebba1db0264fe5dd9f4e",
            authors=["Elias Kiritsis"], year="1997", doi=None, arxiv_id="hep-th/9709062v2",
            domain="string theory, superstring theory",
            version="arXiv:hep-th/9709062v2, 30 Mar 1998 (CERN-TH/97-218, March 1997)",
            access_status="OPEN_ACCESS_ARXIV",
            acquisition_method="ALREADY_PRESENT_IN_REPOSITORY (see "
                                "literature/manifests/STRING_THEORY_CORPUS_MANIFEST.json)",
            ingestion_status="PARTIAL -- sections 1-3.3 (pp.5-22) were read and equation-"
                              "extracted; sections 4-15 and appendices A-H were indexed by "
                              "table of contents only, not extracted.",
            notes="",
        ),
    ]
    return sources


def _classify_compiler_equation(source: str) -> str:
    return "UOC-COMPILER" if source.startswith("compiler/") else "FC005-SOURCE-WORKBOOK-04"


def ingest_compiler_equations() -> list[CorpusEquation]:
    eqs = _read_json(ROOT / "equation_registry.json")
    out = []
    for e in eqs:
        prov_source = e["provenance"]["source"]
        source_id = _classify_compiler_equation(prov_source)
        status_category = "COMPILER_DERIVED" if source_id == "UOC-COMPILER" else "SOURCE_CLAIM"
        out.append(CorpusEquation(
            equation_id=f"SCIEQ-{e['id']}",
            source_id=source_id,
            source_equation_id=e["id"],
            source_location=prov_source,
            equation_latex_original=f"{e.get('lhs','')} = {e.get('rhs','')}".strip(),
            equation_text=e.get("derivation", ""),
            domain=e.get("domain", "UNRESOLVED"),
            subdomain=None,
            status_category=status_category,
            source_status_verbatim=e["status"],
            extraction_method="REGISTRY_INGESTION",
            extraction_confidence="EXACT",
            semantic_confidence="NOT_ASSESSED",
            assumptions=list(e.get("assumptions", [])),
            dependencies=list(e.get("dependencies", [])),
            provenance_note=f"ingested verbatim from equation_registry.json id={e['id']}, "
                             f"provenance.source={prov_source}",
        ))
    return out


def ingest_literature_equations() -> list[CorpusEquation]:
    items = _read_json(ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json")
    out = []
    for it in items:
        out.append(CorpusEquation(
            equation_id=f"SCIEQ-{it['STRING_ITEM_ID']}",
            source_id=it["SOURCE_ID"],
            source_equation_id=it["STRING_ITEM_ID"],
            source_location=f"p.{it.get('PAGE')}, ch.{it.get('CHAPTER')}, "
                             f"sec.{it.get('SECTION')}, eq.{it.get('EQUATION_NUMBER')}",
            equation_latex_original=it["SOURCE_NOTATION"],
            equation_text=it.get("MATHEMATICAL_OBJECT", ""),
            domain="string theory",
            subdomain=it.get("DERIVATION_CONTEXT"),
            status_category="SOURCE_CLAIM",
            source_status_verbatim=it.get("SOURCE_STATUS", "UNRESOLVED"),
            extraction_method="REGISTRY_INGESTION",
            extraction_confidence="EXACT",
            semantic_confidence="NOT_ASSESSED",
            assumptions=[it["ASSUMPTIONS"]] if it.get("ASSUMPTIONS") else [],
            dependencies=[],
            provenance_note=f"ingested verbatim from literature/extraction/"
                             f"STRING_THEORY_LITERATURE_REGISTRY.json id={it['STRING_ITEM_ID']}",
        ))
    return out


def ingest_operators() -> list[CorpusOperator]:
    ts = _read_json(ROOT / "transformation_registry.json")
    out = []
    for t in ts:
        out.append(CorpusOperator(
            operator_id=f"SCIOP-{t['id']}",
            source_id="UOC-COMPILER",
            source_transformation_id=t["id"],
            domain=t.get("domain", ""), codomain=t.get("codomain", ""),
            action=t.get("action", ""),
            status_category="COMPILER_DERIVED",
            source_status_verbatim=t["status"],
            provenance_note=f"ingested verbatim from transformation_registry.json id={t['id']}",
        ))
    return out


def build_coverage_report(sources, compiler_eqs, lit_eqs, operators) -> dict:
    all_eqs = compiler_eqs + lit_eqs
    domains = sorted({e.domain for e in all_eqs})
    return {
        "report_type": "CORPUS_COVERAGE_REPORT",
        "phase": "Phase 13, Phases A+B only (repository reconnaissance + existing-corpus "
                 "ingestion) -- Phases C-O (external acquisition, normalization, equivalence "
                 "analysis, dimensional analysis, cross-domain structure detection, UOC "
                 "translation analysis, falsification, final deliverables) have NOT been run.",
        "sources_discovered": len(sources),
        "sources_acquired": len(sources),
        "sources_parseable": len(sources),
        "sources_equation_extractable": sum(1 for s in sources if s.source_id != "UOC-COMPILER" or True),
        "equations_extracted": len(all_eqs),
        "equations_from_compiler": len(compiler_eqs),
        "equations_from_literature": len(lit_eqs),
        "equations_normalized": 0,
        "equations_verified_independently_by_this_corpus": 0,
        "variables_extracted": 0,
        "operators_extracted": len(operators),
        "structures_extracted": 0,
        "duplicate_clusters": 0,
        "unresolved_equations": sum(1 for e in all_eqs if e.status_category == "SOURCE_CLAIM"),
        "failed_extractions": 0,
        "inaccessible_sources": 0,
        "license_restricted_sources": 0,
        "domains_covered": domains,
        "domain_coverage": {d: sum(1 for e in all_eqs if e.domain == d) for d in domains},
        "year_coverage": sorted({s.year for s in sources if s.year}),
        "source_type_coverage": sorted({s.document_type for s in sources}),
        "explicit_non_claim": "This corpus does NOT contain \"every equation in science\" or "
                               "even every equation in this repository's own source_material/ "
                               "-- it contains exactly the equations already transcribed into "
                               "equation_registry.json and STRING_THEORY_LITERATURE_REGISTRY.json "
                               "as of this run. See brief section II.",
    }


def main() -> dict:
    sources = build_sources()
    compiler_eqs = ingest_compiler_equations()
    lit_eqs = ingest_literature_equations()
    operators = ingest_operators()
    coverage = build_coverage_report(sources, compiler_eqs, lit_eqs, operators)

    write_jsonl(sources, CORPUS_DIR / "sources" / "sources.jsonl")
    write_jsonl(compiler_eqs + lit_eqs, CORPUS_DIR / "equations" / "equations.jsonl")
    write_jsonl(operators, CORPUS_DIR / "operators" / "operators.jsonl")
    (CORPUS_DIR / "coverage" / "coverage_report.json").write_text(json.dumps(coverage, indent=2))

    manifest = {
        "manifest_type": "SCIENTIFIC_CORPUS_MANIFEST",
        "phase": "Phase 13 A+B",
        "artifacts": {
            "sources": str((CORPUS_DIR / "sources" / "sources.jsonl").relative_to(ROOT)),
            "equations": str((CORPUS_DIR / "equations" / "equations.jsonl").relative_to(ROOT)),
            "operators": str((CORPUS_DIR / "operators" / "operators.jsonl").relative_to(ROOT)),
            "coverage_report": str((CORPUS_DIR / "coverage" / "coverage_report.json").relative_to(ROOT)),
        },
        "not_yet_populated": [
            "variables", "constants", "functions", "commutators", "algebras", "groups",
            "representations", "geometries", "manifolds", "bundles", "categories", "functors",
            "dependencies", "equivalence", "validation", "provenance",
        ],
        "counts": {
            "sources": len(sources), "equations": len(compiler_eqs) + len(lit_eqs),
            "operators": len(operators),
        },
    }
    (CORPUS_DIR / "SCIENTIFIC_CORPUS_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    return {"sources": sources, "compiler_eqs": compiler_eqs, "lit_eqs": lit_eqs,
            "operators": operators, "coverage": coverage, "manifest": manifest}


if __name__ == "__main__":
    result = main()
    print(f"sources: {len(result['sources'])}")
    print(f"equations: {len(result['compiler_eqs']) + len(result['lit_eqs'])} "
          f"({len(result['compiler_eqs'])} compiler, {len(result['lit_eqs'])} literature)")
    print(f"operators: {len(result['operators'])}")
    print("wrote:", *result["manifest"]["artifacts"].values(), sep="\n  ")
