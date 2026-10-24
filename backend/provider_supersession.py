from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

class ProviderSupersessionManager:
    """
    Elite Dimension: Provider Correction & Supersession Propagation Engine.
    When a diagnostic center or clinician amends an existing report:
    1. The target record is stamped with a non-destructive SUPERSEDED marker.
    2. Historical lineage is maintained (original is never deleted).
    3. All active shares/consents containing the superseded record receive an automated amendment broadcast.
    """

    def __init__(self, records: List[Dict[str, Any]], consent_manager, audit_trail):
        self.records = records
        self.consent_manager = consent_manager
        self.audit_trail = audit_trail
        self.broadcast_log: List[Dict[str, Any]] = []

    def apply_supersession(self, superseded_id: str, new_record: Dict[str, Any], reason: str) -> Dict[str, Any]:
        target_record = None
        for r in self.records:
            if r["id"] == superseded_id:
                target_record = r
                break

        if not target_record:
            return {"success": False, "error": f"Record {superseded_id} not found."}

        # 1. Update target record metadata
        target_record["superseded_by"] = new_record["id"]
        target_record["is_superseded"] = True
        target_record["superseded_at"] = datetime.now(timezone.utc).isoformat()
        target_record["supersession_reason"] = reason

        # 2. Add amendment lineage to new record
        new_record["supersedes"] = superseded_id
        new_record["amendment_reason"] = reason

        # 3. Identify all active shares holding the old record
        affected_consents = []
        for c in self.consent_manager.list_consents():
            if c.get("status") == "Active":
                perm_ids = c.get("permitted_record_ids", [])
                if not perm_ids or superseded_id in perm_ids:
                    affected_consents.append(c)

        # 4. Dispatch notification broadcast to affected recipients
        broadcast_events = []
        for c in affected_consents:
            b_event = {
                "broadcast_id": f"BC-{uuid.uuid4().hex[:6]}",
                "consent_id": c["id"],
                "recipient_name": c["recipient_name"],
                "superseded_record_id": superseded_id,
                "replacement_record_id": new_record["id"],
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notice_text": (
                    f"CLINICAL AMENDMENT NOTICE: Record '{target_record.get('title')}' ({superseded_id}) "
                    f"has been superseded by an updated report ({new_record['id']}). "
                    f"Reason: {reason}. Both versions remain inspectable with full audit provenance."
                )
            }
            self.broadcast_log.append(b_event)
            broadcast_events.append(b_event)

            # Auto-include the replacement record in the recipient's permitted list
            if "permitted_record_ids" in c and c["permitted_record_ids"]:
                if new_record["id"] not in c["permitted_record_ids"]:
                    c["permitted_record_ids"].append(new_record["id"])

        # 5. Log in append-only audit trail
        self.audit_trail.record_event(
            action="RECORD_SUPERSEDED_AND_PROPAGATED",
            actor=f"PROVIDER:{new_record.get('provider')}",
            details={
                "superseded_id": superseded_id,
                "new_record_id": new_record["id"],
                "reason": reason,
                "shares_notified_count": len(affected_consents)
            }
        )

        return {
            "success": True,
            "superseded_id": superseded_id,
            "new_record_id": new_record["id"],
            "affected_shares_count": len(affected_consents),
            "broadcast_events": broadcast_events
        }

    def get_broadcasts(self) -> List[Dict[str, Any]]:
        return self.broadcast_log
