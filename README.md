# ABHA Digital Health Journey — Problem Statement 07
**IMPACTX 2026 | Advanced Challenge Brief (Hard Mode)**  
*Reference: Ayushman Bharat Digital Mission (ABDM) / ABHA Ecosystem*

---

## 🏆 Executive Summary

This repository delivers a fully realized, end-to-end, patient-controlled health organizer engineered specifically to solve the real-world fractures of the ABDM ecosystem:
1. **Provenance Protection**: Enforces immutable **3-Date Separation** (`Event Date`, `Report Date`, `Upload Date`) so conflicting dates on re-scans are flagged rather than rewritten.
2. **Zero Silent Merges**: Duplicate and near-duplicate reports are paired using explainable similarity and resolved via **"Keep Both & Link"**, guaranteeing zero clinical data loss.
3. **Medical Safety Boundary**: Reconciles cross-prescription medications (e.g., dual ARB overlaps, handwritten OCR dosage ambiguity) **purely as clinician-ready questions**, strictly refusing autonomous diagnosis or patient recommendations.
4. **Granular Consent & Honest Revocation**: Time-bounded, category-scoped contracts generating cryptographic **Consent Receipts** and **Revocation Affidavits** that transparently disclose physical limits (records already cached locally by providers cannot be wiped).
5. **Emergency "Break-Glass" Access**: 4-hour hard-timeout emergency window for unconscious presentations, complete with immediate out-of-band patient notifications and default shielding of sensitive psychiatric and reproductive records.
6. **Caregiver Delegation**: Granular role-based scoping (routine labs vs prescriptions) with patient visibility and automatic exclusion of high-stigma categories.
7. **Provider Supersession Propagation (Elite)**: Official laboratory amendments flag previous reports as **SUPERSEDED** and broadcast update notices to all active shares.
8. **Tamper-Evident Audit Ledger**: Append-only SHA-256 hash-chained log (`Hash_N = SHA256(Event + Hash_{N-1})`) proving every system action.
9. **Live Evaluation Harness**: 17 scripted automated tests achieving a **100% pass rate**, **100% duplicate recall**, and **zero silent merges**.

---

## 🚀 Quick Start (Zero External Dependencies)

Built entirely with standard library Python 3.12 and modern web technologies. Runs out-of-the-box with **no `npm install` or `pip install` required**.

### 1. Launch the Interactive Web Application
```bash
cd C:\Users\dryve\.gemini\antigravity\scratch\health-journey-abdm
python server.py
```
Open your browser to:
👉 **`http://localhost:8080`**

### 2. Run the Automated Evaluation Harness (CLI)
```bash
python eval/test_harness.py
```
*Output: 17/17 tests passing, 100% pass rate, zero silent merges, verified cryptographic audit trail.*

---

## 📊 Live Judge Demo Script (20-Minute Winning Walkthrough)

Aligned directly with the IMPACTX 2026 judging format (*Brief Page 44*):

### Minute 0–5: Scenario & User Pain Point
- **Persona**: Rohan Sharma (42M, ABHA: `91-4421-8890-1234`), living with Type 2 Diabetes and Hypertension, consulting across Bangalore (Apex Labs, Manipal Hospital) and Delhi (Fortis, Dr. Lal PathLabs).
- **Core Friction**: Fragmented records across cities; re-uploaded scans carrying incorrect dates; a handwritten prescription with smeared ink; dual active prescriptions from different doctors; fear of caregiver overreach on sensitive mental health records.

### Minute 5–12: The End-to-End Solution
1. **Longitudinal Timeline (3-Date Provenance)**:
   - Navigate to the **Timeline** tab. Observe `REC-001` and `REC-002`.
   - Point out the yellow banner: `REC-002` has an inverted date anomaly (`Event Date 2026-04-12` vs `Report Date 2026-03-12`), flagged transparently without overwriting the original.
