from enum import Enum
from typing import Set, Dict, Any, Optional

class IllegalStateTransitionError(Exception):
    def __init__(self, machine_name: str, current_state: str, attempted_state: str, allowed_transitions: Set[str]):
        self.machine_name = machine_name
        self.current_state = current_state
        self.attempted_state = attempted_state
        self.allowed_transitions = allowed_transitions
        super().__init__(
            f"[{machine_name}] Illegal transition from '{current_state}' to '{attempted_state}'. "
            f"Allowed next states: {sorted(list(allowed_transitions)) or 'None (Terminal state)'}"
        )


class ConsentState(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    REVOCATION_REQUESTED = "REVOCATION_REQUESTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class ConsentStateMachine:
    LEGAL_TRANSITIONS: Dict[ConsentState, Set[ConsentState]] = {
        ConsentState.DRAFT: {ConsentState.PENDING_APPROVAL, ConsentState.ACTIVE},
        ConsentState.PENDING_APPROVAL: {ConsentState.ACTIVE, ConsentState.REVOKED},
        ConsentState.ACTIVE: {ConsentState.REVOCATION_REQUESTED, ConsentState.EXPIRED, ConsentState.REVOKED},
        ConsentState.REVOCATION_REQUESTED: {ConsentState.REVOKED},
        ConsentState.REVOKED: set(),  # Terminal: once revoked, cannot be silently revived
        ConsentState.EXPIRED: set()   # Terminal: requires new consent contract
    }

    def __init__(self, initial_state: ConsentState = ConsentState.DRAFT):
        self.state = initial_state

    def transition(self, to_state: ConsentState) -> ConsentState:
        allowed = self.LEGAL_TRANSITIONS.get(self.state, set())
        if to_state not in allowed:
            raise IllegalStateTransitionError(
                "ConsentStateMachine",
                self.state.value,
                to_state.value,
                {s.value for s in allowed}
            )
        self.state = to_state
        return self.state


class RecordIntegrityState(str, Enum):
    INGESTED = "INGESTED"
    ANALYZING = "ANALYZING"
    VERIFIED = "VERIFIED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    LINKED_PAIR = "LINKED_PAIR"
    CLINICIAN_FLAGGED = "CLINICIAN_FLAGGED"
    SUPERSEDED = "SUPERSEDED"


class RecordIntegrityStateMachine:
    LEGAL_TRANSITIONS: Dict[RecordIntegrityState, Set[RecordIntegrityState]] = {
        RecordIntegrityState.INGESTED: {RecordIntegrityState.ANALYZING, RecordIntegrityState.VERIFIED, RecordIntegrityState.CONFLICT_DETECTED},
        RecordIntegrityState.ANALYZING: {RecordIntegrityState.VERIFIED, RecordIntegrityState.CONFLICT_DETECTED, RecordIntegrityState.LINKED_PAIR},
        RecordIntegrityState.VERIFIED: {RecordIntegrityState.CONFLICT_DETECTED, RecordIntegrityState.SUPERSEDED, RecordIntegrityState.CLINICIAN_FLAGGED},
        RecordIntegrityState.CONFLICT_DETECTED: {RecordIntegrityState.LINKED_PAIR, RecordIntegrityState.CLINICIAN_FLAGGED, RecordIntegrityState.SUPERSEDED},
        RecordIntegrityState.LINKED_PAIR: {RecordIntegrityState.CLINICIAN_FLAGGED, RecordIntegrityState.SUPERSEDED},
        RecordIntegrityState.CLINICIAN_FLAGGED: {RecordIntegrityState.SUPERSEDED, RecordIntegrityState.VERIFIED},
        RecordIntegrityState.SUPERSEDED: set()  # Terminal: historical archive with supersession marker
    }

    def __init__(self, initial_state: RecordIntegrityState = RecordIntegrityState.INGESTED):
        self.state = initial_state

    def transition(self, to_state: RecordIntegrityState) -> RecordIntegrityState:
        allowed = self.LEGAL_TRANSITIONS.get(self.state, set())
        if to_state not in allowed:
            raise IllegalStateTransitionError(
                "RecordIntegrityStateMachine",
                self.state.value,
                to_state.value,
                {s.value for s in allowed}
            )
        self.state = to_state
        return self.state


class BreakGlassState(str, Enum):
    ARMED = "ARMED"
    TRIGGERED = "TRIGGERED"
    TIME_BOUNDED_ACTIVE = "TIME_BOUNDED_ACTIVE"
    AUTO_TERMINATED = "AUTO_TERMINATED"
    AUDITED = "AUDITED"


class BreakGlassStateMachine:
    LEGAL_TRANSITIONS: Dict[BreakGlassState, Set[BreakGlassState]] = {
        BreakGlassState.ARMED: {BreakGlassState.TRIGGERED},
        BreakGlassState.TRIGGERED: {BreakGlassState.TIME_BOUNDED_ACTIVE, BreakGlassState.AUTO_TERMINATED},
        BreakGlassState.TIME_BOUNDED_ACTIVE: {BreakGlassState.AUTO_TERMINATED},
        BreakGlassState.AUTO_TERMINATED: {BreakGlassState.AUDITED},
        BreakGlassState.AUDITED: {BreakGlassState.ARMED}  # Can re-arm for future emergencies
    }

    def __init__(self, initial_state: BreakGlassState = BreakGlassState.ARMED):
        self.state = initial_state

    def transition(self, to_state: BreakGlassState) -> BreakGlassState:
        allowed = self.LEGAL_TRANSITIONS.get(self.state, set())
        if to_state not in allowed:
            raise IllegalStateTransitionError(
                "BreakGlassStateMachine",
                self.state.value,
                to_state.value,
                {s.value for s in allowed}
            )
        self.state = to_state
        return self.state
