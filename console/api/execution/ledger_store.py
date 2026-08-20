"""Append-only Research Ledger (brief section XII, architecture doc
section 4.3). `console_research/ledger.jsonl` is gitignored by default,
same as `console_runs/`. There is no update/delete here -- only
`append()` and reads. Each event's `content_hash` is a sha256 of its
(action, inputs, outputs) for tamper-evidence, computed by the caller
and passed in already set (this module does not silently rewrite a
caller-supplied hash).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = REPO_ROOT / "console_research" / "ledger.jsonl"


def append(event: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a") as f:
        f.write(json.dumps(event) + "\n")


def tail(limit: int = 50) -> list[dict[str, Any]]:
    """Most recent `limit` events, newest last (matches how a log tail
    reads). Returns [] if the ledger does not exist yet -- an empty
    ledger is a true, honest state (no runs/events have happened),
    never an error."""
    if not LEDGER_PATH.exists():
        return []
    lines = LEDGER_PATH.read_text().splitlines()
    events = [json.loads(line) for line in lines if line.strip()]
    return events[-limit:]


def all_events() -> list[dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    lines = LEDGER_PATH.read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]
