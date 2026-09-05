# Architecture Specification: VAANIRAKSHAK Engine & Attack Lab

**System Architect:** Principal Security & AI Systems Architect  
**Version:** 1.0.0-SIH2026  
**Target Environments:** Android (API 26+) | Python 3.11 FastAPI Backend | React 18 / Vite / Tailwind Dashboard  

---

## 1. System Topology & Data Flow Architecture

VAANIRAKSHAK is built as a micro-service, modular event-driven architecture designed to process streaming audio frames in under **300ms latency** to deliver real-time phone call threat assessment.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                 ANDROID CLIENT                                    │
│                                                                                   │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────┐  │
│  │ CallScreeningService   │   │ Contacts & User Policy │   │ Consented Profiles │  │
│  └───────────┬───────────┘   └───────────┬────────────┘   └─────────┬──────────┘  │
│              │ Intercept Call            │ Query Protection         │ Embedding   │
│              v                           v                          v             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                     Android Audio Acquisition Handler                       │  │
│  │   - Tier 1: Consumer Mode (Call Screening + Local Testing)                  │  │
│  │   - Tier 2: Research/Demo Mode (Mic / WS Loopback Audio Injector)           │  │
│  │   - Tier 3: Privileged Operator Mode (gRPC Carrier Audio Feed)            │  │
│  └───────────────────────────────────────┬─────────────────────────────────────┘  │
└──────────────────────────────────────────┼────────────────────────────────────────┘
                                           │ WebSocket PCM Stream (16kHz, 16-bit)
                                           v
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         PYTHON FASTAPI REAL-TIME AI ENGINE                        │
│                                                                                   │
│    ┌─────────────────────────────────────────────────────────────────────────┐    │
│    │                       WebSocket Handler & Buffer Manager               │    │
│    └────────────────────────────────────┬────────────────────────────────────┘    │
│                                         │ 1-second rolling audio chunks           │
│                                         v                                         │
│    ┌─────────────────────────────────────────────────────────────────────────┐    │
│    │                      PARALLEL EVIDENCE PIPELINE                         │    │
│    │                                                                         │    │
│    │  ┌─────────────────────┐ ┌─────────────────────┐ ┌───────────────────┐  │    │
│    │  │ Voice Authenticity  │ │ SpeakerBiometric    │ │  Streaming STT    │  │    │
│    │  │ (WavLM / AASIST)    │ │ (ECAPA-TDNN)        │ │  (faster-whisper) │  │    │
│    │  └──────────┬──────────┘ └──────────┬──────────┘ └─────────┬─────────┘  │    │
│    │             │ synthetic_prob        │ similarity_score     │ transcript  │    │
│    │             │                       │                      v             │    │
│    │             │                       │            ┌────────────────────┐ │    │
│    │             │                       │            │ Conversation Intel │ │    │
│    │             │                       │            │ (XLM-RoBERTa NLP)  │ │    │
│    │             │                       │            └─────────┬──────────┘ │    │
│    │             │                       │                      │ intent     │    │
│    │             │                       │                      │ tactics    │    │
│    └─────────────┼───────────────────────┼──────────────────────┼────────────┘    │
│                  │                       │                      │                 │
│                  v                       v                      v                 │
│    ┌─────────────────────────────────────────────────────────────────────────┐    │
│    │                         Temporal Risk State Engine                      │    │
│    │                   - Rolling GRU State Tracker (0 -> 100)                │    │
│    │                   - Evidence Aggregator & Weighted Trajectory           │    │
│    └────────────────────────────────────┬────────────────────────────────────┘    │
│                                         │ Risk Assessment & Evidence JSON         │
│                                         v                                         │
│    ┌─────────────────────────────────────────────────────────────────────────┐    │
│    │                            Decision Engine                              │    │
│    │           - SAFE / LOW / MEDIUM / HIGH / CRITICAL Band Evaluation       │    │
│    │           - Trigger 10-second Policy Confirmation / Intervention        │    │
│    └────────────────────────────────────┬────────────────────────────────────┘    │
└─────────────────────────────────────────┼─────────────────────────────────────────┘
                                          │
                  +-----------------------+-----------------------+
                  │ Event Broadcast                               │ Metrics / Audit
                  v                                               v
