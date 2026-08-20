"""Phase 14 audits (brief section XXXI). Runs real checks against the
registries scripts/generate_scientific_corpus_phase14_extraction.py just
produced -- never suppresses a failure to present a clean report (brief:
"Any failure must remain visible. Do not suppress failures to achieve a
clean report.").
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CORPUS_DIR = ROOT / "data" / "scientific_corpus"
CANONICAL_FILES = [
    "equation_registry.json", "transformation_registry.json", "object_registry.json",
    "master_mdcl.json", "self_audit_report.json", "chainlink_registry.json",
    "protocol_registry.json", "status_matrix.json",
]


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def audit_source_provenance(equations, variables, operators, relations, structures) -> dict:
    """Every record type carries its provenance in different fields by
    design (EquationRecord/RelationRecord/StructureRecord have an
    explicit `provenance` string; SymbolOccurrence/OperatorOccurrence
    instead carry `source_location` + `extraction_method`, since they
    are occurrence-level records, not top-level entities -- see
    scientific_corpus/extraction/schema.py). This audit checks each
    record type against its OWN real provenance-carrying fields, not a
    single field name assumed uniform across all five record types
    (an earlier version of this audit did that and produced 54 false
    positives against every real operator record -- a bug in the audit,
    not the extraction data)."""
    missing = []
    for label, records, id_field, required_fields in (
        ("equation", equations, "equation_id", ("source_id", "provenance")),
        ("variable", variables, "variable_id", ("source_id", "source_location", "extraction_method")),
        ("operator", operators, "operator_id", ("source_id", "source_location", "extraction_method")),
        ("relation", relations, "relation_id", ("source_id", "provenance")),
        ("structure", structures, "structure_id", ("source_id", "provenance")),
    ):
        for r in records:
            if any(not r.get(f) for f in required_fields):
                missing.append(f"{label}:{r.get(id_field)}")
    return {"passed": len(missing) == 0, "issues": missing[:20], "n_issues": len(missing)}


def audit_extraction_completeness(equations, literature_items) -> dict:
    lit_ids = {i["STRING_ITEM_ID"] for i in literature_items}
    covered = {e["provenance"].split("literature_item=")[1].split(";")[0]
               for e in equations if "literature_item=" in e.get("provenance", "")}
    missing = lit_ids - covered
    return {"passed": len(missing) == 0, "missing_literature_items": sorted(missing)}


def audit_determinism() -> dict:
    from scientific_corpus.extraction.literature_extractor import extract_from_literature_registry
    items = json.loads((ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json").read_text())
    a = extract_from_literature_registry(items)
    b = extract_from_literature_registry(items)
    equal = all(
        [x.to_dict() for x in ga] == [x.to_dict() for x in gb] for ga, gb in zip(a, b)
    )
    return {"passed": equal}


def audit_duplicates(equations, variables, operators, relations, structures) -> dict:
    dupes = {}
    for label, records, key in (
        ("equation", equations, "equation_id"), ("variable", variables, "variable_id"),
        ("operator", operators, "operator_id"), ("relation", relations, "relation_id"),
        ("structure", structures, "structure_id"),
    ):
        ids = [r[key] for r in records]
        seen = set()
        local_dupes = [i for i in ids if i in seen or seen.add(i)]
        if local_dupes:
            dupes[label] = local_dupes
    return {"passed": len(dupes) == 0, "duplicates": dupes}


def audit_symbol_collision(variables) -> dict:
    """No two DIFFERENT literal symbols within the same equation may
    share a variable_id (a hash collision would silently merge them)."""
    by_id: dict[str, set[str]] = {}
    for v in variables:
        by_id.setdefault(v["variable_id"], set()).add((v["equation_id"], v["literal_symbol"]))
    collisions = {vid: list(pairs) for vid, pairs in by_id.items()
                  if len({sym for _eq, sym in pairs}) > 1}
    return {"passed": len(collisions) == 0, "collisions": collisions}


def audit_operator_references(equations, operators) -> dict:
    operator_ids = {o["operator_id"] for o in operators}
    missing = []
    for e in equations:
        for oid in e.get("operator_ids", []):
            if oid not in operator_ids:
                missing.append((e["equation_id"], oid))
    return {"passed": len(missing) == 0, "missing_operator_refs": missing[:20]}


def audit_relation_references(equations, relations) -> dict:
    equation_ids = {e["equation_id"] for e in equations}
    missing = [r["relation_id"] for r in relations if r["equation_id"] not in equation_ids]
    return {"passed": len(missing) == 0, "orphan_relations": missing}


def audit_dimensional_metadata(equations) -> dict:
    """Every equation must carry an honest, non-fabricated dimensional
    status -- this phase never invented a dimension for anything."""
    bad = [e["equation_id"] for e in equations if e.get("dimensional_information") != "NOT_EXTRACTED"]
    return {"passed": len(bad) == 0, "equations_with_fabricated_dimensions": bad}


def audit_canonical_isolation() -> dict:
    before = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_scientific_corpus_phase14_extraction.py"),
             "--output-root", tmp, "--max-pdf-pages", "1", "--max-pdfs", "1"],
            cwd=ROOT, check=True, capture_output=True, timeout=60,
        )
    after = {f: (ROOT / f).read_bytes() for f in CANONICAL_FILES}
    changed = [f for f in CANONICAL_FILES if before[f] != after[f]]
    return {"passed": len(changed) == 0, "changed_files": changed}


def audit_uoc_chain_crosswalk(crosswalk_rows) -> dict:
    positions = {r["chain_position"] for r in crosswalk_rows}
    expected = {str(i) for i in range(1, 12)}
    metric_row = next(
        (r for r in crosswalk_rows if r["chain_position"] == "6" and r["source_id"] == "UOC-COMPILER"), None
    )
    caveat_present = bool(metric_row and "not asserted" in metric_row.get("provenance", "").lower())
    return {
        "passed": positions == expected and caveat_present,
        "missing_positions": sorted(expected - positions),
        "metric_nonequivalence_caveat_present": caveat_present,
    }


def main() -> dict:
    equations = _read_jsonl(CORPUS_DIR / "equations" / "equation_registry.jsonl")
    variables = _read_jsonl(CORPUS_DIR / "variables" / "variable_registry.jsonl")
    operators = _read_jsonl(CORPUS_DIR / "operators" / "operator_registry.jsonl")
    relations = _read_jsonl(CORPUS_DIR / "relations" / "relation_registry.jsonl")
    structures = _read_jsonl(CORPUS_DIR / "structures" / "structure_registry.jsonl")
    literature_items = json.loads(
        (ROOT / "literature" / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json").read_text())

    import csv
    with (ROOT / "UOC_CHAIN_LITERATURE_CROSSWALK.csv").open() as f:
        crosswalk_rows = list(csv.DictReader(f))

    audits = {
        "source_provenance_audit": audit_source_provenance(equations, variables, operators, relations, structures),
        "extraction_completeness_audit": audit_extraction_completeness(equations, literature_items),
        "extraction_determinism_audit": audit_determinism(),
        "duplicate_audit": audit_duplicates(equations, variables, operators, relations, structures),
        "symbol_collision_audit": audit_symbol_collision(variables),
        "operator_audit": audit_operator_references(equations, operators),
        "relation_audit": audit_relation_references(equations, relations),
        "dimensional_metadata_audit": audit_dimensional_metadata(equations),
        "canonical_isolation_audit": audit_canonical_isolation(),
        "uoc_chain_crosswalk_audit": audit_uoc_chain_crosswalk(crosswalk_rows),
    }
    all_passed = all(a["passed"] for a in audits.values())
    result = {"all_passed": all_passed, "audits": audits}
    (ROOT / "PHASE14_EXTRACTION_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    result = main()
    for name, audit in result["audits"].items():
        print(f"{'PASS' if audit['passed'] else 'FAIL'}  {name}")
    print()
    print("ALL PASSED" if result["all_passed"] else "SOME AUDITS FAILED -- see PHASE14_EXTRACTION_AUDIT.json")
    sys.exit(0 if result["all_passed"] else 1)
