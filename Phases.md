# VaaniRakshak — Implementation Phases

## Phase 0 — Project Foundation

### Goal

Create a clean monorepo and documentation system.

Deliver:

- repository
- PRD.md
- Architecture.md
- Rules.md
- Phases.md
- docs structure
- .env.example
- Docker Compose
- README
- Memory.md template only after coding begins

Acceptance:

- project boots
- all services have health checks
- no secrets committed

---

## Phase 1 — Attack Lab Foundation

### Goal

Create the controlled voice-cloning research/demo environment.

Build:

- Attack Lab UI
- consent workflow
- reference voice manager
- language selector
- script manager
- generator adapter interface
- synthetic sample metadata
- sample browser
- demo playback
- provenance storage

Do not build unauthorized voice collection.

Acceptance:

- consented reference sample can enter the lab
- a synthetic sample can be generated through a pluggable generator
- sample is labeled synthetic
- metadata is recorded

---

## Phase 2 — Dataset & Evidence Infrastructure

Build:

```text
datasets/
├── bona_fide/
├── synthetic/
├── demo_attacks/
├── manifests/
└── provenance/
```

Create:

- DATASET_CARD.md
- LANGUAGE_COVERAGE_MATRIX.md
- source manifests
- license records
- train/val/test manifests
- speaker-disjoint splitting
- generator-disjoint evaluation support

Acceptance:

- every training sample has traceable metadata
- no undocumented audio is used

---

## Phase 3 — Voice Authenticity Model

Build baseline:

- preprocessing
- WavLM representation pipeline
- classifier
- AASIST/RawNet research adapters
- training scripts
- validation
- checkpointing
- inference API

Metrics:

- precision
- recall
- F1
- ROC-AUC/PR-AUC as appropriate
- EER where appropriate
- latency

Acceptance:

- model can classify real vs synthetic
- evaluation is reproducible

---

## Phase 4 — Speaker Verification

Build:

- ECAPA-TDNN adapter
- consented speaker enrollment
- embedding storage
- similarity scoring
- threshold calibration

Acceptance:

- reference voice can be enrolled
- cloned voice can demonstrate high similarity
- identity and authenticity remain separate signals

---

## Phase 5 — Multilingual STT

Build:

- language identification
- multilingual STT adapter
- streaming/chunked transcription
- Hinglish/code-switch handling
- transcript normalization

Start with strong Indian-language coverage and expand globally.

Acceptance:

- supported languages produce usable transcripts
- language ID is exposed to the risk engine

---

## Phase 6 — Conversation Intelligence

Build classifiers for:

- financial fraud
- OTP/password/PIN
- remote access
- APK installation
- identity verification
- emergencies
- job/investment scams
- threats/blackmail

Build social-engineering classifiers:

- urgency
- fear
- authority
- secrecy
- pressure
- emotional manipulation
- threat
- reward/scarcity/isolation

Acceptance:

- structured multi-label output
- per-label confidence
- test suite exists

---

## Phase 7 — Temporal Risk Engine

Build:

- rolling conversation state
- chunk feature history
- GRU/Transformer experiment
- risk trajectory
- confidence smoothing
- configurable thresholds

Acceptance:

- risk can evolve:
  `18 → 27 → 43 → 67 → 91`
- noisy single-chunk predictions do not immediately trigger catastrophic action

---

## Phase 8 — Unified Risk & Decision Engine

Fuse:

- synthetic probability
- speaker similarity
- impersonation
- intent
- social engineering
- caller context
- sensitive action
- temporal trajectory

Build policy engine:

- SAFE
- LOW
- MEDIUM
- HIGH
- CRITICAL

Acceptance:

- every decision has evidence
- policy is configurable
- model does not directly control termination

---

## Phase 9 — Android Foundation

Build:

- Kotlin project
- Compose
- onboarding
- permission education
- contacts integration
- RoleManager flow
- CallScreeningService
- security state
- notifications
- local settings

Acceptance:

- app installs
- role flow works where supported
- known/unknown classification works
- no fake Android APIs

---

## Phase 10 — Android Live Security UI

Build:

- minimal protection indicator
- live risk score
- animated risk bar
- security state
- critical intervention state
- post-call explanation

Acceptance:

- normal phone UI remains primary
- security layer is visually minimal
- risk updates arrive live

---

## Phase 11 — Backend + WebSocket

Build:

- FastAPI
- authentication
- call sessions
- WebSockets
- Redis state
- Supabase integration
- event schemas
- model orchestration

Acceptance:

- Android can establish a security session
- backend can stream structured risk updates
- reconnect logic works

---

## Phase 12 — Dashboard

Build:

- live command center
- active call
- risk timeline
- model outputs
- transcript
- evidence
- incidents
- Attack Lab
- Dataset Explorer
- Language Coverage
- Evaluation

Acceptance:

- judge can understand the system without developer explanation

---

## Phase 13 — Multilingual Expansion

Expand model/data/evaluation coverage.

For every language record:

- STT capability
- voice detector evaluation
- NLP evaluation
- Attack Lab generation capability
- known limitations

Acceptance:

- language matrix is honest and current
- Indian-language coverage is strong
- global architecture remains extensible

---

## Phase 14 — Robustness

Test:

- telephone compression
- noise
- reverb
- packet loss simulation
- short clips
- long clips
- different microphones
- accents
- code switching
- unseen synthetic generators

Acceptance:

- documented robustness results
- failure cases known

---

## Phase 15 — Security & Privacy

Implement:

- encryption
- retention policies
- secure secrets
- rate limiting
- audit logs
- consent records
- privacy controls

Acceptance:

- no raw audio retained by default
- no secrets in source
- security tests pass

---

## Phase 16 — SIH Demo Mode

Prepare three controlled scenarios:

### Scenario A

Real trusted voice → SAFE.

### Scenario B

Consent-based cloned trusted voice + malicious request → CRITICAL.

### Scenario C

Real human scammer + malicious request → CRITICAL.

Build:

- demo reset
- demo status
- predictable scripts
- live dashboard
- fallback test stream
- judge explanation

Acceptance:

The entire demo can be run repeatedly.

---

## Phase 17 — Final Evaluation

Run:

- unit tests
- integration tests
- Android tests
- API load tests
- ML benchmarks
- multilingual benchmarks
- security tests
- failure injection
- latency tests

Create final reports.

Never alter metrics to make them look better.

---

## Phase 18 — Documentation & Judge Package

Final files:

```text
docs/
├── DATASET_CARD.md
├── MODEL_CARD.md
├── TRAINING.md
├── LANGUAGE_COVERAGE_MATRIX.md
├── PRIVACY.md
├── SECURITY.md
├── SIH_DEMO.md
└── LIMITATIONS.md
```

Also prepare:

- architecture diagram
- model pipeline diagram
- demo flow
- 2-minute pitch
- technical Q&A
- judge questions/answers
- dataset evidence
- benchmark evidence

---

## Phase 19 — Final Polish

Do not add random features.

Focus on:

- reliability
- speed
- visual polish
- explainability
- demo reproducibility
- honest claims
- documentation

The final system should feel like a real security product, not a collection of disconnected AI demos.
