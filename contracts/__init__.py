"""Shared versioned contracts for the Hotel Smart-Glasses POC."""

from contracts.models import (
    CandidateEnrollment,
    CueMessage,
    CuePayload,
    DeviceStreamMessage,
    DebugFaceDetection,
    DebugFrameMessage,
    GuestRegistrationRequest,
    GuestUpdateRequest,
    LoungeProfile,
    MatchEvent,
    RosterEntry,
    TapEvent,
    utc_now_iso,
)

__all__ = [
    "CandidateEnrollment",
    "CueMessage",
    "CuePayload",
    "DeviceStreamMessage",
    "DebugFaceDetection",
    "DebugFrameMessage",
    "GuestRegistrationRequest",
    "GuestUpdateRequest",
    "LoungeProfile",
    "MatchEvent",
    "RosterEntry",
    "TapEvent",
    "utc_now_iso",
]
