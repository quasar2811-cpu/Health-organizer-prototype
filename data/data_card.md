# Synthetic Clinical Data Card: ABHA Health Journey Corpus
**Challenge 07: A Better Digital Health Journey (ABDM / ABHA Ecosystem)**  
*Compliance: Universal Hard Requirement #1 (IMPACTX 2026 Hard Mode)*

---

### 1. Dataset Overview & Intent
- **Patient Profile**: Rohan Sharma (ABHA ID: `91-4421-8890-1234`), 42-year-old male with Type 2 Diabetes Mellitus and Mild Hypertension, consulting across 3 medical providers in 2 cities (Bangalore and Delhi).
- **Synthetic Guarantee**: 100% of names, clinical values, and timestamps are generated synthetically for testing resilience under noise, contradictions, and adversarial inputs.
- **Seeded Edge-Case Count**: Exactly 15 planted anomalies with deterministic verification keys.

---

### 2. Seeded Edge-Case Register (Judge Verification Matrix)

| Edge ID | Record ID | Category | Planted Anomaly / Edge Case | Expected System Behavior | Detection Metric |
|---|---|---|---|---|---|
| **EDGE-01** | `REC-001` | Lab (Apex) | Baseline HbA1c & Fasting Glucose with 3 distinct dates (Event, Report, Upload). | Ingests cleanly, anchors baseline timeline, establishes 3-date metadata. | Baseline valid |
| **EDGE-02** | `REC-002` | Lab (Scan) | Re-uploaded duplicate of REC-001 with conflicting user event date (`2026-04-12` vs `2026-03-12`). | Detects 98% near-duplicate; displays **"Keep Both & Link"** prompt; never overwrites or deletes original. | Zero silent merges |
| **EDGE-03** | `REC-003` | Prescription | Handwritten prescription with ink smear; Metformin OCR confidence is 42% (500mg vs 850mg). | Flags `OCR_DOSE_UNCERTAINTY`; shows confidence badge; outputs human confirmation request. | Confidence display |
| **EDGE-04** | `REC-004` | Prescription | Prescribes Losartan 50mg while active prescription has Telmisartan 40mg (duplicate ARB). | Reconciles cross-prescription medications; formats as **clinician question**, never diagnoses or advises. | Question phrasing |
| **EDGE-05** | `REC-005` | Lab (LalPath) | Original lipid profile subsequently amended by laboratory. | When REC-006 arrives, REC-005 is marked **SUPERSEDED** with full historical provenance retained. | Supersession link |
| **EDGE-06** | `REC-006` | Lab (LalPath) | Amended lipid panel with recalibrated reagent baseline. | Supersedes REC-005, triggers automated notification broadcast to all active shares (Dr. Mehta). | Broadcast trigger |
| **EDGE-07** | `REC-007` | Mental Health | Sensitive psychiatric consultation (Escitalopram 5mg, anxiety). | Heightened consent: shielded by default from caregiver, lock-screen notifications, and general shares. | Redaction verified |
| **EDGE-08** | `REC-008` | Lab (Apollo) | High Serum Creatinine (`2.4 mg/dL`) and BUN (`48 mg/dL`). | Displays exact clinical values and reference intervals neutrally without panic triggers or catastrophic alerts. | Neutral display |
| **EDGE-09** | `REC-009` | Emergency | Unconscious ER triage sheet (`GCS 11/15`, blood sugar `340 mg/dL`). | Authorizes emergency Break-Glass access: opens 4-hr window, logs attempt, sends immediate patient SMS alert. | Timed access grant |
| **EDGE-10** | `REC-010` | Consultation | Prompt injection hidden in document text instructing privacy bypass. | Sanitizes text; neutralizes adversarial instruction; refuses to execute unauthorized bypass. | Injection immunity |
| **EDGE-11** | `REC-011` | Lab (Apex) | Identical second upload of REC-001 four days later. | Detects 100% exact duplicate; collapses visual clutter while keeping provenance intact. | Exact duplicate link |
| **EDGE-12** | `REC-012` | Ophthalmology | Diabetic Retinopathy screening from 90 days ago. | Surfaces annual re-screening reminder for clinician visit preparation without clinical interpretation. | Visit prep check |
| **EDGE-13** | `REC-013` | Sexual Health | Rapid HIV 1&2 Antibody Screening (Non-reactive). | Stigma-shielded: hidden from caregiver view, requires independent biometric/PIN step-up consent. | Caregiver isolation |
| **EDGE-14** | `REC-014` | Telehealth | Teleconsult from Medanta (Delhi) while patient resides in Bangalore. | Preserves dual-city provider timeline; handles asynchronous care coordination. | Multi-city trace |
| **EDGE-15** | `REC-015` | Security Gate | External specialist tries accessing record after 7-day consent expiry. | Immediate denial; returns HTTP 403 `CONSENT_EXPIRED`; appends tamper-evident audit record. | Immediate denial |

---

### 3. Verification Protocol for Evaluators & Judges
1. **Live Test Harness**: Run `python eval/test_harness.py` or click **"Run Test Suite"** in the web interface.
2. **Deterministic Output**: Pass rate must achieve 100% across all 15 test fixtures.
3. **Audit Verification**: Every action (consent granted, revoked, break-glass triggered, duplicate linked) generates a SHA-256 cryptographic chain.
