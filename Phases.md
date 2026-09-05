# Phase Roadmap: VAANIRAKSHAK Implementation Strategy

**Methodology:** Sequential, Milestone-Driven Verification  
**Source of Truth:** `Phases.md`  

---

## Overview of Implementation Phases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: Project Architecture, Specifications & Document Baseline       │ (CURRENT)
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Core Backend Infrastructure, Data Models & Session State       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: AI Subsystems & Multi-Evidence Extraction Pipelines            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Temporal Risk Engine & Decision Pipeline                       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: System A — Attack Lab & Modular Voice Generators               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: System B — Android Security Client Core                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: Android Live Call Security HUD & Emergency Intervention View  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: React Live Security Command Center Dashboard                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 8: SIH Demo Scenarios, E2E Verification & Benchmarks              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 9: Production Hardening, Security Audit & SIH Submission Package  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 10: CyberCrime (1930) Forensic Dossier & Carrier Webhook Adapter  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 11: Indic Language Expansion & Real-Time Loopback Audio Injector   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     v
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 12: Biometric Profile Vault, Incident Ledger & Live Policy Matrix │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Phase Breakdown

### Phase 0: Project Setup & Baseline Documentation
- **Goal**: Establish project directory structure, source-of-truth specification documents (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`), state tracking (`Memory.md`), and technical compliance cards (`DATASET_CARD.md`, `MODEL_CARD.md`, `TRAINING.md`, `LANGUAGE_COVERAGE_MATRIX.md`, `PRIVACY.md`, `SECURITY.md`, `SIH_DEMO.md`, `LIMITATIONS.md`).
- **Deliverables**: Complete documentation baseline in workspace root.
- **Verification**: All 14 baseline files initialized, validated, and recorded in `Memory.md`.

### Phase 1: Core Backend Infrastructure, Data Models & Session State
- **Goal**: Build Python FastAPI backend, Pydantic schemas, Redis session manager, Supabase/PostgreSQL schema migrations, and high-throughput streaming WebSocket server.
- **Deliverables**: `backend/` project structure, `db/` schemas, `redis/` session tracker, `websocket/` streaming handler.
- **Verification**: Unit tests for audio buffer chunking, Redis session creation, and WebSocket protocol connection.

### Phase 2: AI Subsystems & Multi-Evidence Extraction Pipelines
- **Goal**: Implement independent evidence extraction models:
  1. *Voice Authenticity*: WavLM / AASIST acoustic anti-spoofing engine.
  2. *Speaker Verification*: ECAPA-TDNN biometric similarity calculator.
  3. *Multilingual STT*: `faster-whisper` streaming transcription.
  4. *Conversation Intelligence*: XLM-RoBERTa intent classifier + Social engineering tactic detector + Deterministic regex rules.
- **Deliverables**: `backend/services/ai/` modules for authenticity, speaker verification, STT, and intent analysis.
- **Verification**: Test audio samples passed through each pipeline component; verified output JSON structures.

### Phase 3: Temporal Risk Engine & Decision Pipeline
- **Goal**: Build rolling GRU temporal risk state aggregator, evidence weights, dynamic score trajectory calculator ($0 - 100$), and configurable policy decision engine.
- **Deliverables**: `backend/services/risk/` and `backend/services/decision/` modules.
- **Verification**: Simulated sequence tests demonstrating trajectory progression ($32 \rightarrow 58 \rightarrow 78 \rightarrow 94$) and CRITICAL threshold intervention triggers.

### Phase 4: System A — Attack Lab & Modular Voice Generators
- **Goal**: Implement Attack Lab synthetic audio generation system with decoupled `VoiceGenerator` adapters (Bark/Coqui, OpenVoice, Mock adapter), telecom audio degradation simulator (AMR-WB, packet loss, noise), and cryptographic provenance tagging.
- **Deliverables**: `backend/attack_lab/` module and CLI/API test suites.
- **Verification**: Generate synthetic samples, verify watermarking/provenance metadata, apply degradation, and pass through defense engine.

### Phase 5: System B — Android Security Client Core
- **Goal**: Build Kotlin / Jetpack Compose Android application supporting `CallScreeningService`, `RoleManager`, `ContactsContract` integration, onboarding flow, unknown number protection policy, and consented speaker profile enrollment.
- **Deliverables**: `android/` project structure, Compose views, ViewModels, and Ktor client integration.
- **Verification**: Android unit & UI tests for permissions, contact filtering, and speaker profile enrollment.

### Phase 6: Android Live Call Security HUD & Emergency Intervention View
- **Goal**: Build minimal dynamic overlay HUD (`🛡 Protected | Risk 37/100`), smooth color bar transitions, 10-second emergency intervention countdown UI, threat breakdown overlay, and post-call animated explanation screen.
- **Deliverables**: Jetpack Compose floating window service / call overlay UI components.
- **Verification**: Simulated live call streams driving HUD updates through states SAFE $\rightarrow$ LOW $\rightarrow$ MEDIUM $\rightarrow$ HIGH $\rightarrow$ CRITICAL.

### Phase 7: React Live Security Command Center Dashboard
- **Goal**: Build judge-friendly React + Vite + Tailwind CSS live dashboard displaying real-time call risk radar, voice authenticity spectrum, speaker similarity gauge, live multilingual transcripts, incident forensics, and Attack Lab controls.
- **Deliverables**: `dashboard/` React application.
- **Verification**: E2E WebSocket integration with backend displaying real-time metrics during simulated calls.

### Phase 8: SIH Demo Scenarios, E2E Verification & Benchmarks
- **Goal**: Execute the 3 mandatory SIH demonstration scenarios (Scenario 1: Real Voice, Scenario 2: AI Cloned Voice, Scenario 3: Real Human Scammer), execute performance benchmarks (latency, EER, F1), and finalize documentation.
- **Deliverables**: Comprehensive benchmark report, passing test suites, updated `SIH_DEMO.md`, and complete `Memory.md`.
- **Verification**: All 3 scenarios verified end-to-end with full automated and manual trace records.

### Phase 9: Production Hardening, Security Audit & SIH Submission Package
- **Goal**: Production-harden the multi-tiered defense architecture, eliminate input boundary & policy bypass vulnerabilities, guarantee TypeScript zero-warning clean build, create automated launch/test scripts (`run_backend.sh`, `run_dashboard.sh`, `test_all.sh`), environment templates (`.env.example`), and provide the unified SIH evaluator-grade `README.md`.
- **Deliverables**:
  1. `backend/tests/test_security_hardening.py` (23 adversarial security audit tests).
  2. Input clamping & validation defense in `backend/services/risk/temporal_state.py`.
  3. Zero-warning TypeScript build in `dashboard/`.
  4. Automation shell scripts: `run_backend.sh`, `run_dashboard.sh`, `test_all.sh`.
  5. Configuration template `.env.example`.
  6. Evaluator-ready master `README.md`.
### Phase 10: CyberCrime (1930) Forensic Dossier & Carrier Webhook Adapter
- **Goal**: Implement evidentiary-grade cyber incident dossier generation, SHA-256 cryptographic evidence sealing (tamper-evident audit chain), export pipeline for India's National CyberCrime Reporting Portal (1930 / I4C schema), and Tier-3 Telecom Carrier CDR/SIP trunk webhook integration.
- **Deliverables**:
  1. `backend/services/forensics/dossier_generator.py`: Evidentiary dossier compiler with SHA-256 seal and I4C JSON-LD schema.
  2. `backend/services/carrier/sip_trunk_adapter.py`: Carrier CDR / SIP trunk event webhook and fraud teardown signaler.
  3. `backend/api/endpoints_forensics.py`: REST endpoints for dossier generation, inspection, and direct file download.
  4. React Dashboard: Interactive CyberCrime 1930 report dialog with cryptographic verification badge and dossier export trigger.
  5. `backend/tests/test_forensics_dossier.py`: Test suite verifying cryptographic sealing, tamper detection, and carrier hooks.
- **Verification**: All forensic tests passing, SHA-256 seal tamper detection verified, and 1-click dossier download functional.

### Phase 11: Indic Language Expansion & Real-Time Loopback Audio Injector
- **Goal**: Expand multilingual social engineering NLP to native Indian regional languages (Marathi, Tamil, Telugu, Bengali, Gujarati, Punjabi), expand Attack Lab generation for Indic dialects, and build an automated live loopback PCM audio streamer simulating real-time telecom calls over WebSockets for live jury evaluation.
- **Deliverables**:
  1. Indic scam lexicon and regex pattern integration in `backend/services/ai/intent_nlp.py` covering Marathi (`mr`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Gujarati (`gu`), and Punjabi (`pa`).
  2. `backend/services/telephony/loopback_streamer.py`: High-fidelity real-time PCM audio chunker and WebSocket streaming injector for automated scenario playback.
  3. Attack Lab multilingual scenario adapter extensions.
  4. `backend/tests/test_indic_multilingual.py`: Test suite verifying multi-dialect scam detection and loopback streaming.
- **Verification**: Indic test suite passing 100%, cross-dialect scam detection verified, and loopback simulation operational.

### Phase 12: Biometric Profile Vault, Incident Ledger & Live Policy Matrix
- **Goal**: Implement the Consented Biometric Profile Vault (storing and querying 192-d ECAPA-TDNN voice embeddings with strict consent controls), full Incident History Ledger & Audit Trail API, and live dynamic defense policy tuning (intervention window and threshold matrix).
- **Deliverables**:
  1. `backend/services/biometrics/profile_vault.py`: Biometric embedding vault, cosine similarity matching, and consent audit engine.
  2. `backend/api/endpoints_policy.py`: Dynamic policy tuning endpoints (thresholds, intervention countdown, auto-block toggle).
  3. Incident audit logging integration in `backend/api/endpoints_incidents.py`.
  4. React Dashboard: Biometric Speaker Vault & Dynamic Policy Settings view.
  5. `backend/tests/test_biometrics_and_policy.py`: Test suite for biometric enrollment, cosine verification, and dynamic policy reconfig.
- **Verification**: All 15+ tests passing, policy tuning verified, and biometric matching functional.




