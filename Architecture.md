# VaaniRakshak — Architecture

## 1. Architecture Principle

Build two systems around one shared research infrastructure:

```text
ATTACK LAB
Consented voice → controlled synthetic attack → test sample
                                      ↓
                               VaaniRakshak
                                      ↓
                         detection / reasoning / action
```

The Attack Lab must never be coupled as a malicious operational tool.

---

## 2. High-Level Architecture

```text
                        ANDROID DEVICE
                              │
                       Incoming phone call
                              │
                              ▼
                  Android Telecom / Screening
                              │
                    Contact / identity resolver
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  KNOWN              UNKNOWN
                    │                   │
                    └─────────┬─────────┘
                              ▼
                     Protection Session
                              │
                       Minimal UI state
                              │
                    Authorized audio path
                              │
                              ▼
                       FastAPI Gateway
                              │
                        WebSocket stream
                              │
                         Redis session
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       Voice detector   Speaker verifier    STT
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                    Conversation Intelligence
                              │
                    Temporal Conversation State
                              │
                              ▼
                         Risk Engine
                              │
                              ▼
                       Decision Engine
                       /             \
                 CONTINUE          CRITICAL
                    │                 │
                    ▼                 ▼
              Android update     Protection action
                                      │
                                      ▼
                              Explanation UI
```

---

## 3. Attack Lab Architecture

```text
Attack Lab UI
    │
    ├── Consent manager
    ├── Language selector
    ├── Reference voice manager
    ├── Script manager
    └── Generation controller
              │
              ▼
       Voice Generation Adapter
              │
       ┌──────┼─────────┐
       ▼      ▼         ▼
      TTS  Voice Conv  Clone adapter
       │      │         │
       └──────┼─────────┘
              ▼
        Synthetic sample
              │
        Quality/metadata
              │
              ▼
       Controlled demo stream
```

The generator must be an adapter interface so the actual model can be swapped.

Example interface:

```python
class VoiceGenerator:
    def generate(
        self,
        reference_voice,
        text,
        language,
        config,
    ) -> GeneratedSample:
        ...
```

---

## 4. Repository Structure

```text
VaaniRakshak/
├── android/
│   ├── app/
│   ├── telecom/
│   ├── security/
│   ├── audio/
│   ├── network/
│   ├── data/
│   ├── ui/
│   └── tests/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── calls/
│   │   ├── websocket/
│   │   ├── risk/
│   │   ├── incidents/
│   │   └── settings/
│   ├── services/
│   ├── workers/
│   ├── schemas/
│   ├── db/
│   └── tests/
│
├── ml/
│   ├── voice_authenticity/
│   ├── speaker_verification/
│   ├── stt/
│   ├── conversation/
│   ├── temporal/
│   ├── risk_engine/
│   ├── training/
│   ├── evaluation/
│   └── common/
│
├── attack_lab/
│   ├── generators/
│   ├── consent/
│   ├── scripts/
│   ├── audio/
│   ├── evaluation/
│   └── ui/
│
├── datasets/
│   ├── bona_fide/
│   ├── synthetic/
│   ├── demo_attacks/
│   ├── manifests/
│   └── provenance/
│
├── dashboard/
│   ├── src/
│   └── tests/
│
├── models/
│   ├── checkpoints/
│   └── registry/
│
├── experiments/
│
├── docs/
│   ├── DATASET_CARD.md
│   ├── MODEL_CARD.md
│   ├── TRAINING.md
│   ├── LANGUAGE_COVERAGE_MATRIX.md
│   └── SIH_DEMO.md
│
├── docker/
├── scripts/
├── .env.example
├── docker-compose.yml
├── PRD.md
├── Architecture.md
├── Rules.md
├── Phases.md
└── Memory.md
```

---

## 5. Backend Request Flow

### Call session

```text
POST /v1/calls/session
```

Creates:

- session_id
- device_id
- call metadata
- policy
- language state

