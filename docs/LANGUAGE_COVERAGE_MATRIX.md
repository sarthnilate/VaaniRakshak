# Language Coverage Matrix

Status: **NOT YET POPULATED — no language has been benchmarked.**

Once populated (starting Phase 5, expanded through Phase 13), each
supported language will be tracked across these capabilities:

| Language | Language ID | STT | Voice Authenticity | Speaker Verification | Fraud NLP | Attack Lab Generation | Status |
|---|---|---|---|---|---|---|---|

Status values follow Rules.md section 8:

- `TESTED` — validated with recorded results in this repo
- `MODEL-SUPPORTED / NOT-YET-BENCHMARKED` — the underlying foundation model
  claims support, but VaaniRakshak has not measured it
- `NOT SUPPORTED` — no current path to support

Target language set (PRD.md section 8):

Indian priority: English, Hindi, Hinglish, Marathi, Bengali, Tamil, Telugu,
Kannada, Malayalam, Gujarati, Punjabi, Urdu, Odia, Assamese, Nepali,
Sanskrit.

Global: extensible to major world languages supported by the selected
multilingual foundation models (e.g. Spanish, French, German, Portuguese,
Arabic, Mandarin, Japanese, Korean, Russian), added as validated — never
claimed by default.
