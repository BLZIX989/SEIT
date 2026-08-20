"""Read-only adapter over the existing literature ingestion architecture
(brief: Literature Workspace, Phase 9). Never writes anything.

External literature search (arXiv/web APIs) is explicitly out of scope
here -- nothing in this module makes a network call. It reads exactly
the files the earlier L0/L0-A/L0-ST literature campaigns already
produced and committed:

- literature/manifests/LITERATURE_DOWNLOAD_MANIFEST.json -- acquisition
  provenance (URL, SHA256, page count) for every source actually
  downloaded.
- literature/extraction/STRING_THEORY_LITERATURE_REGISTRY.json and
  reports/l0/LITERATURE_EXTRACTION_REGISTRY.json -- two real but
  differently-shaped page/section/equation-cited extraction registries
  from two separate campaigns, kept verbatim rather than merged into
  one lossy schema.
- literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv -- the one
  genuine literature-to-node linkage in this repository: a real
  MDCL_NODE_ID column (curated, not free-text matching).
- literature/recovery/STRING_THEORY_PROPOSED_RECOVERIES/*.json --
  proposed (never canonical) recovery attempts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LITERATURE_DIR = REPO_ROOT / "literature"


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def get_sources() -> list[dict[str, Any]]:
    """Every source actually downloaded, verbatim, from the real
    acquisition manifest -- URL, SHA256, page count, license note."""
    manifest = _read_json(LITERATURE_DIR / "manifests" / "LITERATURE_DOWNLOAD_MANIFEST.json")
    if manifest is None:
        return []
    return manifest.get("acquired", [])


def get_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    string_theory = _read_json(LITERATURE_DIR / "extraction" / "STRING_THEORY_LITERATURE_REGISTRY.json") or []
    for rec in string_theory:
        items.append({
            "id": rec.get("STRING_ITEM_ID", ""),
            "source_id": rec.get("SOURCE_ID", ""),
            "corpus": "string_theory",
            "raw": rec,
        })

    general = _read_json(REPO_ROOT / "reports" / "l0" / "LITERATURE_EXTRACTION_REGISTRY.json") or []
    for rec in general:
        items.append({
            "id": rec.get("LITERATURE_ITEM_ID", ""),
            "source_id": rec.get("SOURCE_ID", ""),
            "corpus": "general",
            "raw": rec,
        })

    return items


def get_crosswalk(nodes: dict[str, dict] | None = None) -> list[dict[str, Any]]:
    """literature/crosswalk/STRING_THEORY_MDCL_CROSSWALK.csv, parsed into
    dicts. `node_is_registered` is computed against the live node set
    when provided -- several rows deliberately name a node the compiler
    doesn't register yet."""
    path = LITERATURE_DIR / "crosswalk" / "STRING_THEORY_MDCL_CROSSWALK.csv"
    if not path.exists():
        return []
    known = set(nodes) if nodes is not None else None
    out = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            node_id = (row.get("MDCL_NODE_ID") or "").strip()
            out.append({
                "raw": row,
                "mdcl_node_id": node_id,
                "node_is_registered": (node_id in known) if known is not None else False,
            })
    return out


def get_recoveries() -> list[dict[str, Any]]:
    recoveries_dir = LITERATURE_DIR / "recovery" / "STRING_THEORY_PROPOSED_RECOVERIES"
    if not recoveries_dir.exists():
        return []
    out = []
    for path in sorted(recoveries_dir.glob("*.json")):
        rec = json.loads(path.read_text())
        out.append({"id": rec.get("RECOVERY_ID", path.stem), "raw": rec})
    return out
