import hashlib
import json
import time
from typing import Dict, Any, List, Tuple

class AuditTrailLedger:
    """
    Append-only, SHA-256 hash-chained tamper-evident audit ledger.
    Every single state transition, consent grant, revocation, access attempt,
    break-glass event, and provider amendment is hashed into the chain:
    Hash_N = SHA256(index + timestamp + action + actor + details + prev_hash)
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self._init_genesis()

    def _init_genesis(self):
        genesis_entry = {
            "index": 0,
            "timestamp": "2026-10-24T00:00:00Z",
            "action": "LEDGER_GENESIS",
            "actor": "ABHA_SYSTEM_VAULT",
            "patient_id": "SYSTEM",
            "details": {"message": "ABHA Tamper-Evident Audit Ledger initialized."},
            "prev_hash": self.GENESIS_HASH,
            "hash": ""
        }
        genesis_entry["hash"] = self._compute_hash(genesis_entry)
        self.chain.append(genesis_entry)

    def _compute_hash(self, entry: Dict[str, Any]) -> str:
        payload = f"{entry['index']}|{entry['timestamp']}|{entry['action']}|{entry['actor']}|{entry['patient_id']}|{json.dumps(entry['details'], sort_keys=True)}|{entry['prev_hash']}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_event(self, action: str, actor: str, details: Dict[str, Any], patient_id: str = "91-4421-8890-1234") -> Dict[str, Any]:
        prev_entry = self.chain[-1]
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        index = len(self.chain)

        entry = {
            "index": index,
            "timestamp": timestamp,
            "action": action,
            "actor": actor,
            "patient_id": patient_id,
            "details": details,
            "prev_hash": prev_entry["hash"],
            "hash": ""
        }
        entry["hash"] = self._compute_hash(entry)
        self.chain.append(entry)
        return entry

    def verify_integrity(self) -> Tuple[bool, str]:
        """
        Verifies that no entry has been altered, inserted, or deleted.
        """
        if not self.chain:
            return False, "Chain is empty"

        for i in range(len(self.chain)):
            entry = self.chain[i]
            expected_hash = self._compute_hash(entry)
            if entry["hash"] != expected_hash:
                return False, f"Tamper detected at index {i}: Hash mismatch. Expected {expected_hash}, found {entry['hash']}"
            if i > 0:
                prev_entry = self.chain[i - 1]
                if entry["prev_hash"] != prev_entry["hash"]:
                    return False, f"Broken chain link at index {i}: prev_hash does not match hash of entry {i-1}"

        return True, f"Ledger integrity verified: all {len(self.chain)} blocks are cryptographically valid."

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self.chain[-limit:]))
