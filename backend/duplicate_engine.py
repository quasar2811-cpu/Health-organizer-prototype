from typing import List, Dict, Any, Tuple, Optional
import difflib

class DuplicateDetectionEngine:
    """
    Explainable duplicate and near-duplicate detector.
    
    Hard Principle:
    NEVER silently merge or delete clinical records.
    Every detected near-duplicate or exact re-scan is linked explicitly
    via 'KEEP_BOTH_AND_LINK' with explainable similarity scores and provenance.
    """

    DUPLICATE_THRESHOLD = 0.80

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").lower().strip().split())

    def _compute_text_similarity(self, s1: str, s2: str) -> float:
        matcher = difflib.SequenceMatcher(None, self._normalize_text(s1), self._normalize_text(s2))
        return matcher.ratio()

    def _extract_parameter_fingerprint(self, record: Dict[str, Any]) -> Dict[str, str]:
        params = {}
        for p in record.get("parameters", []):
            name = self._normalize_text(p.get("name", ""))
            val = self._normalize_text(str(p.get("value", "")))
            if name:
                params[name] = val
        return params

    def compare_records(self, rec_a: Dict[str, Any], rec_b: Dict[str, Any]) -> Tuple[float, List[str]]:
        if rec_a["id"] == rec_b["id"]:
            return 1.0, ["Identical record reference"]

        reasons = []

        # 1. Parameter Value Match (weight: 0.50)
        params_a = self._extract_parameter_fingerprint(rec_a)
        params_b = self._extract_parameter_fingerprint(rec_b)
        param_sim = 0.0

        if params_a and params_b:
            common_keys = set(params_a.keys()).intersection(set(params_b.keys()))
            if common_keys:
                matching_values = sum(1 for k in common_keys if params_a[k] == params_b[k])
                # Subset / containment ratio: re-scans often contain a subset of original panel
                param_sim = matching_values / min(len(params_a), len(params_b))
                reasons.append(f"{matching_values} clinical lab parameters match identically ({param_sim * 100:.1f}%)")

        # 2. Provider match (weight: 0.30)
        prov_sim = self._compute_text_similarity(rec_a.get("provider", ""), rec_b.get("provider", ""))
        if prov_sim > 0.7:
            reasons.append(f"Matching diagnostic provider: '{rec_a.get('provider')}'")

        # 3. Title / Keyword match (weight: 0.20)
        title_sim = self._compute_text_similarity(rec_a.get("title", ""), rec_b.get("title", ""))
        tokens_a = set(self._normalize_text(rec_a.get("title", "")).split())
        tokens_b = set(self._normalize_text(rec_b.get("title", "")).split())
        if tokens_a and tokens_b:
            jaccard = len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))
            title_sim = max(title_sim, jaccard)
        if title_sim > 0.2:
            reasons.append(f"Related clinical test domain ({title_sim * 100:.1f}%)")

        overall_score = (param_sim * 0.50) + (prov_sim * 0.30) + (title_sim * 0.20)
        return round(overall_score, 3), reasons

    def detect_all_duplicates(self) -> List[Dict[str, Any]]:
        """
        Scans all records and pairs near-duplicates.
        Strictly returns candidate pairs with explainable reasoning and
        mandates the 'KEEP_BOTH_AND_LINK' action. Zero silent merges.
        """
        detected_pairs = []
        n = len(self.records)

        for i in range(n):
            for j in range(i + 1, n):
                rec_a = self.records[i]
                rec_b = self.records[j]

                score, reasons = self.compare_records(rec_a, rec_b)
                if score >= self.DUPLICATE_THRESHOLD:
                    detected_pairs.append({
                        "record_a_id": rec_a["id"],
                        "record_b_id": rec_b["id"],
                        "record_a_title": rec_a.get("title"),
                        "record_b_title": rec_b.get("title"),
                        "similarity_score": score,
                        "confidence_percentage": f"{score * 100:.1f}%",
                        "explainable_reasons": reasons,
                        "recommended_action": "KEEP_BOTH_AND_LINK",
                        "silent_merge_forbidden": True,
                        "provenance_note": (
                            f"Record {rec_b['id']} appears to be a re-scan or duplicate of {rec_a['id']}. "
                            f"Original clinical timestamps preserved without in-place modification."
                        )
                    })

        return detected_pairs
