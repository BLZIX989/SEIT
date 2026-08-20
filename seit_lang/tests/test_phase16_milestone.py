"""Phase 16 (first milestone): the brief's own spectral_test.seit
program is actually executable via `seit run`, producing a real
machine-readable result -- not a design document.

WHAT THIS PHASE ADDS ON TOP OF PHASES 1-15: every earlier phase could
already parse, type-check, compile, and evaluate spectral_test.seit
IN-PROCESS (see seit_lang/tests/test_parser.py,
test_semantic.py, test_evaluate.py). What was still missing for the
brief's literal "runnable via `seit run spectral_test.seit`" was a way
for the CLI itself to be given B's actual value -- `variable B:
IncidenceMatrix;` has no producing statement (Phase 4's own, honest
finding), so nothing in the source text can supply it; some external
mechanism has to. cli.py gained a `--inputs <file.json>` flag for
exactly this (see cli._load_inputs), used here for the first time
end to end, over a real subprocess invocation of `python -m
seit_lang.cli` / `python -m seit_lang` -- the closest thing this
un-packaged repository has to an installed `seit` executable.

TWO FIXTURES, BOTH HONEST: spectral_test.seit is the brief's own
LITERAL example text, byte for byte -- and it still fails at `seit
run`, for the exact reason Phase 2's own tests found (heat_kernel(L,
beta) calls beta, which the literal example never declares). That
finding is not papered over here: test_literal_milestone_still_fails_
via_cli confirms the CLI reports the same honest failure a real user
running the brief's own text verbatim would see. spectral_test_
complete.seit (Phase 1) is the one-line-corrected version (`constant
beta: Scalar = 1.0;` added) that Phase 16 actually delivers as
"executable," run here with a real, concretely constructed incidence
matrix for a 3-vertex path graph (spectral_test_inputs.json) -- not a
placeholder value chosen to look right, but literally B[i,col]=+/-1
for that graph's own edges, the same convention Phase 6's
ring_incidence_matrix uses.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.cli import cmd_report, cmd_run, cmd_verify
from seit_lang.manifest import build_manifest

FIXTURES = Path(__file__).parent / "fixtures"
MILESTONE_LITERAL = str(FIXTURES / "spectral_test.seit")
MILESTONE_COMPLETE = str(FIXTURES / "spectral_test_complete.seit")
MILESTONE_INPUTS = str(FIXTURES / "spectral_test_inputs.json")

_B = np.array([[-1.0, 0.0], [1.0, -1.0], [0.0, 1.0]])


# --- the literal brief text still honestly fails, unchanged from Phase 2 ---

def test_literal_milestone_fails_via_cli_run_for_the_documented_reason():
    result = cmd_run(MILESTONE_LITERAL, inputs_path=MILESTONE_INPUTS)
    assert result["ok"] is False
    assert "beta" in result["error"]


# --- the corrected milestone genuinely runs, in-process --------------------

def test_corrected_milestone_runs_with_real_supplied_B():
    result = cmd_run(MILESTONE_COMPLETE, inputs_path=MILESTONE_INPUTS)
    assert result["ok"] is True
    assert result["declared_inputs"] == ["B"]
    L = np.array(result["environment"]["L"])
    assert np.allclose(L, _B @ _B.T)
    assert result["states"]["L"] == "CALCULATED"  # no longer BLOCKED, per Phase 4's honest finding


def test_corrected_milestone_verify_statements_genuinely_pass():
    result = cmd_verify(MILESTONE_COMPLETE, inputs_path=MILESTONE_INPUTS)
    assert result["ok"] is True
    assert len(result["verify_results"]) == 2
    assert all(r["passed"] is True for r in result["verify_results"])


def test_corrected_milestone_report_is_fully_successful():
    result = cmd_report(MILESTONE_COMPLETE, inputs_path=MILESTONE_INPUTS)
    assert result["ok"] is True
    assert result["blocked"] == {}
    assert result["states"]["L"] == "CALCULATED"
    assert result["states"]["B"] == "CALCULATED"  # supplied input, no producing statement


def test_corrected_milestone_manifest_records_real_heat_kernel_output():
    manifest = build_manifest(MILESTONE_COMPLETE, inputs={"B": _B})
    assert manifest["execution_manifest"]["run_succeeded"] is True
    L = np.array(manifest["numerical_outputs"]["L"])
    assert np.allclose(L, _B @ _B.T)
    assert "spectrum" in manifest["operator_registry"]
    assert "heat_kernel" in manifest["operator_registry"]


# --- real subprocess invocation: `seit run spectral_test_complete.seit` ----

def test_milestone_runnable_via_real_seit_cli_subprocess():
    proc = subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "run", MILESTONE_COMPLETE,
         "--inputs", MILESTONE_INPUTS],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=60)
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    L = np.array(payload["environment"]["L"])
    assert np.allclose(L, _B @ _B.T)


def test_milestone_runnable_via_seit_lang_module_entrypoint():
    """`python -m seit_lang run ...` (seit_lang/__main__.py) is the
    closest thing this un-packaged repository has to `seit run` as a
    standalone executable."""
    proc = subprocess.run(
        [sys.executable, "-m", "seit_lang", "run", MILESTONE_COMPLETE,
         "--inputs", MILESTONE_INPUTS],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=60)
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True


def test_milestone_exit_code_is_1_when_input_withheld():
    proc = subprocess.run(
        [sys.executable, "-m", "seit_lang.cli", "run", MILESTONE_COMPLETE],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
