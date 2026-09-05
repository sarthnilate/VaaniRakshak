# VaaniRakshak — Product Requirements Document

## 1. Project Identity

**Project:** VaaniRakshak  
**SIH Problem Statement:** SIH26104 — AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks  
**Primary platform:** Android  
**Primary audience:** Citizens of India, with a global multilingual architecture  
**Project type:** Privacy-first, real-time voice-threat detection and prevention platform.

VaaniRakshak is a phone security layer that protects people from voice-cloning impersonation, social engineering, fraud, credential theft, and other high-risk calls.

The project has TWO intentionally separate systems:

1. **Attack Lab** — a controlled, consent-based voice-cloning simulator used only to create synthetic attack samples and demonstrate the threat to judges.
2. **VaaniRakshak** — the actual defensive product that detects synthetic speech, verifies speaker similarity where consent exists, understands conversation risk, calculates dynamic risk, and protects the user.

The Attack Lab is the attack simulator. VaaniRakshak is the security product.

---

## 2. Problem

Generative speech systems can produce convincing copies of a person's voice. Attackers can use such voices to impersonate family members, officials, bank employees, colleagues, recruiters, or executives.

Caller ID and human familiarity with a voice are insufficient.

VaaniRakshak must therefore answer:

- Is the speech likely synthetic/manipulated?
- Does the voice resemble a trusted/enrolled speaker?
- Is the caller impersonating someone?
- Is the conversation requesting money, OTPs, passwords, PINs, remote access, APK installation, personal information, etc.?
- Is the caller using urgency, fear, authority, secrecy, pressure, threats, or emotional manipulation?
- Is the threat becoming more dangerous over time?
- Should the call continue, warn, or be terminated?

---

## 3. Product Vision

Make voice calls behave like a protected security surface.

The user should NOT need to open a separate app and manually analyze every call.

The intended experience is:

Incoming call → automatic protection → tiny security indicator → live risk evolution → intervention if critical → animated explanation.

The normal phone-call experience remains dominant.

---

## 4. Target Users

### Primary

All citizens who use Android phones.

### Secondary/future

- Banks and financial institutions
- Telecom operators
- Government services
- Enterprises
- Customer-support organizations
- High-value employees/executives
- Security operations teams

Do not make the consumer product dependent on enterprise-only workflows.

---

## 5. Core User Flow

### First installation

1. Install VaaniRakshak.
2. Explain permissions before requesting them.
3. Request only permissions/roles actually required by the current feature set.
4. Configure protection.
5. Optionally configure trusted contacts / consented speaker profiles.
6. Enable Android call-screening role where supported.

### Incoming call

- Saved contact = KNOWN.
- Number not saved in the user's contacts = UNKNOWN.
- UNKNOWN calls automatically enter protection analysis.
- Protection remains active unless explicitly disabled through the security control/policy.
- Do not silently disable protection simply because a caller is trusted.

### During call

Minimal overlay/security surface:

`🛡 Protected`

and:

`Risk 37/100`

The risk bar changes as evidence arrives.

### Critical threat

A sufficiently confirmed critical threat enters a configurable confirmation/intervention policy.

Default demo policy:

- observe risk evolution for approximately 10 seconds;
- do not hard-code 10 seconds into the ML model;
- if critical confidence is reached, terminate/protect according to supported Android/telecom capabilities;
- notify the user.

### After call

Show a full animated security explanation:

- Call protected / terminated
- Overall risk score
- Synthetic voice probability
- Speaker similarity if available
- Impersonation signal
- Fraud intent
- Social-engineering indicators
- Sensitive request detected
- Why the decision happened
- Recommended safe next action
- Report / dismiss

---

## 6. Attack Lab

The Attack Lab is a controlled research/demo environment.

### Purpose

Demonstrate the exact threat VaaniRakshak is designed to defend against.

### Required demo

1. Record/obtain a user's voice only with explicit consent.
2. Generate a synthetic voice resembling that consenting speaker.
3. Use a controlled scripted conversation.
4. Place the demonstration call through an appropriate test setup.
5. VaaniRakshak receives the synthetic sample through its permitted audio/demo integration.
6. VaaniRakshak detects:
   - high speaker similarity;
   - high synthetic probability;
   - impersonation;
   - malicious conversation context if present.
7. Risk rises.
8. Protection action occurs.
9. Explanation UI appears.

### Safety requirements

