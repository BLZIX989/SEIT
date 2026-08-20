"""Tests for seit_lang.state (Phase 3)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.core.status import Status
from compiler.dependencies.graph import EXECUTABLE_UPSTREAM_STATUSES
from seit_lang.state import (
    ALLOWED_SEIT_TRANSITIONS,
    DependencyNotReadyError,
    InvalidSeitTransitionError,
    SeitState,
    SeitStateMachine,
    TERMINAL_SEIT_STATES,
    can_transition_seit,
    seit_state_to_status,
    status_to_seit_state,
)


def test_all_11_brief_states_present():
    expected = {
        "DECLARED", "RESOLVED", "CALCULATED", "VERIFIED", "DERIVED", "CERTIFIED",
        "OPEN", "FAILED", "FALSIFIED", "SUPERSEDED", "BLOCKED",
    }
    assert {s.value for s in SeitState} == expected


def test_every_state_has_a_transition_table_entry():
    assert set(ALLOWED_SEIT_TRANSITIONS) == set(SeitState)


# --- "states must not collapse" -----------------------------------------

def test_calculated_and_verified_are_distinct_and_require_explicit_edge():
    assert SeitState.CALCULATED != SeitState.VERIFIED
    assert can_transition_seit(SeitState.CALCULATED, SeitState.VERIFIED) is True
    # cannot skip the VERIFIED rung to reach DERIVED directly
    assert can_transition_seit(SeitState.CALCULATED, SeitState.DERIVED) is False


def test_verified_and_derived_are_distinct_and_require_explicit_edge():
    assert SeitState.VERIFIED != SeitState.DERIVED
    assert can_transition_seit(SeitState.VERIFIED, SeitState.DERIVED) is True
    # cannot skip DERIVED to reach CERTIFIED directly
    assert can_transition_seit(SeitState.VERIFIED, SeitState.CERTIFIED) is False


def test_open_and_failed_have_different_reachable_states():
    assert SeitState.OPEN != SeitState.FAILED
    assert ALLOWED_SEIT_TRANSITIONS[SeitState.OPEN] != ALLOWED_SEIT_TRANSITIONS[SeitState.FAILED]
    # OPEN may proceed straight to CALCULATED; FAILED may only retry
    assert can_transition_seit(SeitState.OPEN, SeitState.CALCULATED) is True
    assert can_transition_seit(SeitState.FAILED, SeitState.CALCULATED) is False


def test_falsified_and_superseded_are_both_terminal_but_distinct():
    assert SeitState.FALSIFIED != SeitState.SUPERSEDED
    assert TERMINAL_SEIT_STATES == {SeitState.FALSIFIED, SeitState.SUPERSEDED}
    # both terminal (no outgoing edges)...
    assert ALLOWED_SEIT_TRANSITIONS[SeitState.FALSIFIED] == set()
    assert ALLOWED_SEIT_TRANSITIONS[SeitState.SUPERSEDED] == set()
    # ...but reconcile to DIFFERENT compiler statuses -- not interchangeable
    assert seit_state_to_status(SeitState.FALSIFIED).status == Status.FALSIFIED
    assert seit_state_to_status(SeitState.SUPERSEDED).status == Status.OPEN
    assert seit_state_to_status(SeitState.FALSIFIED).lossy is False
    assert seit_state_to_status(SeitState.SUPERSEDED).lossy is True


def test_falsifiability_preserved_at_every_rung_including_certified():
    for s in (SeitState.CALCULATED, SeitState.VERIFIED, SeitState.DERIVED, SeitState.CERTIFIED):
        assert can_transition_seit(s, SeitState.FALSIFIED) is True


def test_failed_is_retriable_matching_compiler_fail_semantics():
    assert can_transition_seit(SeitState.FAILED, SeitState.DECLARED) is True
    assert can_transition_seit(SeitState.FAILED, SeitState.OPEN) is True


def test_same_state_transition_is_always_allowed():
    for s in SeitState:
        assert can_transition_seit(s, s) is True


def test_no_transitions_out_of_falsified_or_superseded():
    for terminal in TERMINAL_SEIT_STATES:
        for other in SeitState:
            if other == terminal:
                continue
            assert can_transition_seit(terminal, other) is False


# --- reconciliation with compiler.core.status.Status ------------------------

def test_status_to_seit_state_covers_all_8_status_values():
    for status in Status:
        result = status_to_seit_state(status)
        assert isinstance(result.seit_state, SeitState)


def test_seit_state_to_status_covers_all_11_seit_states():
    for state in SeitState:
        result = seit_state_to_status(state)
        assert isinstance(result.status, Status)


def test_direct_matches_are_not_lossy():
    for status in (Status.VERIFIED, Status.DERIVED, Status.CALCULATED, Status.OPEN,
                   Status.FAIL, Status.FALSIFIED):
        assert status_to_seit_state(status).lossy is False


def test_conditional_and_proposed_have_no_direct_seit_rung_and_are_lossy():
    assert status_to_seit_state(Status.CONDITIONAL).lossy is True
    assert status_to_seit_state(Status.PROPOSED).lossy is True


def test_certified_has_no_status_equivalent_and_maps_conservatively_to_verified():
    result = seit_state_to_status(SeitState.CERTIFIED)
    assert result.status == Status.VERIFIED
    assert result.lossy is True


def test_superseded_never_maps_to_a_failure_or_falsification_status():
    result = seit_state_to_status(SeitState.SUPERSEDED)
    assert result.status not in (Status.FAIL, Status.FALSIFIED)


# --- SeitStateMachine: transitions + dependency validity --------------------

def test_declare_starts_a_node_at_declared():
    m = SeitStateMachine()
    m.declare("L")
    assert m.state_of("L") == SeitState.DECLARED


def test_valid_transition_sequence():
    m = SeitStateMachine()
    m.declare("L")
    m.transition("L", SeitState.RESOLVED)
    m.transition("L", SeitState.CALCULATED)
    m.transition("L", SeitState.VERIFIED)
    m.transition("L", SeitState.DERIVED)
    m.transition("L", SeitState.CERTIFIED)
    assert m.state_of("L") == SeitState.CERTIFIED


def test_invalid_transition_raises():
    m = SeitStateMachine()
    m.declare("L")
    with pytest.raises(InvalidSeitTransitionError):
        m.transition("L", SeitState.DERIVED)  # cannot skip straight from DECLARED


def test_dependency_not_ready_blocks_entry_into_calculated():
    m = SeitStateMachine()
    m.add_dependency("L", "B")  # L depends on B; B still DECLARED
    m.transition("L", SeitState.RESOLVED)
    with pytest.raises(DependencyNotReadyError):
        m.transition("L", SeitState.CALCULATED)


def test_dependency_ready_allows_entry_into_calculated():
    m = SeitStateMachine()
    m.add_dependency("L", "B")
    m.transition("B", SeitState.RESOLVED)
    m.transition("B", SeitState.CALCULATED)  # B has no deps, enters freely
    m.transition("L", SeitState.RESOLVED)
    m.transition("L", SeitState.CALCULATED)  # now B is CALCULATED -> ready
    assert m.state_of("L") == SeitState.CALCULATED


def test_dependency_ready_via_conditional_reconciliation():
    # B's real compiler-side status is CONDITIONAL, which reconciles
    # (lossily) to SeitState.CALCULATED -- still EXECUTABLE_UPSTREAM per
    # compiler/dependencies/graph.py, so L must be allowed to proceed.
    m = SeitStateMachine()
    m.add_dependency("L", "B")
    m.transition("B", SeitState.RESOLVED)
    m.transition("B", SeitState.CALCULATED)
    assert seit_state_to_status(SeitState.CALCULATED).status in EXECUTABLE_UPSTREAM_STATUSES
    m.transition("L", SeitState.RESOLVED)
    m.transition("L", SeitState.CALCULATED)


def test_declaring_an_already_declared_node_is_idempotent():
    m = SeitStateMachine()
    m.declare("L")
    m.transition("L", SeitState.RESOLVED)
    m.declare("L")  # must not reset back to DECLARED
    assert m.state_of("L") == SeitState.RESOLVED


def test_add_dependency_auto_declares_both_nodes():
    m = SeitStateMachine()
    m.add_dependency("L", "B")
    assert m.state_of("L") == SeitState.DECLARED
    assert m.state_of("B") == SeitState.DECLARED
    assert "B" in m.dependencies["L"]
