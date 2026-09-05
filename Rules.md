# VaaniRakshak — AI/Engineering Rules

## 1. Prime Directive

Build a real, testable, privacy-first security product.

Never fake functionality, benchmark results, permissions, Android capabilities, dataset provenance, or model performance.

If a feature cannot be implemented on ordinary Android, document the platform constraint and implement the closest legitimate architecture.

---

## 2. Technology Rules

### Android

Use:

- Kotlin
- Jetpack Compose
- Android Telecom APIs
- CallScreeningService
- RoleManager
- Contacts APIs
- Kotlin Coroutines
- AndroidX

Avoid introducing unnecessary frameworks.

### Backend

Use:

- Python
- FastAPI
- Pydantic
- PyTorch
- torchaudio
- librosa
- NumPy
- Transformers
- Datasets
- faster-whisper
- Supabase/PostgreSQL
- Redis
- Docker

### Frontend

Use:

- React
- TypeScript
- Vite
- Tailwind
- Recharts

---

## 3. AI Rules

No single AI model is the entire security system.

Use layered evidence:

```text
Voice
+
Identity
+
Conversation
+
Context
+
Temporal behavior
=
Risk
```

The LLM is never the sole detector.

The LLM must never directly terminate calls.

The policy/decision engine controls security actions.

---

## 4. Voice Clone Attack Lab Rules

Attack Lab is strictly controlled.

Allowed:

- explicit consented reference voices
- licensed datasets
- synthetic samples for security research
- controlled scripts
- test-phone demonstrations

Forbidden:

- unauthorized voice collection
- covert cloning
- impersonating real people without consent
- operational fraud workflows
- harvesting voices from calls
- deceptive deployment

Every generated demo sample should have metadata indicating:

- consent/source
- generator
- language
- generation family
- timestamp
- synthetic label

---

## 5. Dataset Rules

Every dataset must have:

- source
- license/permission status
- version
- language
- speaker information as legally appropriate
- label
- generation family if synthetic
- preprocessing
- split

Never claim an external dataset is ours.

Never copy restricted audio into the repository.

For external data, store manifests/provenance and only retain audio when permitted.

---

## 6. Training Rules

Use speaker-disjoint splits.

Where possible use generator-disjoint evaluation.

Do not allow the same speaker to leak across train/test.

Do not train and test on identical samples.

Include:

- bona-fide speech
- synthetic speech
- voice-conversion samples
- cloned speech
- codec-degraded speech
- noise/reverb conditions
- multilingual speech
- unseen synthetic conditions

---

## 7. Metrics Rules

Never report accuracy alone.

Report appropriate metrics such as:

- precision
- recall
- F1
- ROC-AUC where appropriate
- PR-AUC where appropriate
- EER for speaker/anti-spoofing contexts where appropriate
- confusion matrix
- latency
- per-language metrics

Separate validation and held-out test results.

---

## 8. Multilingual Rules

Never silently translate every language into English and claim native multilingual intelligence.

Maintain language IDs.

Track performance by language.

Support code-switching such as Hinglish.

Maintain a language coverage matrix.

If a language is supported by the underlying foundation model but not validated by VaaniRakshak, mark it as:

`MODEL-SUPPORTED / NOT-YET-BENCHMARKED`

not simply `FULLY SUPPORTED`.

---

## 9. Privacy Rules

Default:

```text
audio
 ↓
inference
 ↓
structured result
 ↓
discard
```

Do not create a call-recording library.

Do not retain raw call audio by default.

Do not put sensitive audio into logs.

Encrypt sensitive stored data.

Minimize retention.

---

## 10. Android Permission Rules

Explain each permission before requesting it.

Request only permissions required by the active feature.

Do not ask for permissions merely because they might be useful later.

Never claim a permission grants capabilities it does not grant.

Never claim CallScreeningService provides unrestricted call audio.

---

## 11. Error Handling

Every backend endpoint must:

- validate input
- return structured errors
- log safely
- avoid leaking secrets
- handle model timeouts
- handle Redis failures
- handle WebSocket disconnects

AI failure must degrade safely.

Example:

```text
ML unavailable
     ↓
do not fabricate a SAFE result
     ↓
show protection unavailable / limited mode
     ↓
apply conservative policy
```

---

## 12. Security

Never hard-code:

- API keys
- database passwords
- model-provider secrets
- JWT secrets

Use `.env`.

Commit only `.env.example`.

Use authentication and authorization on production endpoints.

Apply rate limits.

Validate uploaded files.

Limit audio size and duration.

---

## 13. Code Quality

Prefer:

- small modules
- typed interfaces
- dependency injection
- unit tests
- integration tests
- clear naming
- configuration over hard-coding

Avoid:

- giant files
- duplicate logic
- magic constants
- hidden global state
- unused dependencies
- unnecessary abstraction

---

## 14. Risk Engine Rules

Risk must be explainable.

Every critical decision should have structured evidence.

Example:

```json
{
  "risk_score": 94,
  "band": "CRITICAL",
  "evidence": [
    {"type": "synthetic_voice", "score": 0.96},
    {"type": "speaker_similarity", "score": 0.92},
    {"type": "money_request", "score": 0.98},
    {"type": "urgency", "score": 0.91}
  ]
}
```

---

## 15. UI Rules

Security UI must be:

- minimal during calls
- readable
- accessible
- non-blocking unless policy requires intervention
- understandable in seconds

Use animation to communicate changing risk, not for decoration.

Post-call explanation can be richer.

---

## 16. AI Agent Rules

When coding:

1. Inspect the existing repository before changing it.
2. Read PRD, Architecture, Rules and Phases first.
3. Read Memory.md after it exists.
4. Do not rewrite working code without a reason.
5. Run tests after meaningful changes.
6. Update documentation after architecture changes.
7. Update Memory.md after every completed phase.
8. Never invent files or APIs.
9. Never fabricate test output.
10. If blocked, report the exact blocker and implement a clean interface/mock only when appropriate.

---

## 17. Demo Rules

The SIH demo must be reproducible.

Maintain:

- demo scripts
- sample metadata
- fallback recordings where legally/consensually allowed
- deterministic configuration
- offline fallback for non-network-critical visual portions
- clear distinction between live detection and pre-generated demo data

Never secretly substitute a prerecorded result while claiming it is live inference.

---

## 18. Judge Honesty Rule

If asked:

"Can ordinary Android capture cellular call audio?"

Answer honestly.

If asked:

"What did you train on?"

Show actual provenance.

If asked:

"What is your accuracy?"

Show measured results and conditions.

If asked:

"Does this detect all languages perfectly?"

No. Explain validated coverage and multilingual architecture.

Credibility is more important than exaggerated claims.
