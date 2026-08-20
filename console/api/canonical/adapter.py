"""Read-only adapter over the existing compiler registry files.

This module NEVER writes to any *_registry.json / master_mdcl.json /
status_matrix.json / self_audit_report.json / fc005_result.json file.
Every function here is a pure read + reshape. The compiler
(`compiler/run_compiler.py`) remains the only writer of these files.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# console/api/canonical/adapter.py -> repo root is three parents up.
REPO_ROOT = Path(__file__).resolve().parents[3]

REGISTRY_FILES = {
    "types": "type_registry.json",
    "objects": "object_registry.json",
    "transformations": "transformation_registry.json",
    "equations": "equation_registry.json",
    "status_matrix": "status_matrix.json",
    "master_mdcl": "master_mdcl.json",
    "self_audit": "self_audit_report.json",
    "target_independence": "target_independence.json",
    "proofs": "proof_registry.json",
    "calculations": "calculation_registry.json",
    "falsifications": "falsification_registry.json",
    "provenance": "provenance_registry.json",
    "fc005_result": "fc005_result.json",
}


class RegistryNotFoundError(FileNotFoundError):
    """Raised when a registry file is missing -- e.g. before the first
    `python3 -m compiler.run_compiler` invocation in a fresh checkout.
    The API must surface this honestly (503/explicit error), never
    fall back to synthetic data (brief section XXXII)."""


def _read_json(relative_name: str) -> Any:
    path = REPO_ROOT / relative_name
    if not path.exists():
        raise RegistryNotFoundError(
            f"{relative_name} not found at repo root ({path}). "
            f"Run `python3 -m compiler.run_compiler` first."
        )
    return json.loads(path.read_text())


def load_all() -> dict[str, Any]:
    """Load every registry file fresh (no caching across requests --
    canonical state can change between two API calls if a run happens
    in between, and this adapter must never serve stale data)."""
    return {key: _read_json(fname) for key, fname in REGISTRY_FILES.items()}


def get_types() -> list[dict]:
    return _read_json(REGISTRY_FILES["types"])


def get_objects() -> list[dict]:
    return _read_json(REGISTRY_FILES["objects"])


def get_transformations() -> list[dict]:
    return _read_json(REGISTRY_FILES["transformations"])


def get_equations() -> list[dict]:
    return _read_json(REGISTRY_FILES["equations"])


def get_status_matrix() -> list[dict]:
    return _read_json(REGISTRY_FILES["status_matrix"])


def get_master_mdcl() -> dict:
    return _read_json(REGISTRY_FILES["master_mdcl"])


def get_self_audit() -> list[dict]:
    return _read_json(REGISTRY_FILES["self_audit"])


def get_target_independence() -> dict:
    return _read_json(REGISTRY_FILES["target_independence"])


def get_proofs() -> list[dict]:
    return _read_json(REGISTRY_FILES["proofs"])


def get_calculations() -> list[dict]:
    return _read_json(REGISTRY_FILES["calculations"])


def get_falsifications() -> list[dict]:
    return _read_json(REGISTRY_FILES["falsifications"])


def get_provenance() -> dict:
    return _read_json(REGISTRY_FILES["provenance"])


def get_fc005_result() -> dict:
    return _read_json(REGISTRY_FILES["fc005_result"])


def get_all_nodes_merged() -> dict[str, dict]:
    """Merge objects/transformations/equations into one id-keyed dict,
    each entry tagged with its `kind`. This is the single canonical
    node lookup every other function in this package builds on."""
    merged: dict[str, dict] = {}
    for kind, loader in (("Object", get_objects),
                          ("Transformation", get_transformations),
                          ("Equation", get_equations)):
        for node in loader():
            entry = dict(node)
            entry["kind"] = kind
            merged[node["id"]] = entry
    return merged


def build_reverse_dependency_index(nodes: dict[str, dict]) -> dict[str, list[str]]:
    """id -> list of node ids that declare a dependency on it (dependents)."""
    reverse: dict[str, list[str]] = {nid: [] for nid in nodes}
    for nid, node in nodes.items():
        for dep in node.get("dependencies", []):
            reverse.setdefault(dep, []).append(nid)
    return reverse


def find_falsifications_for_node(node_id: str, falsifications: list[dict]) -> list[dict]:
    """Best-effort match of falsification_registry.json's free-text
    `target` field against a node id. `falsification_registry.json`
    records were never designed with a strict node-id foreign key (some
    targets are e.g. 'diffusion-metric-candidate(cycle)'), so this
    returns matches tagged with an honest confidence level rather than
    silently presenting a guess as a certain link."""
    matches = []
    for f in falsifications:
        target = f.get("target", "")
        if target == node_id:
            matches.append({"record": f, "match_confidence": "exact_id"})
        elif target.startswith(node_id):
            matches.append({"record": f, "match_confidence": "prefix_match"})
        elif node_id.lower() in target.lower():
            matches.append({"record": f, "match_confidence": "substring_match"})
    return matches


def find_calculations_for_node(node_id: str, provenance: dict, calculations: list[dict]) -> list[dict]:
    """Link via provenance_registry.json[node_id]['calculation_id'], the
    real foreign key the compiler itself writes -- not a text-match
    heuristic."""
    prov = provenance.get(node_id, {})
    calc_id = prov.get("calculation_id", "")
    if not calc_id:
        return []
    return [c for c in calculations if c.get("id") == calc_id]


def find_proofs_for_node(node_id: str, proofs: list[dict]) -> list[dict]:
    """Real foreign key: proof_registry.json entries carry transformation_id."""
    return [p for p in proofs if p.get("transformation_id") == node_id]
