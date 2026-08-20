"""Hypothesis status state machine (brief section XI, architecture doc
section 4.4). Same pattern as compiler/core/status.py's own
ALLOWED_TRANSITIONS -- a hypothesis's status is informational only (it
can never promote the corresponding MDCL node's canonical status,
which only the compiler itself can do via Status.can_transition()), but
it still has to obey a real state machine so the UI cannot jump a
hypothesis straight from PROPOSED to VERIFIED without ever having been
tested.
"""
from __future__ import annotations

HypothesisStatus = str  # kept as plain str (not an Enum) to match the
                         # pydantic Literal used in models.Hypothesis

STATUSES = {
    "PROPOSED", "TESTING", "SUPPORTED", "DERIVED", "VERIFIED",
    "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED",
}

TERMINAL_STATUSES = {"REJECTED", "FALSIFIED", "SUPERSEDED"}

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PROPOSED": {"TESTING", "REJECTED", "BLOCKED"},
    "TESTING": {"SUPPORTED", "REJECTED", "FALSIFIED", "BLOCKED"},
    "SUPPORTED": {"DERIVED", "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED"},
    "DERIVED": {"VERIFIED", "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED"},
    "VERIFIED": {"SUPERSEDED"},  # a later counterexample can still supersede/falsify
    "BLOCKED": {"PROPOSED", "TESTING", "REJECTED"},  # unblock back into the pipeline
    "REJECTED": set(),    # terminal
    "FALSIFIED": set(),   # terminal
    "SUPERSEDED": set(),  # terminal
}


def can_transition(old: str, new: str) -> bool:
    if old == new:
        return True
    return new in ALLOWED_TRANSITIONS.get(old, set())
