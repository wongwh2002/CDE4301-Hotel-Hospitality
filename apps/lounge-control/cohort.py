"""In-memory active lounge cohort manager.

Tracks guests currently present in the lounge:
- In-memory state with TTL expiry
- Idempotent event handling for card reader taps
- Never persists photos, crops, or derived templates
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


class ActiveCohortManager:
    def __init__(self):
        # candidate_id -> guest display data
        self._cohort: Dict[str, Dict[str, Any]] = {}
        # guest_ref -> Set[candidate_id]
        self._guest_to_candidates: Dict[str, Set[str]] = {}
        # event_id -> timestamp (for idempotency)
        self._processed_events: Dict[str, Dict[str, Any]] = {}

    def is_event_processed(self, event_id: str) -> Optional[Dict[str, Any]]:
        return self._processed_events.get(event_id)

    def record_event_processed(self, event_id: str, outcome: Dict[str, Any]) -> None:
        self._processed_events[event_id] = outcome

    def get_candidate_for_guest(self, guest_ref: str) -> Optional[str]:
        """Return active candidate ID for guest_ref if present."""
        self.clean_expired()
        cids = self._guest_to_candidates.get(guest_ref)
        if cids:
            return next(iter(cids))
        return None

    def has_guest(self, guest_ref: str) -> bool:
        """Return whether guest_ref has an active presence in the lounge."""
        return self.get_candidate_for_guest(guest_ref) is not None

    def admit_candidate(
        self,
        candidate_id: str,
        guest_ref: str,
        display_name: str,
        room_number: Optional[str],
        allergies: List[str],
        preferences: List[str],
        expires_at: str,
    ) -> Dict[str, Any]:
        """Admit a guest into the active lounge cohort.

        Enforces at most one active presence per guest_ref.
        """
        self.clean_expired()
        # Enforce at most one active presence per guest_ref
        if guest_ref in self._guest_to_candidates:
            for old_cid in list(self._guest_to_candidates[guest_ref]):
                self._cohort.pop(old_cid, None)
            self._guest_to_candidates[guest_ref].clear()

        now_iso = datetime.now(timezone.utc).isoformat()
        record = {
            "candidate_id": candidate_id,
            "guest_ref": guest_ref,
            "display_name": display_name,
            "room_number": room_number,
            "allergies": list(allergies),
            "preferences": list(preferences),
            "admitted_at": now_iso,
            "expires_at": expires_at,
        }
        self._cohort[candidate_id] = record

        if guest_ref not in self._guest_to_candidates:
            self._guest_to_candidates[guest_ref] = set()
        self._guest_to_candidates[guest_ref].add(candidate_id)
        return record

    def depart_guest(self, guest_ref: str) -> List[str]:
        """Remove all active candidates for a departing guest."""
        self.clean_expired()
        candidate_ids = list(self._guest_to_candidates.get(guest_ref, set()))
        for cid in candidate_ids:
            if cid in self._cohort:
                del self._cohort[cid]
        if guest_ref in self._guest_to_candidates:
            del self._guest_to_candidates[guest_ref]
        return candidate_ids

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        self.clean_expired()
        return self._cohort.get(candidate_id)

    def clean_expired(self) -> List[str]:
        """Remove candidates whose presence TTL has expired."""
        now_iso = datetime.now(timezone.utc).isoformat()
        expired_ids = [
            cid for cid, rec in self._cohort.items()
            if rec.get("expires_at") and rec["expires_at"] < now_iso
        ]
        for cid in expired_ids:
            rec = self._cohort.pop(cid, None)
            if rec and rec["guest_ref"] in self._guest_to_candidates:
                self._guest_to_candidates[rec["guest_ref"]].discard(cid)
                if not self._guest_to_candidates[rec["guest_ref"]]:
                    del self._guest_to_candidates[rec["guest_ref"]]
        return expired_ids

    def get_roster(self) -> List[Dict[str, str]]:
        """Return active roster with display_name and admitted_at only."""
        self.clean_expired()
        sorted_records = sorted(
            self._cohort.values(),
            key=lambda rec: rec.get("admitted_at", ""),
        )
        return [
            {
                "display_name": rec["display_name"],
                "admitted_at": rec["admitted_at"],
            }
            for rec in sorted_records
        ]

    def get_summary(self) -> List[Dict[str, Any]]:
        """Return non-sensitive summary of active cohort."""
        self.clean_expired()
        return [
            {
                "candidate_id": rec["candidate_id"],
                "admitted_at": rec["admitted_at"],
                "expires_at": rec["expires_at"],
            }
            for rec in self._cohort.values()
        ]

    def size(self) -> int:
        self.clean_expired()
        return len(self._cohort)
