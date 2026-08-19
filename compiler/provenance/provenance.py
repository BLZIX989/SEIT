"""Provenance engine (spec section 27)."""
from __future__ import annotations

import platform
import subprocess
from datetime import datetime, timezone

from compiler.core.ir import Provenance
from compiler.core.status import Status


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
            cwd=_repo_root(),
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _repo_root() -> str:
    import pathlib
    return str(pathlib.Path(__file__).resolve().parents[2])


def numerical_environment() -> dict[str, str]:
    env = {"python": platform.python_version()}
    for mod in ("numpy", "scipy", "sympy"):
        try:
            m = __import__(mod)
            env[mod] = getattr(m, "__version__", "unknown")
        except ImportError:
            env[mod] = "not installed"
    return env


CODE_VERSION = "forward-mdcl-compiler-0.1.0"


def make_provenance(
    *,
    source: str,
    source_version: str = "",
    object_id: str = "",
    equation_id: str = "",
    dependency_ids: list[str] | None = None,
    transformation_id: str = "",
    calculation_id: str = "",
    status: Status = Status.OPEN,
    verification: dict | None = None,
) -> Provenance:
    return Provenance(
        source=source,
        source_version=source_version,
        object_id=object_id,
        equation_id=equation_id,
        dependency_ids=list(dependency_ids or []),
        transformation_id=transformation_id,
        calculation_id=calculation_id,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        git_commit=_git_commit(),
        code_version=CODE_VERSION,
        numerical_environment=numerical_environment(),
        status=status.value,
        verification=verification or {},
    )
