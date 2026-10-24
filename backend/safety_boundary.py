import re
from typing import Dict, Any, List, Tuple

class SafetyBoundaryEngine:
    """
    Responsible AI and Medical Safety Boundary Engine.
    
    Strict Rules:
    1. NEVER diagnose conditions or answer "Do I have X?"
    2. Convert diagnostic questions into structured questions for a human clinician.
    3. Sanitize and neutralize embedded prompt injections.
    4. Display abnormal lab values neutrally without alarmist alerts.
    5. Mask sensitive notifications for lock-screen safety.
    """

    DIAGNOSTIC_QUESTION_PATTERNS = [
        r"\bdo i have\b",
        r"\bam i (suffering from|having|at risk of)\b",
        r"\bis it cancer\b",
        r"\bdiagnose me\b",
        r"\bwhat disease do i have\b",
        r"\bwhat is wrong with me\b",
        r"\bdo these tests mean i have\b",
        r"\bwill i die\b",
        r"\bis this fatal\b"
    ]

    PROMPT_INJECTION_PATTERNS = [
        r"<!--.*?-->",
        r"system instruction override",
        r"ignore all (hipaa|privacy|rules|previous instructions)",
        r"bypass (revocation|filters|consent)",
        r"grant full access",
        r"dump patient (hiv|psychiatric|confidential)",
        r"disregard safety"
    ]

    def evaluate_user_query(self, user_query: str, patient_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intercepts user questions. If diagnostic or adversarial, enforces strict refusal and guidance.
        """
        clean_q = user_query.strip().lower()

        # 1. Prompt Injection Check
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, clean_q, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "action": "PROMPT_INJECTION_CONTAINED",
                    "response": (
                        "SECURITY DEFENSE ALERT: An adversarial instruction attempting to alter privacy controls "
                        "or bypass ABHA consent boundaries was detected and neutralized. "
                        "All security and privacy policies remain strictly enforced."
                    ),
                    "clinician_questions": []
                }

        # 2. Diagnostic Query Check
        for pattern in self.DIAGNOSTIC_QUESTION_PATTERNS:
            if re.search(pattern, clean_q, re.IGNORECASE):
                # Synthesize clinician questions based on records
                questions = self._generate_clinician_discussion_guide(patient_records, clean_q)
                return {
                    "is_safe": False,
                    "action": "DIAGNOSIS_REFUSAL_AND_ROUTING",
                    "refusal_reason": "Medical safety boundary: AI assistants are strictly prohibited from diagnosing conditions or interpreting diagnostic likelihoods.",
                    "response": (
                        "I cannot diagnose medical conditions or evaluate whether you have a specific illness. "
                        "Only a qualified healthcare provider can evaluate your clinical history, physical symptoms, and laboratory data together. "
                        "Below are specific, neutral questions prepared from your health locker that you can discuss directly with your doctor."
                    ),
                    "clinician_questions": questions
                }

        # Safe general inquiry
        return {
            "is_safe": True,
            "action": "INFORMATIONAL_ORGANIZER",
            "response": (
                "Here is an organized overview of your health documents and timelines. "
                "All items are sourced directly from your verified diagnostic providers."
            ),
            "clinician_questions": []
        }

    def _generate_clinician_discussion_guide(self, records: List[Dict[str, Any]], query: str) -> List[str]:
        questions = []
        for r in records:
            if r.get("category") == "diagnostic_lab":
                for p in r.get("parameters", []):
                    if "Abnormal" in p.get("flag", ""):
                        questions.append(
                            f"Ask Doctor: 'My recent lab from {r.get('provider')} showed {p['name']} at {p['value']} {p['unit']} (reference range: {p['ref_range']}). How does this fit into my overall care plan?'"
                        )
        if not questions:
            questions.append("Ask Doctor: 'Could you review my latest test reports with me and help me understand what subsequent steps or lifestyle adjustments are recommended?'")
        return questions[:3]

    def sanitize_lock_screen_notification(self, raw_message: str, is_sensitive: bool = False) -> Dict[str, str]:
        """
        Produces a dual-layer notification:
        - Lock screen view: 100% PII and clinical condition free.
        - In-app authenticated view: full contextual information.
        """
        lock_screen_text = "ABHA Health Locker: You have a new health record update. Unlock device to review."
        if is_sensitive:
            lock_screen_text = "ABHA Security Notice: New confidential document activity. Biometric sign-in required."

        return {
            "lock_screen_text": lock_screen_text,
            "authenticated_text": raw_message,
            "is_sanitized": True
        }

    def format_lab_value_neutrally(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """
        Displays abnormal values with purely factual reference ranges.
        Strictly forbids alarming red hazard icons, flashing banners, or anxiety-inducing copy.
        """
        return {
            "name": param.get("name"),
            "value": param.get("value"),
            "unit": param.get("unit"),
            "reference_range": param.get("ref_range"),
            "source_flag": param.get("flag", "Standard"),
            "display_tone": "NEUTRAL_INFORMATIVE",
            "interpretation_statement": "Displayed strictly as recorded by testing facility. Clinical significance must be determined by your treating physician."
        }
