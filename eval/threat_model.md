# Threat Model: ABHA Digital Health Organizer
**Challenge 07: A Better Digital Health Journey**  
*Compliance: Universal Hard Requirement #5 (IMPACTX 2026 Hard Mode)*

---

### 1. Risk Register & Implemented Mitigations

```
                  ┌──────────────────────────────────────────────┐
                  │          PATIENT-CONTROLLED VAULT            │
                  │   (ABHA: 91-4421-8890-1234 Rohan Sharma)    │
                  └───────┬──────────────┬─────────────┬─────────┘
                          │              │             │
        ┌─────────────────┴─┐     ┌──────┴──────┐    ┌─┴────────────────┐
        │  Caregiver Gate   │     │ Consent API │    │ Break-Glass Gate │
        │ (Scoped Role/PIN) │     │(Time-Bounded│    │ (Hospital ER)    │
        └─────────┬─────────┘     └──────┬──────┘    └────────┬─────────┘
                  │                      │                    │
                  ▼                      ▼                    ▼
          [Mitigation T2]        [Mitigation T1,T3]   [Mitigation T3]
         Caregiver Shield       Revocation & Ledger  Timed Emergency Log
```

---

#### Threat 1: Silent Medical Misattribution via Inappropriate Merges
- **Threat Scenario**: Two lab reports for the same test carry different dates (one being a re-scan with an erroneous user date). An automated system might overwrite the older date, merge values, or delete one record, destroying clinical provenance and potentially causing incorrect medication titration.
- **Implemented Mitigation**:
  1. The system enforces strict separation of **Event Date**, **Report Date**, and **Upload Date** on every ingested entity.
  2. Duplicate engine strictly enforces a **"Keep Both & Link"** policy.
  3. No programmatic deletion or in-place overwrite is permitted. Both records remain retrievable and verifiable by clinicians with an explicit discrepancy marker.

---

#### Threat 2: Caregiver Overreach & Coercive Boundary Violation
- **Threat Scenario**: An older relative or family helper assisting with routine digital appointments gains unrestricted access, exposing sensitive psychiatric consultations (`REC-007`) or sexual health screenings (`REC-013`).
- **Implemented Mitigation**:
  1. Fine-grained caregiver role definitions (`view_prescriptions`, `view_routine_labs`).
  2. Built-in **Heightened Consent Lockdown** for sensitive categories (`psychiatric_mental_health`, `sexual_reproductive_health`), which are filtered out of caregiver queries by default.
  3. Step-up patient confirmation (biometric/PIN) is mandatory to share any sensitive category.
  4. Real-time patient audit log displaying exact caregiver access timestamps and viewed IDs.

---

#### Threat 3: Illegitimate or Abusive Emergency Break-Glass Invocation
- **Threat Scenario**: A bad actor or curious hospital staff member triggers the emergency "break-glass" workflow to bypass patient consent when the patient is not in a medical emergency.
- **Implemented Mitigation**:
  1. Strict authorization scoping: Emergency access only grants essential vitals, acute medications, and allergies (sensitive mental/reproductive records are excluded by default).
  2. Time-limited session token automatically expires after 4 hours with hard cutoff.
  3. Immediate out-of-band notification dispatched to patient and emergency contact phone.
  4. Tamper-evident append-only logging recording practitioner ID, clinical rationale, IP, and timestamp.

---

#### Threat 4: Lock-Screen Notification Privacy Leaks & Social Stigma
- **Threat Scenario**: A push notification arriving on a patient's mobile device reveals sensitive diagnosis details or lab tests (e.g. *"Your Escitalopram 5mg refill is approved"* or *"HIV antibody screening result ready"*), exposing private medical conditions to peers or family members.
- **Implemented Mitigation**:
  1. Automated notification sanitizer strips all clinical terms, provider specialties, and drug names from push payloads.
  2. Lock-screen notification format: *"ABHA Health Locker: You have 1 new document update. Unlock app to view."*
  3. Sensitive clinical details are rendered solely inside the authenticated viewport.

---

#### Threat 5: Adversarial Prompt Injection & Unauthorized Diagnostic Requests
- **Threat Scenario**: A user uploads a scanned clinical note containing embedded prompt injections (e.g., instructions to ignore privacy filters) or asks the AI assistant *"Do I have chronic kidney disease based on my creatinine?"*
- **Implemented Mitigation**:
  1. Strict **Deterministic Refusal Boundary**: All diagnostic questions ("Do I have X?", "Am I sick?") trigger a standardized refusal and automatically synthesize neutral, clinician-ready visit questions.
  2. Input sanitization engine strips markdown and comment tags (`<!-- SYSTEM OVERRIDE -->`) and isolates clinical text from query execution pipelines.
  3. Zero diagnostic claims or prognostic guarantees are outputted under any system prompt perturbation.

---

### 2. Threat Mitigation Verification Matrix
| Threat | Target Surface | Test Fixture | Automated Test in Harness | Status |
|---|---|---|---|---|
| **T1: Silent Merge** | Ingestion Pipeline | `REC-001` vs `REC-002` | `test_duplicate_zero_silent_merge` | **PASS (0 Merges)** |
| **T2: Caregiver Leak** | Delegation API | `REC-007`, `REC-013` | `test_caregiver_sensitive_exclusion` | **PASS (Shielded)** |
| **T3: Break-Glass Abuse** | Emergency Endpoint | `REC-009` | `test_break_glass_expiry_and_audit` | **PASS (4h Hard Limit)** |
| **T4: Lock-Screen Leak** | Notification Service | `REC-007` Notification | `test_lock_screen_notification_sanitized`| **PASS (Zero PII)** |
| **T5: Diagnostic Injection**| AI / Assistant Engine| `REC-010` & Chat Prompts| `test_prompt_injection_and_diagnosis_refusal`| **PASS (Refused)** |