### Live stream

```text
WS /v1/calls/{session_id}/stream
```

Messages include:

```json
{
  "type": "risk_update",
  "session_id": "...",
  "risk_score": 74,
  "synthetic_probability": 0.82,
  "speaker_similarity": 0.88,
  "threats": ["impersonation", "urgency"]
}
```

### Decision

```text
POST /v1/calls/{session_id}/decision
```

The server returns a policy decision, but Android must enforce only actions that its current platform privileges/support permit.

---

## 6. ML Pipeline

### Audio

```text
audio chunk
    ↓
validation
    ↓
preprocessing
    ↓
voice authenticity
    ↓
speaker embedding
    ↓
feature fusion
```

### Speech

```text
audio
 ↓
multilingual STT
 ↓
language identification
 ↓
text normalization
 ↓
multilingual classifiers
```

### Conversation

```text
chunk features
      ↓
conversation state
      ↓
temporal model
      ↓
risk fusion
```

---

## 7. Model Ensemble

Initial research candidates:

### Authenticity

- WavLM-based classifier
- AASIST-style detector
- RawNet-style detector

### Speaker

- ECAPA-TDNN

### STT

- faster-whisper / Whisper-compatible abstraction

### NLP

- XLM-RoBERTa or equivalent multilingual encoder
- rule-based high-risk phrase layer
- optional LLM explanation layer

### Temporal

- GRU or Transformer temporal model

The architecture must allow model replacement without changing the Android client.

---

## 8. Risk Fusion

Conceptual:

```text
R = f(
  authenticity,
  speaker_anomaly,
  impersonation,
  intent,
  social_engineering,
  caller_context,
  sensitive_action,
  temporal_change
)
```

Do not hard-code arbitrary weights before validation.

Store model and policy versions with every decision.

---

## 9. Database

### Supabase/PostgreSQL

Core tables:

```text
users
devices
trusted_contacts
consents
speaker_profiles
call_sessions
call_events
risk_events
incidents
model_versions
model_evaluations
language_profiles
audit_logs
```

### Redis

Use for:

- active call state
- TTL-based sessions
- live risk state
- caching
- rate limits
- event coordination

### Future Kafka

Use when event throughput becomes large enough to justify durable distributed streaming.

Do not introduce Kafka into the first prototype unless a concrete need appears.

---

## 10. Android Architecture

```text
UI
 │
SecurityManager
 │
CallScreeningService
 │
CallSessionManager
 │
Network/WebSocket
 │
Local state
```

Use Kotlin coroutines and clean separation between:

- Telecom
- security policy
- network
- UI
- persistence

The Android client should be thin.

---

## 11. Android Platform Constraint

Never fake unrestricted cellular call audio capture.

`CallScreeningService` is for call screening and caller/call metadata. Ordinary third-party apps cannot simply capture unrestricted cellular uplink/downlink audio.

Therefore the architecture has:

### Consumer mode

Real Android call screening + supported security signals.

### Controlled demo mode

A permitted audio source/test stream feeds the same backend pipeline so the complete AI detection flow can be demonstrated.

### Future telecom mode

Carrier/network-level or privileged deployment can provide a deeper audio-analysis path under appropriate authorization.

This distinction must appear in documentation and judge answers.

---

## 12. Deployment

Prototype:

```text
Android
   ↓
FastAPI
   ↓
Redis
   ↓
ML workers
   ↓
Supabase
```

Use Docker Compose locally.

Production evolution:

```text
Load Balancer
      ↓
API replicas
      ↓
Redis Cluster
      ↓
Event streaming
      ↓
GPU ML workers
      ↓
PostgreSQL/Supabase
```

---

## 13. Observability

Track:

- API latency
- WebSocket latency
- inference latency
- model version
- decision latency
- dropped chunks
- errors
- GPU/CPU utilization
- false positives/false negatives
- per-language performance

Never log raw sensitive audio by default.
