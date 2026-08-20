"""Append-only Hypothesis store (brief section XI, architecture doc
section 4.4). `console_research/hypotheses.jsonl` -- gitignored, same
as console_research/ledger.jsonl (Phase 6). Every write appends one
*complete* Hypothesis snapshot as a JSON line; nothing is ever mutated
in place. "Current" state for a given id is simply its latest line --
this gives the full state history for free and matches the
WRITE/MERGE/RECALL/RESOLVE/REJECT/SUPERSEDE model referenced in the
brief, without needing a second delta-event log alongside it.

This module never imports anything from console/api/canonical --
target_node_id validation against the real MDCL happens one layer up,
in main.py, so this store stays a pure, canonical-state-agnostic
read/write layer over its own file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
HYPOTHESES_PATH = REPO_ROOT / "console_research" / "hypotheses.jsonl"

_HYP_ID_RE = re.compile(r"^HYP-(\d+)$")


def _all_lines() -> list[dict[str, Any]]:
    if not HYPOTHESES_PATH.exists():
        return []
    lines = HYPOTHESES_PATH.read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def next_hypothesis_id() -> str:
    max_n = 0
    for rec in _all_lines():
        m = _HYP_ID_RE.match(rec.get("id", ""))
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"HYP-{max_n + 1:04d}"


def append(hypothesis: dict[str, Any]) -> None:
    HYPOTHESES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HYPOTHESES_PATH.open("a") as f:
        f.write(json.dumps(hypothesis) + "\n")


def load_history(hypothesis_id: str) -> list[dict[str, Any]]:
    """Every recorded state for this id, oldest first."""
    return [rec for rec in _all_lines() if rec.get("id") == hypothesis_id]


def load_current(hypothesis_id: str) -> dict[str, Any] | None:
    history = load_history(hypothesis_id)
    return history[-1] if history else None


def load_current_all() -> list[dict[str, Any]]:
    """Latest snapshot per hypothesis id, in id order."""
    latest: dict[str, dict[str, Any]] = {}
    for rec in _all_lines():
        latest[rec["id"]] = rec  # later lines overwrite earlier ones for the same id
    return [latest[hid] for hid in sorted(latest)]


_WORD_RE = re.compile(r"[a-z0-9]+")


def _normalize(statement: str) -> set[str]:
    return set(_WORD_RE.findall(statement.lower()))


def find_possible_duplicates(
    target_node_id: str, statement: str, exclude_terminal: bool = True,
) -> list[dict[str, Any]]:
    """Heuristic-only "has an equivalent hypothesis already been tried"
    check (brief section XI): exact normalized-word-set match, or >=0.6
    Jaccard overlap, against other hypotheses targeting the same node.
    This is explicitly a heuristic, not a proof of equivalence -- the
    API reports it as such via `match_confidence`, the same honesty
    pattern used for falsification-record matching in
    console/api/canonical/adapter.py.
    """
    from console.api.research.hypothesis_status import TERMINAL_STATUSES

    target_words = _normalize(statement)
    if not target_words:
        return []

    matches = []
    for rec in load_current_all():
        if rec["target_node_id"] != target_node_id:
            continue
        if exclude_terminal and rec["status"] in TERMINAL_STATUSES:
            continue
        other_words = _normalize(rec["statement"])
        if not other_words:
            continue
        if other_words == target_words:
            confidence = "exact_normalized_match"
            score = 1.0
        else:
            overlap = len(target_words & other_words) / len(target_words | other_words)
            if overlap < 0.6:
                continue
            confidence = "word_overlap"
            score = overlap
        matches.append({
            "id": rec["id"], "statement": rec["statement"], "status": rec["status"],
            "match_confidence": confidence, "similarity": round(score, 3),
        })
    matches.sort(key=lambda m: -m["similarity"])
    return matches


def historical_failure_rates() -> dict[str, float]:
    """Per-node: (REJECTED + FALSIFIED hypotheses) / (all terminal
    hypotheses) targeting that node, from real hypothesis records only.
    A node with no terminal hypotheses is absent from the result (there
    is no rate to report -- 0.0 would falsely imply "tried and always
    succeeded"). This is the one new, real "historical failure rate"
    input to frontier ranking transparency (brief section XV) that
    Phase 7 makes possible -- everything else on that list was already
    computable from canonical state alone.
    """
    from console.api.research.hypothesis_status import TERMINAL_STATUSES

    terminal_counts: dict[str, int] = {}
    failed_counts: dict[str, int] = {}
    for rec in load_current_all():
        if rec["status"] not in TERMINAL_STATUSES:
            continue
        nid = rec["target_node_id"]
        terminal_counts[nid] = terminal_counts.get(nid, 0) + 1
        if rec["status"] in ("REJECTED", "FALSIFIED"):
            failed_counts[nid] = failed_counts.get(nid, 0) + 1
    return {
        nid: round(failed_counts.get(nid, 0) / count, 3)
        for nid, count in terminal_counts.items()
    }
