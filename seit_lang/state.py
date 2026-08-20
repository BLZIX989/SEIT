"""FMUTC state machine (Phase 3): the brief's new DECLARED->RESOLVED->
CALCULATED->VERIFIED->DERIVED->CERTIFIED pipeline with terminal branches
OPEN/FAILED/FALSIFIED/SUPERSEDED/BLOCKED, reconciled with -- not
replacing -- compiler/core/status.py's existing Status enum. This is the
one place in seit_lang that legitimately imports from compiler/core and
compiler/dependencies: the brief's own instruction is to EXPOSE those
systems through the language, not to avoid touching them (the isolation
discipline elsewhere in this repo, e.g. scientific_corpus/derivation,
is about never WRITING to canonical registries or compiler/ internals
outside the compiler's own execution path -- read-only imports of
compiler/core/status.py and compiler/dependencies/graph.py are exactly
what "reconciled with (not replacing)" and "expose the Forward-MDCL
dependency system through the language" ask for).

Design decisions worth stating plainly (all deliberate, none accidental):

1. A REAL, DOCUMENTED ORDERING DISCREPANCY. The brief's pipeline reads
   VERIFIED -> DERIVED. But compiler/core/status.py's own
   ALLOWED_TRANSITIONS has DERIVED: {VERIFIED, FAIL, FALSIFIED} and
   VERIFIED: {FALSIFIED} -- i.e. in the EXISTING compiler, a derivation
   is typically produced first and VERIFIED next (derive the formula,
   then verify it numerically), the opposite relative order from what
   the brief states for FMUTC. This module does NOT quietly harmonize
   the two: SeitState's transition graph below follows the brief's
   literal DECLARED->RESOLVED->CALCULATED->VERIFIED->DERIVED->CERTIFIED
   order (VERIFIED must precede DERIVED in an FMUTC-level program), and
   the reconciliation functions document the ordering clash rather than
   hiding it. A future phase reconciling this for real would need its
   own decision and its own record -- not a silent fix here.

2. CERTIFIED and SUPERSEDED have no compiler.core.status.Status
   equivalent at all (compiler/core/status.py has 8 values: VERIFIED,
   DERIVED, CALCULATED, CONDITIONAL, PROPOSED, OPEN, FAIL, FALSIFIED --
   nothing above VERIFIED/DERIVED, and no "replaced by newer work"
   concept). Downward-mapping CERTIFIED to Status.VERIFIED (never to
   DERIVED or something implying a status stronger than the compiler
   itself expresses) and SUPERSEDED to Status.OPEN (never to FAIL or
   FALSIFIED -- being superseded is not being wrong) are documented,
   deliberately conservative choices, each returned with lossy=True so
   no caller can mistake them for an exact round trip.

3. compiler.core.status.Status.CONDITIONAL and .PROPOSED have no
   corresponding rung in the brief's FMUTC state list. They still occur
   in real, existing registries (CONDITIONAL is one of the frontier's
   ADMISSIBLE_STATUSES; PROPOSED is where LEGACY_STATUS_MAP sends every
   unverified prose claim), so this module maps them lossily rather than
   refusing to reconcile: CONDITIONAL -> CALCULATED (the nearest rung
   compiler's own transition graph treats as a sibling of CONDITIONAL),
   PROPOSED -> DECLARED (a bare, uncomputed claim).

4. "States must not collapse" is enforced structurally, not just by
   having distinct enum members: CALCULATED cannot transition directly
   to DERIVED (must pass through VERIFIED); VERIFIED cannot transition
   directly to CERTIFIED (must pass through DERIVED); OPEN and FAILED
   have different reachable-state sets (OPEN can reach CALCULATED
   directly -- an open item can still be picked up and computed --
   FAILED can only return to DECLARED or OPEN, matching
   compiler/core/status.py's own FAIL: {OPEN, PROPOSED} "may be retried
   upstream" comment); FALSIFIED and SUPERSEDED are both terminal (no
   outgoing edges) but reconcile to different Status values, so they are
   never interchangeable even though both end a node's lifecycle.

5. Falsifiability is preserved at every rung, including the top one:
   CERTIFIED -> FALSIFIED is a real edge, mirroring
   compiler/core/status.py's own Status.VERIFIED: {FALSIFIED} comment,
   "a later counterexample can still falsify." Nothing in this project
   is ever above being falsified.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from compiler.core.status import Status
from compiler.dependencies.graph import EXECUTABLE_UPSTREAM_STATUSES


class SeitState(str, Enum):
    # main pipeline (brief's literal order)
    DECLARED = "DECLARED"
    RESOLVED = "RESOLVED"
    CALCULATED = "CALCULATED"
    VERIFIED = "VERIFIED"
    DERIVED = "DERIVED"
    CERTIFIED = "CERTIFIED"
    # terminal / branch states
    OPEN = "OPEN"
    FAILED = "FAILED"
    FALSIFIED = "FALSIFIED"
    SUPERSEDED = "SUPERSEDED"
    BLOCKED = "BLOCKED"


ALLOWED_SEIT_TRANSITIONS: dict[SeitState, set[SeitState]] = {
    SeitState.DECLARED: {SeitState.RESOLVED, SeitState.OPEN, SeitState.BLOCKED},
    SeitState.RESOLVED: {SeitState.CALCULATED, SeitState.OPEN, SeitState.BLOCKED, SeitState.FAILED},
    SeitState.CALCULATED: {SeitState.VERIFIED, SeitState.FAILED, SeitState.FALSIFIED},
    SeitState.VERIFIED: {SeitState.DERIVED, SeitState.FALSIFIED, SeitState.SUPERSEDED},
    SeitState.DERIVED: {SeitState.CERTIFIED, SeitState.FALSIFIED, SeitState.SUPERSEDED},
    SeitState.CERTIFIED: {SeitState.FALSIFIED, SeitState.SUPERSEDED},
    SeitState.OPEN: {SeitState.DECLARED, SeitState.RESOLVED, SeitState.CALCULATED,
                      SeitState.FAILED, SeitState.FALSIFIED},
    SeitState.FAILED: {SeitState.DECLARED, SeitState.OPEN},
    SeitState.FALSIFIED: set(),   # terminal
    SeitState.SUPERSEDED: set(),  # terminal
    SeitState.BLOCKED: {SeitState.RESOLVED, SeitState.OPEN, SeitState.FAILED},
}

# States entered into CALCULATED (the moment a node actually consumes
# its dependencies to produce a result) are exactly RESOLVED->CALCULATED
# and OPEN->CALCULATED per the graph above -- this is where dependency
# validity is enforced (see SeitStateMachine.transition).
_ENTERS_CALCULATED = {
    old for old, nxt in ALLOWED_SEIT_TRANSITIONS.items() if SeitState.CALCULATED in nxt
}

TERMINAL_SEIT_STATES: frozenset[SeitState] = frozenset(
    s for s, nxt in ALLOWED_SEIT_TRANSITIONS.items() if not nxt
)


def can_transition_seit(old: SeitState, new: SeitState) -> bool:
    if old == new:
        return True
    return new in ALLOWED_SEIT_TRANSITIONS.get(old, set())


class SeitStateError(Exception):
    pass


class InvalidSeitTransitionError(SeitStateError):
    def __init__(self, node: str, old: SeitState, new: SeitState):
        super().__init__(f"invalid transition for {node!r}: {old.value} -> {new.value} is not allowed")
        self.node = node
        self.old = old
        self.new = new


class DependencyNotReadyError(SeitStateError):
    def __init__(self, node: str, dep: str, dep_state: SeitState):
        super().__init__(
            f"{node!r} cannot enter CALCULATED: dependency {dep!r} is in state "
            f"{dep_state.value}, which does not reconcile to an "
            f"EXECUTABLE_UPSTREAM_STATUSES status (compiler/dependencies/graph.py)")
        self.node = node
        self.dep = dep
        self.dep_state = dep_state


# --- reconciliation with compiler.core.status.Status -----------------------

@dataclass(frozen=True)
class SeitFromStatus:
    seit_state: SeitState
    lossy: bool
    note: str


@dataclass(frozen=True)
class StatusFromSeit:
    status: Status
    lossy: bool
    note: str


_STATUS_TO_SEIT: dict[Status, SeitFromStatus] = {
    Status.VERIFIED: SeitFromStatus(SeitState.VERIFIED, False, "direct match"),
    Status.DERIVED: SeitFromStatus(
        SeitState.DERIVED, False,
        "label matches, but see module docstring: compiler's own DERIVED often "
        "PRECEDES VERIFIED (derive, then verify), the opposite relative order "
        "from FMUTC's stated DECLARED->...->VERIFIED->DERIVED->CERTIFIED pipeline"),
    Status.CALCULATED: SeitFromStatus(SeitState.CALCULATED, False, "direct match"),
    Status.CONDITIONAL: SeitFromStatus(
        SeitState.CALCULATED, True,
        "no CONDITIONAL rung exists in the brief's FMUTC state list; CALCULATED is "
        "the nearest rung compiler/core/status.py's own transition graph treats as "
        "a sibling of CONDITIONAL -- the 'holds only under stated assumptions' "
        "information is lost in this direction"),
    Status.PROPOSED: SeitFromStatus(
        SeitState.DECLARED, True,
        "PROPOSED (a bare prose claim, no artifact) is nearest to DECLARED (just "
        "introduced, nothing computed) -- not RESOLVED, since PROPOSED carries no "
        "claim about dependency readiness"),
    Status.OPEN: SeitFromStatus(SeitState.OPEN, False, "direct match"),
    Status.FAIL: SeitFromStatus(SeitState.FAILED, False, "same meaning, FAIL vs FAILED label only"),
    Status.FALSIFIED: SeitFromStatus(SeitState.FALSIFIED, False, "direct match, terminal in both"),
}

_SEIT_TO_STATUS: dict[SeitState, StatusFromSeit] = {
    SeitState.DECLARED: StatusFromSeit(
        Status.OPEN, True,
        "no artifact and no stated claim exist yet; compiler's PROPOSED implies a "
        "stated (if unverified) claim, which DECLARED does not -- OPEN is the "
        "closer, more conservative equivalent"),
    SeitState.RESOLVED: StatusFromSeit(
        Status.OPEN, True,
        "dependencies are structurally ready but nothing has executed yet; "
        "compiler/core/status.py has no rung for 'ready but not yet run' distinct "
        "from OPEN"),
    SeitState.CALCULATED: StatusFromSeit(Status.CALCULATED, False, "direct match"),
    SeitState.VERIFIED: StatusFromSeit(Status.VERIFIED, False, "direct match"),
    SeitState.DERIVED: StatusFromSeit(
        Status.DERIVED, False,
        "label matches; see module docstring for the ordering discrepancy"),
    SeitState.CERTIFIED: StatusFromSeit(
        Status.VERIFIED, True,
        "compiler/core/status.py has nothing above VERIFIED/DERIVED; CERTIFIED is "
        "mapped conservatively to VERIFIED (never to DERIVED, which carries a more "
        "specific structural-derivation meaning CERTIFIED does not by itself imply)"),
    SeitState.OPEN: StatusFromSeit(Status.OPEN, False, "direct match"),
    SeitState.FAILED: StatusFromSeit(Status.FAIL, False, "same meaning, FAILED vs FAIL label only"),
    SeitState.FALSIFIED: StatusFromSeit(Status.FALSIFIED, False, "direct match, terminal in both"),
    SeitState.SUPERSEDED: StatusFromSeit(
        Status.OPEN, True,
        "being superseded is NOT being wrong -- mapping to FAIL or FALSIFIED would "
        "misrepresent a replaced-by-better-work claim as an error; OPEN is the "
        "non-judgmental fallback compiler/core/status.py offers"),
    SeitState.BLOCKED: StatusFromSeit(
        Status.OPEN, True,
        "compiler/core/status.py has no formal BLOCKED status; a blocked node has "
        "produced no artifact, so OPEN is the closest non-committal equivalent"),
}


def status_to_seit_state(status: Status) -> SeitFromStatus:
    return _STATUS_TO_SEIT[status]


def seit_state_to_status(state: SeitState) -> StatusFromSeit:
    return _SEIT_TO_STATUS[state]


# --- per-node state machine with dependency-validity enforcement -----------

class SeitStateMachine:
    """Tracks SeitState per named node plus a dependency graph, and
    enforces "dependency validity" (Phase 3's own requirement) at the
    one transition where it actually matters: entering CALCULATED, i.e.
    the moment a node consumes its declared dependencies to produce a
    result. This reuses compiler/dependencies/graph.py's own
    EXECUTABLE_UPSTREAM_STATUSES constant rather than redefining what
    "ready" means."""

    def __init__(self) -> None:
        self.states: dict[str, SeitState] = {}
        self.dependencies: dict[str, set[str]] = {}

    def declare(self, node: str) -> None:
        if node in self.states:
            return
        self.states[node] = SeitState.DECLARED
        self.dependencies.setdefault(node, set())

    def add_dependency(self, node: str, depends_on: str) -> None:
        self.declare(node)
        self.declare(depends_on)
        self.dependencies[node].add(depends_on)

    def state_of(self, node: str) -> SeitState:
        return self.states[node]

    def transition(self, node: str, new_state: SeitState) -> None:
        self.declare(node)
        old_state = self.states[node]
        if not can_transition_seit(old_state, new_state):
            raise InvalidSeitTransitionError(node, old_state, new_state)
        if new_state == SeitState.CALCULATED and old_state in _ENTERS_CALCULATED:
            for dep in self.dependencies.get(node, ()):
                dep_state = self.states.get(dep, SeitState.DECLARED)
                dep_status = seit_state_to_status(dep_state).status
                if dep_status not in EXECUTABLE_UPSTREAM_STATUSES:
                    raise DependencyNotReadyError(node, dep, dep_state)
        self.states[node] = new_state