┌───────────────────────────────────┐           ┌───────────────────────────────────┐
│        REDIS SESSION STORE        │           │    SUPABASE / POSTGRESQL DB       │
│  - Live Call States               │           │  - Incidents & Threat Logs        │
│  - Temporal Risk Trajectories     │           │  - Consented Speaker Embeddings   │
│  - Rate Limiting                  │           │  - System Audit Trail             │
└─────────────────┬─────────────────┘           └───────────────────────────────────┘
                  │ Real-Time WS Update
                  v
┌───────────────────────────────────────────────────────────────────────────────────┐
│                   REACT + VITE + TAILWIND LIVE COMMAND CENTER                     │
│  - Real-Time Risk Radar   - Voice Authenticity Spectrum   - Live Transcript       │
│  - Speaker Anomaly Gauge  - Attack Lab Control Center     - Incident Forensics    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications & Design Patterns

### 2.1 System A: Attack Lab Architecture

#### Modular Generator Architecture (`VoiceGenerator` Adapter Pattern)
```
                ┌──────────────────────────────────────┐
                │        VoiceGenerator (ABC)          │
                └──────────────────┬───────────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      │                            │                            │
      v                            v                            v
┌───────────┐                ┌───────────┐                ┌───────────┐
│ BarkXTTS  │                │ OpenVoice │                │ MockAudio │
│ Adapter   │                │ Adapter   │                │ Adapter   │
└───────────┘                └───────────┘                └───────────┘
```

#### Audio Degradation Pipeline (`DegradationSimulator`)
To test defense robustness against real-world cellular network impairments, generated synthetic audio passes through a telecom degradation pipeline:
1. **Codec Compression**: AMR-WB (12.65 kbps), AMR-NB (7.4 kbps), G.711 $\mu$-law compression simulation.
2. **Bandwidth Filtering**: Narrowband ($300\text{Hz} - 3.4\text{kHz}$) and Wideband ($50\text{Hz} - 7\text{kHz}$) bandpass filters.
3. **Acoustic Noise**: Street, babble, and impulse noise injection at specified Signal-to-Noise Ratios (SNR: 5dB to 25dB).
4. **Packet Loss**: Simulated jitter and 2%–5% frame drop simulating VoIP/cellular transport.

### 2.2 System B: Android Security Application Architecture

#### 3-Tier Audio & Telecom Acquisition Boundaries

| Mode Tier | Description | Suitable Context | Security & Privacy Guarantees |
|---|---|---|---|
| **Tier 1: Consumer Mode** | Uses standard `CallScreeningService` to intercept calls, identify unknown numbers, and display floating security HUD overlay using Android system windows. Uses simulated audio loopback for local testing. | Public Play Store release / Consumer devices | Zero platform policy violations; standard Android permission framework. |
| **Tier 2: Research/Demo Mode** | Captures ambient mic audio or uses internal loopback / WebSocket stream injection from Attack Lab. | Hackathon evaluation, live security testing, hardware test benches | Explicit user research consent modal active; visible persistent foreground notification. |
| **Tier 3: Carrier/Privileged Mode** | Direct gRPC voice stream integration with telecom IMS/VoLTE core or operator-level tap. | Future enterprise telecom deployment | High throughput, server-side carrier integration; zero app-side audio overhead. |

#### Android Technical Stack
- **Language**: Kotlin 1.9+
- **UI Framework**: Jetpack Compose (Material3 + Custom Cyberpunk Security Palette)
- **Architecture**: Clean Architecture + MVVM + Repository Pattern
- **Async & Reactive**: Kotlin Coroutines + StateFlow / SharedFlow
- **Networking**: Ktor Client / Retrofit + WebSockets
- **Permissions**: `TelecomManager`, `CallScreeningService`, `RoleManager`, `ContactsContract`

---

### 2.3 Backend & AI Engine Architecture

