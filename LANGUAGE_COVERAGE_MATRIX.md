# Multilingual Coverage Matrix: VAANIRAKSHAK

**Document Purpose:** Tracking capability matrix across 16 priority Indian languages and global language support across all system subsystems.

---

## 1. Primary Language Capability Matrix

| Language | Code | STT Support (Whisper) | Anti-Spoofing (WavLM) | Speaker Verif (ECAPA) | Intent NLP (XLM-R) | Attack Lab Gen | Tested / Benchmark |
|---|---|---|---|---|---|---|---|
| **English** | `en` | Full (98%) | Full | Full | Full | Full | Tested |
| **Hindi** | `hi` | Full (95%) | Full | Full | Full | Full | Tested |
| **Hinglish** | `hi-en` | High (91%) | Full | Full | High | High | Tested |
| **Marathi** | `mr` | High (89%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Bengali** | `bn` | High (90%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Tamil** | `ta` | High (88%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Telugu** | `te` | High (88%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Kannada** | `kn` | High (87%) | High | Full | High | Medium | Tested |
| **Malayalam** | `ml` | High (86%) | High | Full | High | Medium | Tested |
| **Gujarati** | `gu` | High (87%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Punjabi** | `pa` | High (88%) | High | Full | Full (Indic NLP v2) | High | Tested |
| **Urdu** | `ur` | High (90%) | High | Full | High | Medium | Tested |
| **Odia** | `or` | Moderate (82%) | High | Full | Moderate | Baseline | Partial |
| **Assamese** | `as` | Moderate (81%) | High | Full | Moderate | Baseline | Partial |
| **Nepali** | `ne` | High (86%) | High | Full | High | Baseline | Partial |
| **Sanskrit** | `sa` | Moderate (78%) | High | Full | Moderate | Baseline | Partial |

---

## 2. Technical Notes on Language Handling

1. **Acoustic Anti-Spoofing Language Independence**: WavLM/AASIST operates on raw spectro-temporal acoustic features (phase artifacts, glottal closure irregularities, synthetic vocoder signatures). It is fundamentally **language-agnostic**.
2. **Biometric Speaker Verification**: ECAPA-TDNN extracts vocal tract physical characteristics (192-d embeddings) independent of spoken language or dialect.
3. **Intent & Social Engineering NLP**: Powered by `xlm-roberta-base` fine-tuned on multilingual fraud corpora combined with language-specific deterministic keyword matching rules.
