from typing import List, Dict, Any

class MedicationReconciliationEngine:
    """
    Cross-prescription reconciliation engine.
    
    Hard Constraint:
    Discrepancies are NEVER presented as medical advice or therapeutic recommendations.
    All outputs are strictly formatted as structured questions for a human clinician.
    """

    KNOWN_DRUG_CLASSES = {
        "telmisartan": "ARB (Angiotensin II Receptor Blocker)",
        "losartan": "ARB (Angiotensin II Receptor Blocker)",
        "valsartan": "ARB (Angiotensin II Receptor Blocker)",
        "metformin": "Biguanide (Antidiabetic)",
        "glimepiride": "Sulfonylurea (Antidiabetic)",
        "escitalopram": "SSRI (Antidepressant)"
    }

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def extract_prescriptions(self) -> List[Dict[str, Any]]:
        prescriptions = []
        for r in self.records:
            if r.get("category") == "prescription" or r.get("medications"):
                prescriptions.append(r)
        return prescriptions

    def reconcile(self) -> Dict[str, Any]:
        prescriptions = self.extract_prescriptions()
        active_meds = []
        clinician_questions = []
        ocr_uncertainties = []
        class_duplications = []

        seen_classes: Dict[str, List[Dict[str, Any]]] = {}

        for p in prescriptions:
            provider = p.get("provider", "Unknown Clinic")
            doctor = p.get("doctor", "Unknown Doctor")
            event_date = p.get("event_date", "")[:10]

            for m in p.get("medications", []):
                med_name = m.get("name", "")
                norm_name = med_name.lower().split()[0]
                dose = m.get("extracted_dose", "")
                freq = m.get("extracted_frequency", "")
                ocr_conf = m.get("ocr_confidence", 1.0)
                is_ambig = m.get("is_ambiguous", False)

                med_item = {
                    "prescription_id": p["id"],
                    "provider": provider,
                    "doctor": doctor,
                    "date": event_date,
                    "medication_name": med_name,
                    "dose": dose,
                    "frequency": freq,
                    "ocr_confidence": ocr_conf,
                    "is_ambiguous": is_ambig
                }
                active_meds.append(med_item)

                # 1. OCR Confidence check
                if is_ambig or ocr_conf < 0.70:
                    ocr_uncertainties.append({
                        "prescription_id": p["id"],
                        "doctor": doctor,
                        "medication": med_name,
                        "raw_ocr": m.get("raw_ocr_text", ""),
                        "ocr_confidence": f"{ocr_conf * 100:.1f}%",
                        "ambiguity_reason": m.get("ambiguity_reason", "Low character confidence on handwritten dosage numeral."),
                        "suggested_clinician_question": (
                            f"Prescription from {doctor} on {event_date} lists {med_name} with uncertain handwritten dose ({dose}). "
                            f"Could you verify the intended daily dose and confirm if {dose} is accurate?"
                        )
                    })

                # 2. Class Duplication check
                drug_class = self.KNOWN_DRUG_CLASSES.get(norm_name)
                if drug_class:
                    if drug_class not in seen_classes:
                        seen_classes[drug_class] = []
                    seen_classes[drug_class].append(med_item)

        # Evaluate duplicate therapeutic classes across separate prescriptions
        for d_class, meds in seen_classes.items():
            if len(meds) > 1:
                # Grouped across distinct prescriptions
                unique_rx = set(m["prescription_id"] for m in meds)
                if len(unique_rx) > 1:
                    m1 = meds[0]
                    m2 = meds[1]
                    class_duplications.append({
                        "drug_class": d_class,
                        "medications_involved": [
                            f"{m1['medication_name']} ({m1['dose']}) from {m1['doctor']} ({m1['date']})",
                            f"{m2['medication_name']} ({m2['dose']}) from {m2['doctor']} ({m2['date']})"
                        ],
                        "suggested_clinician_question": (
                            f"You currently have prescriptions for both {m1['medication_name']} (from {m1['doctor']}) "
                            f"and {m2['medication_name']} (from {m2['doctor']}), both belonging to the {d_class} family. "
                            f"Ask your doctor: 'Should I continue taking both, or was {m2['medication_name']} meant to replace {m1['medication_name']}?'"
                        )
                    })

        # Compile structured clinician questions
        for u in ocr_uncertainties:
            clinician_questions.append({
                "type": "OCR_DOSAGE_CONFIRMATION",
                "question": u["suggested_clinician_question"],
                "source_record": u["prescription_id"],
                "confidence": u["ocr_confidence"]
            })

        for c in class_duplications:
            clinician_questions.append({
                "type": "THERAPEUTIC_CLASS_OVERLAP",
                "question": c["suggested_clinician_question"],
                "source_records": [m.split()[0] for m in c["medications_involved"]],
                "confidence": "High (Rule-based)"
            })

        return {
            "active_medications": active_meds,
            "ocr_uncertainties": ocr_uncertainties,
            "class_duplications": class_duplications,
            "clinician_ready_questions": clinician_questions,
            "responsible_ai_disclaimer": "These questions are generated to assist your discussion with your licensed healthcare provider. Do NOT start, modify, or stop any medication without professional medical direction."
        }