2. **Duplicate Linking ("Keep Both & Link")**:
   - Open the **Duplicate & Re-Scan Linking** tab.
   - Show `REC-001` vs `REC-002` (98.5% similarity) and `REC-001` vs `REC-011` (exact duplicate).
   - Click **"Keep Both & Link with Provenance"**. Explain how this enforces the **Zero Silent Merges** rule.
3. **Medication Reconciliation & Clinician Prep**:
   - Open the **Medication Reconciliation** tab.
   - Review **OCR Dosage Uncertainty**: Metformin dose character confidence is 42% due to ink smear.
   - Review **Therapeutic Class Overlap**: Highlights concurrent Telmisartan 40mg (Fortis) and Losartan 50mg (Manipal).
   - Review **Clinician-Ready Questions**: Demonstrates questions phrased for Dr. Mehta rather than patient-directed medical instructions.
4. **Consent Revocation with Honest Disclosure**:
   - Open the **Consent & Revocation Ledger** tab.
   - Click **"Revoke Access Immediately"** on Dr. Rajesh Mehta's 7-day share (`CONSENT-701`).
   - The modal pops up displaying the **ABDM Revocation Affidavit** with SHA-256 seal and honest disclosure that past downloads cannot be deleted.
   - Switch active role to **Specialist (Dr. Mehta)**: notice all records are immediately blocked with HTTP 403.
5. **Emergency Break-Glass Simulator**:
   - Open the **Emergency Break-Glass** tab.
   - Click **"Trigger Emergency Break-Glass Access"** (Max Hospital ER trauma presentation).
   - Shows the active 4-hour countdown clock, out-of-band SMS dispatch to Rohan, and sensitive records (`REC-007` & `REC-013`) locked out of emergency view.
6. **Provider Supersession Propagation (Elite)**:
   - Open the **Provider Supersession** tab.
   - Click **"Ingest Amended Report & Broadcast Supersession"**.
   - Original lipid profile `REC-005` is stamped **SUPERSEDED** and update notifications are broadcast to all active shares.

### Minute 12–17: Curveballs & Judge Fault Injection
1. **Curveball: "Do I have chronic kidney disease?"**:
   - Open the **Responsible AI Safety Guard** tab and click the test query button.
   - System strictly refuses to diagnose and routes to 3 clinician-ready questions based on his `2.4 mg/dL` creatinine reading.
2. **Curveball: Abnormal Lab Values Displayed Neutrally**:
   - Check `REC-008` (Creatinine 2.4 mg/dL) on the timeline. It displays factually alongside the reference range without alarmist red banners.
3. **Curveball: Lock-Screen Notification Privacy**:
   - Demonstrates that mobile push alerts only state *"You have a new health update"*, keeping sensitive clinical information behind biometric authentication.
4. **Judge Fault Injection Bar**:
   - Click **504 Gateway Timeout** or **Network Severed (Offline)** on the top bar.
   - Timeline immediately transitions to degraded mode, serving local encrypted cache with clear freshness indicators.

### Minute 17–20: Results & Evidence
- Click **Evaluation Harness** tab and hit **"Run Test Suite Live"**: 17/17 tests passing (100%).
- Click **1-Page Data Card** to view all 15 planted edge cases.
- Click **Threat Model** to review the 5 abuse and privacy mitigations.
- Click **Tamper-Evident Audit Trail** and hit **"Verify Cryptographic Chain Integrity"** to demonstrate cryptographic proof of all transactions.

---

## 🏗️ Architecture & Component Directory

