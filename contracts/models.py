"""Shared Pydantic data models matching contracts/*.schema.json.

These versioned contracts define data exchange between:
- Card-reader adapter / tap-simulator -> lounge-control
- Phone bridge / frame-replay <-> lounge-control
- lounge-control <-> mock-hotel
- lounge-control <-> face-worker
"""

from datetime import datetime, timezone
import re
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
_IDENTIFIER_PATTERN = re.compile(IDENTIFIER_PATTERN)
Identifier = Annotated[str, StringConstraints(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)]
Base64Jpeg = Annotated[str, StringConstraints(min_length=1, max_length=2_800_000)]


def is_valid_identifier(value: str) -> bool:
    """Return whether an opaque protocol identifier has a safe bounded shape."""
    return bool(_IDENTIFIER_PATTERN.fullmatch(value))


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TapEvent(ContractModel):
    """Access event from card reader or simulator."""
    event_id: Identifier = Field(..., description="Unique event identifier for idempotency")
    reader_id: Identifier = Field(..., description="Reader or zone identifier")
    guest_ref: Identifier = Field(..., description="Hotel-internal guest reference token")
    event_type: Literal["entry", "exit"] = Field(..., description="Access action")
    occurred_at: str = Field(..., description="ISO-8601 timestamp")


class DeviceStreamMessage(ContractModel):
    """Message exchanged over the authenticated phone WebSocket."""
    type: Literal["auth", "frame_meta", "frame", "ping", "pong", "session_ack", "error"]
    stream_id: Optional[Identifier] = None
    device_id: Optional[Identifier] = None
    sequence: Optional[int] = Field(None, ge=0)
    captured_at: Optional[str] = None
    format: Literal["image/jpeg"] = "image/jpeg"
    token: Optional[str] = None
    payload_b64: Optional[str] = None
    message: Optional[str] = None

    @model_validator(mode="after")
    def validate_frame_metadata(self):
        if self.type == "frame_meta":
            if not self.stream_id or self.sequence is None or not self.captured_at:
                raise ValueError("frame_meta requires stream_id, sequence, and captured_at")
        if self.type == "frame":
            if not self.stream_id or self.sequence is None or not self.payload_b64:
                raise ValueError("frame requires stream_id, sequence, and payload_b64")
        return self


class MatchEvent(ContractModel):
    """Match update from face-worker, with transient crop bytes when required."""
    candidate_id: Optional[Identifier] = Field(
        None, description="Opaque candidate ID; absent for a no_match cue clear"
    )
    stream_id: Identifier
    track_id: Identifier
    status: Literal["stable_match", "stable_refresh", "unconfirmed", "no_match"]
    device_id: Optional[Identifier] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    crop_id: Optional[Identifier] = None
    crop_b64: Optional[Base64Jpeg] = None
    matched_at: datetime

    @field_validator("matched_at")
    @classmethod
    def require_timezone_aware_match_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("matched_at must include a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def require_candidate_for_stable_events(self):
        if self.status in {"stable_match", "stable_refresh"} and self.candidate_id is None:
            raise ValueError(f"{self.status} requires candidate_id")
        if self.status == "stable_match" and (self.crop_id is None or self.crop_b64 is None):
            raise ValueError("stable_match requires crop_id and crop_b64")
        if self.status == "stable_refresh" and self.crop_id is None:
            raise ValueError("stable_refresh requires crop_id")
        if self.crop_b64 is not None and self.crop_id is None:
            raise ValueError("crop_b64 requires crop_id")
        return self


class CuePayload(ContractModel):
    """Display cue payload for glasses lens."""
    headline: str = Field(..., description="First row: icon + check + name (e.g. '🟢 ✅ ALEX')")
    alert: Optional[str] = Field(None, description="Second row: warning + optional allergen emoji + explicit note")
    guest_ref: Optional[Identifier] = None
    color: str = "green"
    secondary_color: Optional[str] = None


class CueMessage(ContractModel):
    """Glanceable cue message delivered to phone companion app."""
    type: Literal["cue", "clear", "error"]
    stream_id: Identifier
    track_id: Optional[Identifier] = None
    status: Literal["active", "cleared", "suppressed"]
    cue: Optional[CuePayload] = None
    emitted_at: str = Field(default_factory=utc_now_iso)


class DetectedPerson(ContractModel):
    """A stable guest match included in a stream's current detection set."""
    track_id: Identifier
    guest_id: Identifier
    display_name: str = Field(..., min_length=1)
    preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    crop_id: Identifier
    alert: Optional[str] = None


class DetectionSetMessage(ContractModel):
    """Snapshot of currently stable, identified guests on one camera stream."""
    type: Literal["detection_set"]
    stream_id: Identifier
    people: List[DetectedPerson] = Field(default_factory=list)
    emitted_at: str = Field(default_factory=utc_now_iso)


class FaceCropMessage(ContractModel):
    """Transient cropped face image for a track, sent only when it changes."""
    type: Literal["face_crop"]
    stream_id: Identifier
    track_id: Identifier
    crop_id: Identifier
    image_b64: Base64Jpeg
    mime_type: Literal["image/jpeg"] = "image/jpeg"
    emitted_at: str = Field(default_factory=utc_now_iso)


class LoungeProfile(ContractModel):
    """Permitted minimal guest profile exposed by mock-hotel."""
    guest_ref: Identifier
    display_name: str
    room_number: Optional[str] = None
    vip_tier: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    photo_url: Optional[str] = None
    photo_urls: List[str] = Field(default_factory=list)


class CandidateEnrollment(ContractModel):
    """Candidate enrollment into face-worker memory."""
    candidate_id: Identifier
    expires_at: str
    photo_b64: Optional[Base64Jpeg] = None
    photos_b64: List[Base64Jpeg] = Field(default_factory=list, max_length=3)


class GuestRegistrationRequest(ContractModel):
    """Guest registration request for mock-hotel."""
    display_name: str = Field(..., min_length=1, max_length=100)
    room_number: Optional[str] = None
    vip_tier: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    photos_b64: List[Base64Jpeg] = Field(default_factory=list, max_length=3)


class RosterEntry(ContractModel):
    """Active lounge roster entry displaying name and admitted time only."""
    display_name: str
    admitted_at: str
