# Hotel Smart-Glasses POC

This context explores how a hotel worker could receive relevant guest context while serving guests in a lounge.

## Language

**Active lounge cohort**:
A group of guests currently treated as present in one lounge. A guest has one active presence from entry until exit or presence expiry.

**Frame replay**:
A test input that sends a prepared sequence of synthetic or consented camera frames through the same device-frame interface used by the phone bridge, once per run.
_Avoid_: Live camera stream

**Track ID (`track_id`)**:
A temporary identifier for one face track within a camera stream. It helps associate detection updates and clears with the same tracked face; it is not a guest identifier.

**Crop ID (`crop_id`)**:
An opaque reference to a cropped face image sent when a track first appears or its crop changes. The client caches the image for the track's TTL.

**Guest ID (`guest_id`)**:
An opaque identifier for a hotel guest profile. It identifies the guest record and is distinct from a temporary track ID.

**Service preference**:
A short guest preference that can help with a service interaction, such as a preferred drink. Allergies are safety alerts and are represented separately from preferences.

**Detection set**:
A snapshot of the stable, identified people currently reported in one camera stream. Each entry represents a face track, so people with the same name remain separate.

**Detection TTL (time-to-live)**:
The time after the last stable identity observation before lounge-control removes its cached result and crop. The POC target is five seconds; transient `no_match` and `unconfirmed` observations neither extend nor immediately clear that stable result.

**Suggested match**:
A guest identity proposed by face recognition for a face track. It remains provisional until a staff member confirms it.

**Confirmed match**:
A suggested face-to-guest association explicitly checked by a staff member. Guest-specific service context should be treated as reliable only after confirmation.
