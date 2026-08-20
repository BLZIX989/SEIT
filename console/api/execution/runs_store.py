"""Storage for RunSnapshot records (architecture doc section 4.2/7).

`console_runs/` is gitignored by default -- an operational log, not
research content, same treatment as other generated-artifact
directories already in .gitignore. Every RunSnapshot is written once,
at completion, and `save()` refuses to overwrite an existing run_id:
"never overwrite prior states" is enforced by the store, not merely by
convention.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# console/api/execution/runs_store.py -> repo root is three parents up.
REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = REPO_ROOT / "console_runs"

_RUN_ID_RE = re.compile(r"^RUN-(\d+)$")


class RunAlreadyExistsError(FileExistsError):
    """Raised by save() if a snapshot for this run_id already exists --
    RunSnapshots are immutable once written."""


def next_run_id() -> str:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    max_n = 0
    for path in RUNS_DIR.glob("RUN-*.json"):
        m = _RUN_ID_RE.match(path.stem)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"RUN-{max_n + 1:04d}"


def save(snapshot: dict[str, Any]) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{snapshot['run_id']}.json"
    if path.exists():
        raise RunAlreadyExistsError(f"a RunSnapshot for {snapshot['run_id']} already exists at {path}")
    path.write_text(json.dumps(snapshot, indent=2))


def load(run_id: str) -> dict[str, Any] | None:
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def load_all() -> list[dict[str, Any]]:
    if not RUNS_DIR.exists():
        return []
    snapshots = []
    for path in sorted(RUNS_DIR.glob("RUN-*.json")):
        snapshots.append(json.loads(path.read_text()))
    snapshots.sort(key=lambda s: s["run_id"])
    return snapshots