```
health-journey-abdm/
├── server.py                        # Multi-threaded REST API & static web server
├── app/
│   ├── index.html                   # Single-Page Application (All 9 Views & Switchers)
│   ├── styles.css                   # Responsive UI + High Contrast + Glassmorphism
│   └── app.js                       # State, Web Speech narration, Hindi i18n, API client
├── backend/
│   ├── audit_trail.py               # Append-only SHA-256 hash-chained ledger
│   ├── state_machines.py            # Explicit state machines (Consent, Record, Break-Glass)
│   ├── timeline_engine.py           # 3-Date separation & chronological discrepancy engine
│   ├── duplicate_engine.py          # Explainable similarity & "Keep Both & Link" engine
│   ├── medication_reconciliation.py # Cross-prescription discrepancy & clinician question generator
│   ├── consent_ledger.py            # Fine-grained consent scoping & revocation receipts
│   ├── break_glass.py               # Emergency ER 4-hour countdown & SMS dispatch
│   ├── provider_supersession.py     # Amended report linking & share broadcast
│   ├── safety_boundary.py           # Diagnosis refusal, neutral display, lock-screen sanitization
│   └── fault_injector.py            # Judge live fault injection (504, stale, offline, race)
├── data/
│   ├── seeded_dataset.json          # 15 deliberately planted synthetic edge-case records
│   └── data_card.md                 # 1-Page clinical synthetic data card
└── eval/
    ├── test_harness.py              # 17 automated unit tests with live reporting
    └── threat_model.md              # 1-Page Threat Model (Top 5 Abuse/Privacy Mitigations)
```

---

## 🎯 Verification Matrix

| Challenge Requirement | Implemented Feature | Test Fixture | Status |
|---|---|---|---|
| **3-Date Provenance** | Event, Report, and Upload dates explicitly separated | `test_01_three_date_separation` | ✅ 100% PASS |
| **Date Conflict Detection** | Chronology inversion detected on re-scans | `test_02_detect_date_conflict_in_rescan` | ✅ 100% PASS |
| **Duplicate Detection** | Explainable similarity scoring (Parameters, Provider, Domain) | `test_03_duplicate_detection_precision_recall` | ✅ 100% Recall |
| **Zero Silent Merges** | "Keep Both & Link" action preserving original records | `test_04_zero_silent_merges` | ✅ 0 Merges |
| **OCR Uncertainty** | 42% confidence on handwritten Metformin dose | `test_05_ocr_uncertainty_quantification` | ✅ 100% PASS |
| **Medication Reconciliation** | Telmisartan + Losartan overlap framed as clinician question | `test_06_medication_reconciliation_clinician_questions` | ✅ 100% PASS |
| **Diagnosis Refusal** | Refuses "Do I have X?" and routes to doctor questions | `test_07_medical_diagnosis_refusal` | ✅ 100% PASS |
| **Prompt Injection Defense**| Neutralizes adversarial instructions embedded in documents | `test_08_prompt_injection_neutralization` | ✅ 100% PASS |
| **Neutral Value Display** | Displays abnormal creatinine (2.4 mg/dL) without panic alarms | `test_09_neutral_display_of_abnormal_values` | ✅ 100% PASS |
| **Fine-Grained Consent** | Category, record, and recipient-level scoping | `test_10_granular_consent_enforcement` | ✅ 100% PASS |
| **Instant Revocation** | Cryptographic affidavit with honest limit disclosure | `test_11_instant_revocation_and_honest_disclosure` | ✅ 100% PASS |
| **Caregiver Delegation** | Sensitive psychiatric & HIV records shielded by default | `test_12_caregiver_sensitive_exclusion` | ✅ 100% PASS |
| **Emergency Break-Glass** | 4-hour countdown + patient notification + audit | `test_13_break_glass_emergency_time_limit` | ✅ 100% PASS |
| **Provider Supersession** | Amended report supersedes old report + broadcasts update | `test_14_provider_supersession_propagation` | ✅ 100% PASS |
| **Tamper-Evident Audit** | SHA-256 hash chaining detects any log modification | `test_15_tamper_evident_audit_trail_integrity` | ✅ 100% PASS |
| **Lock-Screen Privacy** | Sanitizes push notifications to zero clinical PII | `test_16_lock_screen_notification_sanitization` | ✅ 100% PASS |
| **Fault Injection** | Survives 504 Gateway Timeout with local cache fallback | `test_17_fault_injection_service_timeout_fallback` | ✅ 100% PASS |
