from typing import List, Dict, Any, Optional
from datetime import datetime

class TimelineEngine:
    """
    Longitudinal timeline organizer that strictly separates:
    - Event Date: Date when the clinical specimen or examination was conducted
    - Report Date: Date when the diagnostic facility issued the verified report
    - Upload Date: Date when the record was ingested into the ABHA health locker
    
    Strictly flags date discrepancies without silently rewriting them.
    """

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def parse_iso(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            # Strip trailing Z for standard ISO parsing
            clean = date_str.replace("Z", "+00:00")
            return datetime.fromisoformat(clean)
        except Exception:
            return None

    def analyze_record_dates(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects chronological sanity across Event, Report, and Upload dates.
        """
        ev_dt = self.parse_iso(record.get("event_date"))
        rep_dt = self.parse_iso(record.get("report_date"))
        up_dt = self.parse_iso(record.get("upload_date"))

        anomalies = []
        is_conflicted = False

        if ev_dt and rep_dt and ev_dt > rep_dt:
            anomalies.append({
                "type": "CHRONOLOGY_INVERSION",
                "message": f"Event date ({record['event_date'][:10]}) is after Report date ({record['report_date'][:10]}). Likely OCR distortion or incorrect scan metadata."
            })
            is_conflicted = True

        if ev_dt and up_dt and ev_dt > up_dt:
            anomalies.append({
                "type": "FUTURE_EVENT_DATE",
                "message": f"Event date ({record['event_date'][:10]}) is recorded after Upload date ({record['upload_date'][:10]}). User-entered metadata discrepancy."
            })
            is_conflicted = True

        # Check for supersession
        is_superseded = "superseded_by" in record

        return {
            "record_id": record["id"],
            "title": record.get("title"),
            "event_date": record.get("event_date"),
            "report_date": record.get("report_date"),
            "upload_date": record.get("upload_date"),
            "provider": record.get("provider"),
            "city": record.get("city"),
            "is_conflicted": is_conflicted,
            "is_superseded": is_superseded,
            "superseded_by": record.get("superseded_by"),
            "supersedes": record.get("supersedes"),
            "anomalies": anomalies
        }

    def build_longitudinal_timeline(self) -> List[Dict[str, Any]]:
        """
        Returns records sorted chronologically by primary Event Date.
        Conflicted or superseded records carry explicit badges.
        """
        timeline_items = []
        for r in self.records:
            date_meta = self.analyze_record_dates(r)
            timeline_items.append({
                **r,
                "date_metadata": date_meta
            })

        def sort_key(item):
            # Sort by event_date if available, else report_date, else upload_date
            return item.get("event_date") or item.get("report_date") or item.get("upload_date") or ""

        timeline_items.sort(key=sort_key, reverse=True)
        return timeline_items
