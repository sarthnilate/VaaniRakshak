# Privacy Architecture & Data Retention Guarantees: VAANIRAKSHAK

**Classification:** Strict Privacy-First Engineering Guarantee  

---

## 1. Zero Raw Audio Retention Policy

- **Transient In-Memory Feature Extraction**: Incoming audio PCM frames exist exclusively in volatile RAM during feature extraction.
- **Immediate Discard**: Upon completion of feature extraction (anti-spoofing score, speaker embedding, STT transcript chunk), the underlying audio memory buffer is immediately zeroed and freed.
- **Zero Disk Persistence**: Raw call audio is **NEVER** written to local device storage, database logs, server disk, or external cloud storage.

---

## 2. Consented Biometric Speaker Profile Privacy

- **Mathematical Embedding Storage**: Enrolled speaker profiles consist ONLY of 192-dimensional floating-point vectors extracted via ECAPA-TDNN.
- **Irreversible Feature Representation**: Raw acoustic audio CANNOT be reconstructed from a 192-dimensional speaker embedding vector.
- **User Control**: Users can inspect, export, or permanently purge all enrolled biometric vectors with a single tap in the Android client settings.

---

## 3. Incident Audit Logging & Data Minimization

When a high-risk call incident occurs:
- Logged fields: `timestamp`, `caller_hash`, `risk_score`, `risk_band`, `evidence_summary` (`synthetic_prob`, `speaker_similarity`, `detected_intent`).
- Excluded fields: **Zero raw call audio**, **Zero raw unencrypted speech recordings**.
