import http.server
import socketserver
import json
import os
import sys
import urllib.parse
from typing import Dict, Any

# Ensure backend and eval imports work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from backend.audit_trail import AuditTrailLedger
from backend.timeline_engine import TimelineEngine
from backend.duplicate_engine import DuplicateDetectionEngine
from backend.medication_reconciliation import MedicationReconciliationEngine
from backend.consent_ledger import ConsentLedgerManager
from backend.break_glass import BreakGlassManager
from backend.provider_supersession import ProviderSupersessionManager
from backend.safety_boundary import SafetyBoundaryEngine
from backend.fault_injector import FaultInjector
from eval.test_harness import run_evaluation_suite
import zipfile
import io

PORT = 8080

class HealthJourneyState:
    def __init__(self):
        self.data_path = os.path.join(CURRENT_DIR, "data", "seeded_dataset.json")
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        
        self.patient_info = raw["dataset_metadata"]["patient"]
        self.records = raw["records"]
        self.seeded_consents = raw["seeded_consents"]
        
        # Core engines
        self.audit_trail = AuditTrailLedger()
        self.safety_engine = SafetyBoundaryEngine()
        self.fault_injector = FaultInjector(self.audit_trail)
        self.consent_mgr = ConsentLedgerManager(self.seeded_consents, self.audit_trail)
        self.break_glass_mgr = BreakGlassManager(self.audit_trail)
        self.timeline_engine = TimelineEngine(self.records)
        self.duplicate_engine = DuplicateDetectionEngine(self.records)
        self.med_recon = MedicationReconciliationEngine(self.records)
        self.supersession_mgr = ProviderSupersessionManager(self.records, self.consent_mgr, self.audit_trail)

        # Audit initial bootstrap
        self.audit_trail.record_event(
            action="VAULT_BOOTSTRAP_COMPLETE",
            actor="ABHA_INITIALIZER",
            details={"patient_id": self.patient_info["abha_id"], "records_count": len(self.records)}
        )

STATE = HealthJourneyState()

class HealthJourneyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(CURRENT_DIR, "app"), **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # Check judge fault injection
        fault_res = STATE.fault_injector.handle_request(path)
        if fault_res and path.startswith("/api/") and path != "/api/faults" and not path.startswith("/api/faults/"):
            self._send_json(fault_res, status=fault_res.get("http_code", 500))
            return

        if path == "/api/status":
            self._send_json({
                "service": "ABHA Health Journey Organizer",
                "status": "OPERATIONAL",
                "patient": STATE.patient_info,
                "records_count": len(STATE.records),
                "faults": STATE.fault_injector.get_status()
            })
            return

        elif path == "/api/records":
            persona = params.get("persona", ["patient"])[0]
            # Filter according to persona
            if persona == "caregiver":
                # Caregiver view: exclude sensitive categories
                filtered = [r for r in STATE.records if not r.get("is_sensitive", False)]
                self._send_json({"persona": "caregiver", "records": filtered})
            elif persona == "specialist":
                # Specialist with CONSENT-701
                allowed = []
                for r in STATE.records:
                    chk = STATE.consent_mgr.check_access("CONSENT-701", r, "Dr. Rajesh Mehta")
                    if chk["allowed"]:
                        allowed.append(r)
                self._send_json({"persona": "specialist", "consent_id": "CONSENT-701", "records": allowed})
            elif persona == "emergency":
                # Emergency break-glass view
                sessions = STATE.break_glass_mgr.get_active_sessions()
                if not sessions:
                    self._send_json({"persona": "emergency", "records": [], "active_session": None})
                else:
                    active_sess = sessions[-1]
                    filtered = STATE.break_glass_mgr.filter_emergency_records(active_sess["session_id"], STATE.records)
                    self._send_json({"persona": "emergency", "active_session": active_sess, "records": filtered})
            else:
                self._send_json({"persona": "patient", "records": STATE.records})
            return

        elif path == "/api/timeline":
            items = STATE.timeline_engine.build_longitudinal_timeline()
            self._send_json({"timeline": items, "total": len(items)})
            return

        elif path == "/api/duplicates":
            pairs = STATE.duplicate_engine.detect_all_duplicates()
            self._send_json({"duplicates": pairs, "total_pairs": len(pairs), "silent_merge_forbidden": True})
            return

        elif path == "/api/medications/reconcile":
            recon = STATE.med_recon.reconcile()
            self._send_json(recon)
            return

        elif path == "/api/consents":
            consents = STATE.consent_mgr.list_consents()
            self._send_json({"consents": consents})
            return

        elif path == "/api/break-glass/status":
            self._send_json({
                "active_sessions": STATE.break_glass_mgr.get_active_sessions(),
                "dispatched_alerts": STATE.break_glass_mgr.get_alerts()
            })
            return

        elif path == "/api/audit/logs":
            logs = STATE.audit_trail.get_logs(limit=100)
            valid, msg = STATE.audit_trail.verify_integrity()
            self._send_json({
                "integrity_valid": valid,
                "integrity_message": msg,
                "total_blocks": len(STATE.audit_trail.chain),
                "logs": logs
            })
            return

        elif path == "/api/audit/verify":
            valid, msg = STATE.audit_trail.verify_integrity()
            self._send_json({"valid": valid, "verification_message": msg, "chain_length": len(STATE.audit_trail.chain)})
            return

        elif path == "/api/faults":
            self._send_json(STATE.fault_injector.get_status())
            return

        elif path == "/api/eval/run":
            eval_results = run_evaluation_suite()
            self._send_json(eval_results)
            return

        elif path == "/api/download/project-zip":
            # Generate in-memory ZIP of entire codebase
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(CURRENT_DIR):
                    # Skip __pycache__ and .git if any
                    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".pytest_cache")]
                    for file in files:
                        if file.endswith((".pyc", ".pyo", ".zip")):
                            continue
                        abs_file = os.path.join(root, file)
                        rel_file = os.path.relpath(abs_file, CURRENT_DIR)
                        zf.write(abs_file, os.path.join("health-journey-abdm", rel_file))
            
            buffer.seek(0)
            zip_bytes = buffer.getvalue()

            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="health-journey-abdm.zip"')
            self.send_header("Content-Length", str(len(zip_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(zip_bytes)
            return

        # Serve static UI files (index.html, styles.css, app.js)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Read JSON body
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # Judge Fault check
        fault_res = STATE.fault_injector.handle_request(path, payload)
        if fault_res and not path.startswith("/api/faults"):
            self._send_json(fault_res, status=fault_res.get("http_code", 500))
            return

        if path == "/api/consents/revoke":
            consent_id = payload.get("consent_id", "CONSENT-701")
            try:
                receipt = STATE.consent_mgr.revoke_consent(consent_id)
                self._send_json({"success": True, "revocation_receipt": receipt})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=400)
            return

        elif path == "/api/break-glass/trigger":
            hosp = payload.get("hospital_name", "Max Super Speciality Hospital, Delhi")
            doc = payload.get("practitioner_id", "DOC-ER-991")
            just = payload.get("clinical_justification", "Unconscious polytrauma presentation")
            override = payload.get("override_sensitive", False)
            res = STATE.break_glass_mgr.trigger_emergency_access(hosp, doc, just, override_sensitive=override)
            self._send_json(res)
            return

        elif path == "/api/supersession/apply":
            # Ingest amended lab report REC-006 to supersede REC-005
            rec6 = next((r for r in STATE.records if r["id"] == "REC-006"), None)
            reason = payload.get("reason", "Analyzer reagent baseline calibration correction applied by laboratory director.")
            if rec6:
                res = STATE.supersession_mgr.apply_supersession("REC-005", rec6, reason)
                self._send_json(res)
            else:
                self._send_json({"success": False, "error": "Amended record REC-006 not found"}, status=404)
            return

        elif path == "/api/safety/ask":
            query = payload.get("query", "")
            eval_res = STATE.safety_engine.evaluate_user_query(query, STATE.records)
            STATE.audit_trail.record_event(
                action="SAFETY_QUERY_EVALUATED",
                actor="PATIENT_CHAT",
                details={"query": query, "action": eval_res["action"], "is_safe": eval_res["is_safe"]}
            )
            self._send_json(eval_res)
            return

        elif path == "/api/duplicates/link":
            rec_a = payload.get("record_a_id")
            rec_b = payload.get("record_b_id")
            STATE.audit_trail.record_event(
                action="RECORDS_LINKED_KEEP_BOTH",
                actor="PATIENT_ACTION",
                details={"record_a": rec_a, "record_b": rec_b, "policy": "ZERO_SILENT_MERGES"}
            )
            self._send_json({"success": True, "action": "KEEP_BOTH_AND_LINK", "linked_pair": [rec_a, rec_b]})
            return

        elif path == "/api/faults/set":
            fault_name = payload.get("fault_name")
            enabled = payload.get("enabled", False)
            res = STATE.fault_injector.set_fault(fault_name, enabled)
            self._send_json(res)
            return

        elif path == "/api/faults/reset":
            res = STATE.fault_injector.reset_all_faults()
            self._send_json(res)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

def run_server():
    server_address = ("", PORT)
    httpd = socketserver.ThreadingTCPServer(server_address, HealthJourneyRequestHandler)
    httpd.allow_reuse_address = True
    print(f"\n=======================================================")
    print(f"  ABHA Digital Health Journey Server is LIVE")
    print(f"  Local URL : http://localhost:{PORT}")
    print(f"  API Docs  : http://localhost:{PORT}/api/status")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
