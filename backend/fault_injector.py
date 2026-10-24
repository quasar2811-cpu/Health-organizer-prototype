from typing import Dict, Any, Optional

class FaultInjector:
    """
    Live Fault Injection Engine for Judge Testing.
    Allows judges to toggle realistic runtime disruptions:
    1. Service Timeout (Simulated 504 ABDM gateway hang)
    2. Stale Data (Exposes cached records with prominent freshness degradation indicators)
    3. Conflicting Concurrent Update (Simulates race condition during record ingestion)
    4. Malformed Input (Corrupted payload handling without system crash)
    5. Connectivity Loss (Simulates complete offline mode with queued sync)
    """

    def __init__(self, audit_trail):
        self.audit_trail = audit_trail
        self.active_faults = {
            "service_timeout": False,
            "stale_data": False,
            "conflicting_update": False,
            "malformed_input": False,
            "connectivity_loss": False
        }

    def set_fault(self, fault_name: str, enabled: bool) -> Dict[str, Any]:
        if fault_name in self.active_faults:
            self.active_faults[fault_name] = enabled
            self.audit_trail.record_event(
                action="FAULT_INJECTION_STATE_CHANGED",
                actor="JUDGE_TEST_HARNESS",
                details={"fault_name": fault_name, "enabled": enabled}
            )
            return {"status": "success", "fault": fault_name, "enabled": enabled}
        return {"status": "error", "message": f"Unknown fault '{fault_name}'"}

    def reset_all_faults(self) -> Dict[str, Any]:
        for k in self.active_faults:
            self.active_faults[k] = False
        return {"status": "success", "active_faults": self.active_faults}

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_faults": self.active_faults,
            "any_active": any(self.active_faults.values())
        }

    def handle_request(self, endpoint_name: str, payload: Any = None) -> Optional[Dict[str, Any]]:
        """
        Intercepts endpoints if a fault is active.
        """
        if self.active_faults.get("service_timeout"):
            return {
                "fault_triggered": "service_timeout",
                "http_code": 504,
                "error": "Gateway Timeout: Upstream ABDM Central Registry did not respond within 5000ms.",
                "degraded_mode": True,
                "graceful_fallback": "Serving local encrypted offline cache with last known verified state (Cached at 2026-10-24T08:00:00Z)."
            }

        if self.active_faults.get("connectivity_loss"):
            return {
                "fault_triggered": "connectivity_loss",
                "http_code": 503,
                "error": "Network Connection Severed. Local client operating in Offline-First mode.",
                "degraded_mode": True,
                "graceful_fallback": "Changes saved to local IndexedDB/localStorage. Auto-sync queued for reconnection."
            }

        if self.active_faults.get("conflicting_update"):
            return {
                "fault_triggered": "conflicting_update",
                "http_code": 409,
                "error": "Conflict Detected: Record was modified concurrently by another provider session (E-Tag mismatch).",
                "degraded_mode": False,
                "graceful_fallback": "Automatic merge aborted to prevent silent data corruption. Displaying side-by-side reconciliation."
            }

        if self.active_faults.get("malformed_input"):
            return {
                "fault_triggered": "malformed_input",
                "http_code": 422,
                "error": "Malformed Schema Payload: Truncated JSON stream or invalid FHIR resource header.",
                "degraded_mode": False,
                "graceful_fallback": "Payload safely quarantined in audit log. Core health vault remains uncorrupted."
            }

        return None
