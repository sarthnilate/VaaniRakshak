# Governance & Architectural Rules: VAANIRAKSHAK

**Document Status:** Binding Technical & Ethical Directive  
**Target Group:** All System Modules, Engineers, and Contributors  

---

## 1. Fundamental Product Principles

### Rule 1.1: Privacy-First Non-Recording Core
- VaaniRakshak is a **real-time threat detection engine**, NOT a call recording application.
- Raw audio PCM chunks MUST remain strictly in transient volatile memory during model feature extraction and MUST be immediately freed/overwritten.
- Under NO circumstances shall raw caller or receiver voice audio be persisted to disk, stored in database logs, or uploaded to unencrypted third-party storage.

### Rule 1.2: Strict Consent for Biometric Profiles
- Enrolling a speaker profile REQUIRES explicit, interactive user consent.
- Speaker profiles MUST store mathematical embeddings (e.g., 192-dimensional vector floats), NEVER raw audio recordings.
- Users MUST be provided with a 1-tap option to inspect, update, or permanently delete all enrolled biometric embeddings.

---

## 2. Attack Lab Ethical & Operational Boundaries

### Rule 2.1: Non-Covert Research Guarantee
- System A (Attack Lab) is strictly a controlled research and demonstration framework.
- Generated synthetic audio MUST incorporate provenance metadata (`is_synthetic: true`, `generator_family`, `consent_hash`, `timestamp`).
- Attack Lab MUST NEVER be adapted, refactored, or exposed as a covert voice impersonation tool.

### Rule 2.2: Modular Generator Decoupling
- The defensive engine (System B) MUST NOT rely on proprietary features of any single synthetic voice generator.
- All generators MUST conform to the `VoiceGenerator` abstract adapter interface.

---

## 3. Android Platform & Engineering Directives

### Rule 3.1: Zero Invented APIs
- Engineers MUST NOT invent non-existent Android APIs or claim that standard third-party apps can freely tap live cellular voice calls programmatically without platform permissions.
- The app MUST maintain explicit separation between:
  1. *Tier 1 (Consumer Mode)*: Official `CallScreeningService` + Local simulated test loopback.
  2. *Tier 2 (Research/Demo Mode)*: WebSocket audio stream injector for hackathon evaluation.
  3. *Tier 3 (Carrier Mode)*: Carrier/Operator gRPC stream protocol.

### Rule 3.2: Non-Intrusive Live HUD Design
- The live call security indicator MUST remain minimal (`🛡 Protected | Risk 37/100`).
- It MUST NOT block standard call controls (Answer, Reject, Speaker, Mute) during normal risk levels.
- Full-screen alerts and 10-second countdown intervention windows activate ONLY when risk escalates to CRITICAL ($\ge 90$).

---

## 4. AI & Risk Engine Rules

### Rule 4.1: Multi-Evidence Independence
- Risk scores MUST be derived from multiple independent evidence sources (Voice Authenticity, Speaker Verification, Intent Classification, Social Engineering, Temporal Trajectory).
- Single-feature binary classification is forbidden for safety-critical decisions.

### Rule 4.2: Deterministic Action Control
- Call termination, emergency alerts, and intervention triggers MUST be executed by deterministic rule evaluation and temporal GRU state bounds.
- Generative Large Language Models (LLMs) MAY be used for natural language explanation generation and post-call summaries, but MUST NEVER directly trigger call disconnection or alter safety thresholds.

### Rule 4.3: Decoupled Policy Configuration
- Operational parameters (e.g., 10-second confirmation window, sensitivity thresholds, high-risk intent weights) MUST be configurable via environment variables and policy configuration schemas.
- Policies MUST NOT be hard-coded into machine learning model weights or compiled binaries.

---

## 5. Development & Benchmark Standards

### Rule 5.1: Empirical Benchmarking Only
- Engineers MUST NOT claim arbitrary accuracy, F1, or EER metrics without executing repeatable benchmark scripts against documented test datasets.
- Test splits MUST be speaker-disjoint and generator-disjoint to prevent data leakage.

### Rule 5.2: Memory.md Tracking
- After completing any implementation phase, `Memory.md` MUST be updated immediately with exact reproduction commands, modified files, test results, and known limitations.
