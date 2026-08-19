"""Canonical status system for the Forward-MDCL compiler (spec section 4).

CALCULATED != DERIVED. VERIFIED numerical reproduction != theoretical
derivation. Checkpoint reproduction != provenance. Numerical coincidence !=
structural identity. Fitted parameter != prediction.
"""
from __future__ import annotations

from enum import Enum


class Status(str, Enum):
    VERIFIED = "VERIFIED"
    DERIVED = "DERIVED"
    CALCULATED = "CALCULATED"
    CONDITIONAL = "CONDITIONAL"
    PROPOSED = "PROPOSED"
    OPEN = "OPEN"
    FAIL = "FAIL"
    FALSIFIED = "FALSIFIED"


class TerminalStatus(str, Enum):
    CLOSED = "CLOSED"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CONDITIONALLY_CLOSED = "CONDITIONALLY_CLOSED"
    FALSIFIED = "FALSIFIED"


# Historical/legacy labels found in source documents (e.g. "CERTIFIED",
# "PROVEN") must map into the canonical Status system rather than being
# used verbatim. A bare prose assertion is never promoted above PROPOSED;
# promotion to DERIVED/VERIFIED requires an executed, registered artifact.
LEGACY_STATUS_MAP: dict[str, Status] = {
    "CERTIFIED": Status.PROPOSED,
    "PROVEN": Status.PROPOSED,
    "ESTABLISHED": Status.PROPOSED,
    "DERIVED": Status.PROPOSED,     # prose claim of "derived" without artifact
    "VERIFIED": Status.PROPOSED,    # prose claim of "verified" without artifact
    "CALCULATED": Status.PROPOSED,  # prose claim of "calculated" without artifact
    "COMPLETE": Status.PROPOSED,
    "SOLVED": Status.PROPOSED,
}


def map_legacy_status(label: str) -> Status:
    """Map a historical/prose status label onto the canonical Status enum.

    Per governing discipline (spec section 2): a document's own claim that
    something is CERTIFIED/DERIVED/VERIFIED is never taken at face value.
    Only an executed calculation in this compiler may assign VERIFIED,
    DERIVED, or CALCULATED. Everything sourced from prose lands at PROPOSED
    unless explicitly re-derived here.
    """
    return LEGACY_STATUS_MAP.get(label.strip().upper(), Status.PROPOSED)


# Allowed status transitions during execution of a transformation.
ALLOWED_TRANSITIONS: dict[Status, set[Status]] = {
    Status.OPEN: {Status.PROPOSED, Status.CONDITIONAL, Status.CALCULATED,
                  Status.FAIL, Status.FALSIFIED},
    Status.PROPOSED: {Status.CONDITIONAL, Status.CALCULATED, Status.DERIVED,
                       Status.FAIL, Status.FALSIFIED, Status.OPEN},
    Status.CONDITIONAL: {Status.CALCULATED, Status.DERIVED, Status.VERIFIED,
                          Status.FAIL, Status.FALSIFIED, Status.OPEN},
    Status.CALCULATED: {Status.DERIVED, Status.VERIFIED, Status.FAIL,
                         Status.FALSIFIED, Status.CONDITIONAL},
    Status.DERIVED: {Status.VERIFIED, Status.FAIL, Status.FALSIFIED},
    Status.VERIFIED: {Status.FALSIFIED},  # a later counterexample can still falsify
    Status.FAIL: {Status.OPEN, Status.PROPOSED},  # may be retried upstream
    Status.FALSIFIED: set(),  # terminal
}


def can_transition(old: Status, new: Status) -> bool:
    if old == new:
        return True
    return new in ALLOWED_TRANSITIONS.get(old, set())