#### Engine Subsystems & Models

1. **Voice Authenticity Module (Anti-Spoofing)**:
   - **Primary Model**: Fine-tuned WavLM Large / AASIST spectro-temporal feature extractor.
   - **Feature Extraction**: LFCC (Linear Frequency Cepstral Coefficients) + Spectro-Temporal Phase Embeddings.
   - **Output**: `synthetic_probability` ($[0.0, 1.0]$), `human_probability`, `confidence`.

2. **Speaker Verification Module (Biometrics)**:
   - **Primary Model**: ECAPA-TDNN (Emphasized Channel Attention, Propagation and Aggregation in TDNN).
   - **Process**: Extracts 192-dimensional speaker embedding from audio chunk; calculates cosine similarity against enrolled user profiles stored in PostgreSQL.
   - **Output**: `speaker_similarity` ($[0.0, 1.0]$), `enrolled_speaker_id`.

3. **Multilingual Speech-to-Text (STT)**:
   - **Engine**: `faster-whisper` (CTranslate2 implementation of OpenAI Whisper).
   - **Streaming**: VAD (Voice Activity Detection) powered chunking into 1.5-second text windows.
   - **Output**: `transcription`, `detected_language`, `language_probability`.

4. **Conversation Intelligence & Social Engineering NLP**:
   - **Model**: `xlm-roberta-base` fine-tuned for multilingual intent and psychological manipulation detection + Deterministic Regex Rule Fallbacks.
   - **Categories**:
     - *Intents*: `MONEY_TRANSFER`, `OTP_REQUEST`, `PASSWORD_REQUEST`, `PIN_REQUEST`, `REMOTE_ACCESS`, `APK_INSTALLATION`, `BANK_VERIFICATION`.
     - *Tactics*: `URGENCY`, `FEAR`, `AUTHORITY`, `SECRECY`, `PRESSURE`, `ISOLATION`.

5. **Temporal Risk State Engine (GRU Aggregator)**:
   - Maintains rolling state vector over $N$ time steps:
     $$S_t = \text{GRU}(S_{t-1}, E_t)$$
     where $E_t = [\text{synthetic\_prob}, \text{speaker\_similarity}, \text{intent\_score}, \text{tactic\_score}, \text{caller\_context}]$.
   - Calculates dynamic risk trajectory $R_t \in [0, 100]$.

---

## 3. Database & Session Architecture

### 3.1 Redis Session Store
- Key Pattern `call:session:{session_id}`: Store active call metadata, current risk score, temporal history, and client connections.
- Key Pattern `call:stream:{session_id}`: Streaming audio chunk buffer.
- TTL: 30 minutes automatic expiry post-call termination.

### 3.2 Supabase / PostgreSQL Schema
- `users`: User profiles and protection policies.
- `enrolled_speakers`: Consented trusted contact profiles storing 192-d ECAPA-TDNN embeddings (vector column using `pgvector`).
- `incidents`: High-risk call records, evidence snapshots, risk trajectories, and decision audit logs (zero raw audio).
- `attack_lab_provenance`: Provenance registry of generated synthetic audio samples.

---

## 4. API & WebSocket Protocol Contract

### WebSocket Endpoint: `/ws/call/{session_id}`
- **Client Message (Audio Frame)**:
  ```json
  {
    "type": "audio_chunk",
    "sequence": 14,
    "timestamp_ms": 1400,
    "pcm_b64": "..."
  }
  ```
- **Server Message (Risk Update)**:
  ```json
  {
    "type": "risk_update",
    "session_id": "sess_89f2a0",
    "sequence": 14,
    "risk_score": 94,
    "band": "CRITICAL",
    "evidence": {
      "synthetic_probability": 0.96,
      "speaker_similarity": 0.92,
      "detected_intent": "MONEY_TRANSFER",
      "detected_tactics": ["URGENCY", "PRESSURE"],
      "transcription_snippet": "I need your help urgently. Send 20,000 rupees..."
    },
    "action": "INTERVENE_RECOMMENDED",
    "policy_window_sec": 10
  }
  ```
