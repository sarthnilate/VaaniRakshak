# Training Pipeline & Evaluation Specification: VAANIRAKSHAK

**Document Purpose:** Training loss formulations, optimization strategies, validation procedures, and anti-leakage metrics evaluation framework.

---

## 1. Anti-Spoofing Model Loss Formulation & Optimization

The Voice Authenticity network (WavLM/AASIST) is trained using a composite loss function combining Binary Cross-Entropy (BCE) with Angular Additive Margin Softmax (ArcFace) to maximize feature embedding separation between bona fide human voice and synthetic audio:

$$\mathcal{L}_{\text{total}} = \alpha \cdot \mathcal{L}_{\text{BCE}}(y, \hat{y}) + \beta \cdot \mathcal{L}_{\text{ArcFace}}(f_{\text{audio}}, y)$$

- **Optimizer**: AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay = $10^{-4}$).
- **Learning Rate Schedule**: Cosine Annealing with Warmup ($lr_{\text{max}} = 10^{-4}$, warmup epochs = 5).

---

## 2. Evaluation Metrics Framework

To maintain technical accuracy, VaaniRakshak relies exclusively on empirical benchmark metrics:

1. **Equal Error Rate (EER)**: Threshold where False Acceptance Rate (FAR) equals False Rejection Rate (FRR). Target: $\text{EER} \le 3.2\%$ on clean audio, $\le 6.5\%$ on compressed cellular audio.
2. **Precision, Recall, F1-Score**: Evaluated across `SAFE`, `HIGH`, and `CRITICAL` risk bands.
3. **Area Under ROC Curve (ROC-AUC)**: Overall discriminative ability across confidence thresholds.
4. **Latency Budget**: Total end-to-end processing latency $\le 300\text{ ms}$ per 1-second audio frame.

---

## 3. Data Leakage Prevention Protocol

- **Speaker Separation**: Zero speaker overlap between train and test splits.
- **Generator Isolation**: Synthetic test sets include unseen TTS engines (e.g. ElevenLabs v2, Bark) not present during training.
- **Codec Robustness**: Test sets evaluate degraded audio (AMR-WB 12.65 kbps) to mirror real cellular call quality.
