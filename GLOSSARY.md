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

**Detection set**:
A snapshot of the stable, identified guest tracks currently reported in one camera stream.