- Only use voices with explicit consent or appropriately licensed datasets.
- Clearly label generated samples as synthetic.
- Never build Attack Lab as a covert impersonation tool.
- No unauthorized voice harvesting.
- No identity theft workflows.
- Include an explicit `DEMO / CONSENTED SAMPLE` marker in the Attack Lab UI.

### Attack Lab capabilities

- Language selection
- Consented reference voice
- Script selection
- Synthetic speech generation
- Voice-conversion/voice-cloning research adapters
- Codec/telephone-quality simulation
- Noise/reverb simulation
- Exportable demo metadata
- Sample playback in the controlled lab
- Model evaluation hooks

The generation engine must be provider/model agnostic.

---

## 7. VaaniRakshak AI

### 7.1 Voice authenticity

Detect bona-fide vs synthetic/manipulated speech.

Initial research directions:

- WavLM/self-supervised speech representations
- AASIST-style anti-spoofing
- RawNet-style anti-spoofing
- spectro-temporal analysis
- pitch/prosody analysis
- codec/compression robustness
- temporal consistency

Output example:

```json
{
  "synthetic_probability": 0.94,
  "human_probability": 0.06,
  "confidence": 0.91
}
```

Do not treat one model as ground truth. Support ensemble/independent detector experiments.

### 7.2 Speaker verification

Use ECAPA-TDNN or an equivalent strong speaker-embedding architecture.

Only create trusted speaker profiles with consent.

Store protected embeddings rather than raw recordings where practical.

Important:

High speaker similarity does NOT mean legitimate.

Example:

`speaker_similarity = 0.91`

`synthetic_probability = 0.96`

Interpretation:

"The voice resembles the trusted person, but synthetic evidence is strong."

### 7.3 Speech-to-text

Use a multilingual STT abstraction, initially compatible with Whisper/faster-whisper and other suitable engines.

Use chunked near-real-time transcription.

Maintain rolling conversation state.

### 7.4 Conversation intelligence

Use multilingual transformer models and structured classifiers.

Detect:

#### Intent

- MONEY_TRANSFER
- OTP_REQUEST
- PASSWORD_REQUEST
- PIN_REQUEST
- REMOTE_ACCESS
- APK_INSTALLATION
- BANK_VERIFICATION
- IDENTITY_VERIFICATION
- PERSONAL_INFORMATION
- EMERGENCY
- JOB_PAYMENT
- INVESTMENT
- INSURANCE
- THREAT
- BLACKMAIL
- NORMAL_CONVERSATION

#### Social engineering

- URGENCY
- FEAR
- AUTHORITY
- SECRECY
- PRESSURE
- EMOTIONAL_MANIPULATION
- THREAT
- REWARD
- SCARCITY
- ISOLATION

#### Threat categories

- voice impersonation
- financial fraud
- credential theft
- remote-access scams
- employment scams
- emergency scams
- extortion
- malicious instructions
- other suspicious behavior

### 7.5 Temporal risk

Do not independently judge every sentence.

Maintain a rolling timeline:

`8 → 21 → 38 → 64 → 83 → 94`

A sequence of individually harmless statements can become dangerous.

### 7.6 Risk engine

Combine:

- voice authenticity
- speaker anomaly
- impersonation
- conversation intent
- social engineering
- caller context
- sensitive action
- temporal trajectory

Risk score:

`0–29 SAFE`

`30–59 LOW`

`60–79 MEDIUM`

`80–89 HIGH`

`90–100 CRITICAL`

Weights must be configurable and validated through evaluation. Do not present arbitrary weights as scientific truth.

### 7.7 Decision engine

Possible outputs:

- CONTINUE
- MONITOR
- WARN
- CRITICAL_PROTECTION
- TERMINATE_IF_SUPPORTED

The LLM must NOT directly control call termination.

The deterministic/policy decision layer controls actions.

---

## 8. Multilingual Requirement

VaaniRakshak and Attack Lab must be designed for broad global multilingual coverage.

Priority: strong Indian-language support plus global-language architecture.

Indian-language targets include, at minimum:

- Hindi
- English
- Hinglish
- Marathi
- Bengali
- Tamil
- Telugu
- Kannada
- Malayalam
- Gujarati
- Punjabi
- Urdu
- Odia
- Assamese
- Nepali
- Sanskrit

The architecture must support adding further Indian and world languages without rewriting the system.

Global targets should include major language families and languages such as Spanish, French, German, Portuguese, Arabic, Mandarin Chinese, Japanese, Korean, Russian and others supported by the selected multilingual models.

Do not claim identical performance across every language without benchmark evidence.

Maintain:

`LANGUAGE_COVERAGE_MATRIX.md`

with actual tested capabilities.

---

## 9. Privacy

Default data path:

Audio chunk → inference → structured result → audio discarded.

Do not build a call-recording product.

Store only the minimum structured information necessary for security, debugging, analytics and consented evaluation.

Example:

```json
{
  "timestamp": "...",
  "risk_score": 91,
  "synthetic_probability": 0.87,
  "threats": ["impersonation", "otp_request"]
}
```

Consent and retention policies must be explicit.

---

## 10. Android Requirements

Use real Android APIs and roles.

Core direction:

- Kotlin
- Jetpack Compose
- Android Telecom APIs
- CallScreeningService
- RoleManager
- Contacts APIs
- Notifications
- appropriate foreground-service architecture where legitimately required
- WebSocket client
- Room/local preferences where useful

Important platform constraint:

Do not claim that an ordinary third-party CallScreeningService automatically receives unrestricted raw cellular call audio.

Design audio acquisition around supported/authorized paths.

Support three deployment modes:

1. Consumer Android protection
2. Controlled demo/research audio path
3. Future telecom/operator/deep integration

---

## 11. Backend

Primary stack:

- Python
- FastAPI
- WebSockets
- PyTorch
- torchaudio
- librosa
- NumPy
- Hugging Face Transformers/Datasets
- faster-whisper
- Supabase/PostgreSQL
- Redis
- Redis Streams or equivalent event mechanisms initially
- FAISS where vector search is needed
- Docker/Docker Compose
- Nginx where appropriate
- MLflow or Weights & Biases

### Database

Supabase/PostgreSQL is the source of truth.

Store:

- users
- devices
- trusted contacts
- consent records
- speaker profiles/metadata
- calls
- risk events
- incidents
- model versions
- evaluation metadata
- language coverage
- audit logs

### High traffic

Redis handles:

- short-lived session state
- live risk state
- caching
- rate limiting
- streaming/event coordination

Architect event boundaries so Kafka can be introduced later for very large deployments.

Do not add Kafka solely for decoration in the prototype.

---

## 12. Dashboard

React + TypeScript + Vite + Tailwind.

Dashboard screens:

- Live Security Command Center
- Active call
- Live risk
- Voice authenticity
- Speaker similarity
- Threat signals
- Conversation transcript
- Risk timeline
- Decision
- Dataset Explorer
- Attack Lab
- Model Evidence
- Language Coverage
- Evaluation Metrics

---

## 13. SIH Judge Demo

### Demo 1 — Normal call

Your real voice:

- synthetic probability low
- trusted speaker similarity high
- threat low
- call continues

### Demo 2 — AI-cloned voice

Controlled synthetic clone of your consented voice:

- speaker similarity high
- synthetic probability high
- impersonation high
- scam intent high
- risk rises dynamically
- protection/termination occurs according to demo policy
- animated explanation appears

### Demo 3 — Human scammer

Real human voice:

- synthetic probability low
- fraud intent high
- social engineering high
- sensitive request high
- overall risk critical
- protection occurs

The third demo proves VaaniRakshak is not merely a deepfake detector.

---

## 14. Evidence Requirements

The repository must contain:

- dataset cards
- provenance
- licenses
- consent metadata
- train/validation/test splits
- model cards
- training configuration
- experiment results
- confusion matrices
- ROC/PR metrics
- per-language metrics
- unseen-generator evaluation
- telephone/codec robustness evaluation
- Attack Lab samples that are legally/consensually usable
- demo scripts

Never fabricate dataset sizes, accuracy, latency, or benchmark results.

---

## 15. Non-Functional Requirements

- low-latency security decisions
- graceful degradation
- multilingual support
- privacy by default
- auditable decisions
- model versioning
- reproducible training
- testability
- secure APIs
- rate limiting
- observability
- fault tolerance
- configurable policies
- no single AI component has unrestricted authority over destructive actions

---

## 16. Success Criteria

The prototype is successful when:

1. Android app installs and onboards.
2. Call-screening role can be configured where supported.
3. Unknown numbers automatically enter protection.
4. Minimal security UI works.
5. Controlled synthetic voice can be generated in Attack Lab.
6. VaaniRakshak detects synthetic speech.
7. Speaker similarity can be demonstrated with consent.
8. Conversation threats can be detected.
9. Risk evolves over time.
10. Critical demo calls trigger the configured protection action.
11. Post-call explanation is understandable.
12. Human-voice scams can also be detected.
13. Multilingual pipeline works for the tested language set.
14. Dataset/model evidence is inspectable.
15. No fabricated scientific claims exist.
