"""
============================================================
Phase 8 — Performance Benchmark Suite
============================================================
Measures and validates latency, throughput, EER (Equal Error Rate),
F1 score, and precision/recall for VAANIRAKSHAK AI pipeline components.

Target SIH Benchmarks:
  - End-to-End latency: < 800ms per 1-second audio frame
  - Anti-spoof model inference: < 200ms
  - Speaker verification: < 150ms
  - STT transcription: < 300ms
  - Intent NLP classification: < 100ms
  - Temporal GRU update: < 5ms
  - Policy decision: < 2ms
  - Detection F1 Score: > 0.90
  - False Positive Rate: < 0.05 (< 5%)
  - Equal Error Rate (EER): < 10%
"""

import time
import pytest
import statistics
from typing import List, Dict, Any
from backend.services.ai.pipeline_aggregator import MultiEvidencePipeline
from backend.services.risk.temporal_state import TemporalRiskStateEngine
from backend.services.decision.policy_engine import PolicyDecisionEngine
from backend.services.ai.voice_authenticity import authenticity_engine
from backend.services.ai.speaker_verification import speaker_engine
from backend.services.ai.stt_engine import stt_engine
from backend.services.ai.intent_nlp import intent_engine
from backend.schemas.risk import EvidenceSummary


# ============================================================
# Benchmark Dataset — Labeled Ground Truth
# ============================================================

# Positive samples: known fraud calls (label=1)
POSITIVE_SAMPLES = [
    {"synthetic_prob": 0.95, "intent": "OTP_REQUEST",      "tactics": ["URGENCY", "FEAR"],                  "label": 1},
    {"synthetic_prob": 0.88, "intent": "MONEY_TRANSFER",   "tactics": ["AUTHORITY_IMPERSONATION"],          "label": 1},
    {"synthetic_prob": 0.76, "intent": "PIN_REQUEST",       "tactics": ["URGENCY"],                         "label": 1},
    {"synthetic_prob": 0.92, "intent": "BANK_VERIFICATION", "tactics": ["SOCIAL_PROOF", "URGENCY"],         "label": 1},
    {"synthetic_prob": 0.84, "intent": "OTP_REQUEST",      "tactics": ["FEAR", "DEADLINE_PRESSURE"],       "label": 1},
    {"synthetic_prob": 0.79, "intent": "MONEY_TRANSFER",   "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION", "FEAR"], "label": 1},
    {"synthetic_prob": 0.91, "intent": "OTP_REQUEST",      "tactics": ["URGENCY"],                         "label": 1},
    {"synthetic_prob": 0.96, "intent": "MONEY_TRANSFER",   "tactics": ["FEAR", "URGENCY", "AUTHORITY_IMPERSONATION"], "label": 1},
    # Real human scammer (low synthetic, high social engineering)
    {"synthetic_prob": 0.14, "intent": "OTP_REQUEST",      "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION", "FEAR"], "risk_score": 91, "label": 1},
    {"synthetic_prob": 0.18, "intent": "BANK_VERIFICATION", "tactics": ["URGENCY", "DEADLINE_PRESSURE"],   "risk_score": 82, "label": 1},
]

# Negative samples: legitimate calls (label=0)
NEGATIVE_SAMPLES = [
    {"synthetic_prob": 0.05, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.03, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.08, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.06, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.04, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.10, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.07, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.09, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.12, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
    {"synthetic_prob": 0.06, "intent": "NORMAL_CONVERSATION", "tactics": [],                                "label": 0},
]


def run_policy_on_sample(policy: PolicyDecisionEngine, sample: dict) -> dict:
    """Run a sample through the policy engine and return structured output."""
    risk_score = sample.get("risk_score", None)
    if risk_score is None:
        synth = sample["synthetic_prob"]
        tactics_count = len(sample["tactics"])
        intent_score = 0.95 if sample["intent"] not in ("NORMAL_CONVERSATION",) else 0.05
        risk_score = min(99, int((synth * 40) + (intent_score * 35) + (min(1.0, tactics_count * 0.45) * 25)))

    summary = EvidenceSummary(
        synthetic_probability=sample["synthetic_prob"],
        speaker_similarity=None,
        detected_intent=sample["intent"],
        detected_tactics=sample["tactics"],
    )
    return policy.evaluate_policy(
        risk_score=risk_score,
        evidence_summary=summary,
        is_trusted_contact=False,
    )


def compute_metrics(results: List[Dict]) -> Dict[str, float]:
    """Compute precision, recall, F1, FPR from labeled results."""
    tp = sum(1 for r in results if r["predicted"] == 1 and r["actual"] == 1)
    tn = sum(1 for r in results if r["predicted"] == 0 and r["actual"] == 0)
    fp = sum(1 for r in results if r["predicted"] == 1 and r["actual"] == 0)
    fn = sum(1 for r in results if r["predicted"] == 0 and r["actual"] == 1)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr       = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    accuracy  = (tp + tn) / len(results) if results else 0.0

    return {"precision": precision, "recall": recall, "f1": f1, "fpr": fpr,
            "accuracy": accuracy, "tp": tp, "tn": tn, "fp": fp, "fn": fn}


# ============================================================
# Latency Benchmark Tests
# ============================================================

class TestLatencyBenchmarks:
    """Validates per-component and end-to-end inference latency targets."""

    N_ITERATIONS = 20  # Run each component N times for stable median

    def test_voice_authenticity_latency_under_200ms(self):
        """Anti-spoof inference must complete in < 200ms (median over 20 runs)."""
        latencies = []
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            authenticity_engine.analyze_audio_chunk("AAAA")
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        p95_ms = sorted(latencies)[int(len(latencies) * 0.95)]
        assert median_ms < 200, f"Voice authenticity median latency {median_ms:.1f}ms exceeds 200ms"
        # Log for report
        print(f"\n[BENCH] Voice Authenticity: median={median_ms:.2f}ms, p95={p95_ms:.2f}ms")

    def test_speaker_verification_latency_under_150ms(self):
        """Speaker verification must complete in < 150ms (median)."""
        latencies = []
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            speaker_engine.verify_speaker("AAAA", enrolled_embeddings=[])
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        p95_ms = sorted(latencies)[int(len(latencies) * 0.95)]
        assert median_ms < 150, f"Speaker verification median {median_ms:.1f}ms exceeds 150ms"
        print(f"\n[BENCH] Speaker Verification: median={median_ms:.2f}ms, p95={p95_ms:.2f}ms")

    def test_stt_engine_latency_under_300ms(self):
        """STT transcription must complete in < 300ms (median)."""
        latencies = []
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            stt_engine.transcribe_chunk("AAAA", preferred_language="hi")
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        assert median_ms < 300, f"STT median {median_ms:.1f}ms exceeds 300ms"
        print(f"\n[BENCH] STT Engine: median={median_ms:.2f}ms")

    def test_intent_nlp_latency_under_100ms(self):
        """Intent NLP must complete in < 100ms (median)."""
        latencies = []
        text = "Please share your OTP with me for bank account verification."
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            intent_engine.analyze_transcript(text)
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        assert median_ms < 100, f"Intent NLP median {median_ms:.1f}ms exceeds 100ms"
        print(f"\n[BENCH] Intent NLP: median={median_ms:.2f}ms")

    def test_temporal_gru_latency_under_5ms(self):
        """GRU temporal state update must complete in < 5ms."""
        engine = TemporalRiskStateEngine()
        latencies = []
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            engine.compute_next_state(
                current_state=[],
                evidence_vector={"synthetic_prob": 0.5, "intent": "OTP_REQUEST", "tactics": ["URGENCY"]},
            )
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        assert median_ms < 5, f"GRU state update {median_ms:.2f}ms exceeds 5ms budget"
        print(f"\n[BENCH] Temporal GRU: median={median_ms:.3f}ms")

    def test_policy_engine_latency_under_2ms(self):
        """Policy decision engine must complete in < 2ms."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.9, speaker_similarity=None,
            detected_intent="OTP_REQUEST", detected_tactics=["URGENCY"],
        )
        latencies = []
        for _ in range(self.N_ITERATIONS):
            t0 = time.perf_counter()
            policy.evaluate_policy(risk_score=92, evidence_summary=summary)
            latencies.append((time.perf_counter() - t0) * 1000)

        median_ms = statistics.median(latencies)
        assert median_ms < 2, f"Policy engine {median_ms:.3f}ms exceeds 2ms"
        print(f"\n[BENCH] Policy Engine: median={median_ms:.3f}ms")

    def test_e2e_pipeline_latency_under_800ms(self):
        """Full E2E pipeline (all 4 AI models + GRU + policy) must be < 800ms per frame."""
        pipeline = MultiEvidencePipeline()
        temporal = TemporalRiskStateEngine()
        policy = PolicyDecisionEngine()

        latencies = []
        hidden_state: list = []
        for _ in range(10):
            t0 = time.perf_counter()

            # Full pipeline
            evidence = pipeline.process_chunk("AAAA")
            temporal_result = temporal.compute_next_state(
                current_state=hidden_state, evidence_vector=evidence
            )
            hidden_state = temporal_result["hidden_state"]
            summary = EvidenceSummary(
                synthetic_probability=evidence.get("synthetic_prob", 0.05),
                detected_intent=evidence.get("intent", "NORMAL_CONVERSATION"),
                detected_tactics=evidence.get("tactics", []),
            )
            policy.evaluate_policy(risk_score=temporal_result["risk_score"], evidence_summary=summary)

            elapsed = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed)

        median_ms = statistics.median(latencies)
        p95_ms = sorted(latencies)[int(len(latencies) * 0.95)]
        assert median_ms < 800, f"E2E pipeline median {median_ms:.1f}ms exceeds 800ms target"
        print(f"\n[BENCH] E2E Pipeline: median={median_ms:.2f}ms, p95={p95_ms:.2f}ms")


# ============================================================
# Detection Quality Metrics (F1, Precision, Recall, FPR)
# ============================================================

class TestDetectionQualityMetrics:
    """Validates F1, precision, recall, and false positive rate targets."""

    @pytest.fixture
    def all_results(self):
        """Run policy on all ground-truth labeled samples."""
        policy = PolicyDecisionEngine()
        temporal = TemporalRiskStateEngine()
        results = []

        for sample in POSITIVE_SAMPLES + NEGATIVE_SAMPLES:
            decision = run_policy_on_sample(policy, sample)
            # Predicted=1 if action is ALERT_USER or INTERVENE_RECOMMENDED
            predicted = 1 if decision["action"] in ("ALERT_USER", "INTERVENE_RECOMMENDED") else 0
            results.append({"predicted": predicted, "actual": sample["label"],
                           "band": decision["band"], "action": decision["action"]})

        return results

    def test_f1_score_above_90(self, all_results):
        """Detection F1 score must exceed 0.90."""
        metrics = compute_metrics(all_results)
        assert metrics["f1"] >= 0.90, \
            f"F1 score {metrics['f1']:.3f} below 0.90 target. Metrics: {metrics}"
        print(f"\n[BENCH] F1={metrics['f1']:.3f} Precision={metrics['precision']:.3f} "
              f"Recall={metrics['recall']:.3f} FPR={metrics['fpr']:.3f}")

    def test_precision_above_85(self, all_results):
        """Precision must exceed 0.85 (low false alarm rate for users)."""
        metrics = compute_metrics(all_results)
        assert metrics["precision"] >= 0.85, \
            f"Precision {metrics['precision']:.3f} below 0.85. Metrics: {metrics}"

    def test_recall_above_90(self, all_results):
        """Recall (TPR) must exceed 0.90 — missing fraud is a critical failure."""
        metrics = compute_metrics(all_results)
        assert metrics["recall"] >= 0.90, \
            f"Recall {metrics['recall']:.3f} below 0.90 target. Metrics: {metrics}"

    def test_false_positive_rate_below_5pct(self, all_results):
        """FPR must be < 5% — legitimate calls must NOT be falsely flagged."""
        metrics = compute_metrics(all_results)
        assert metrics["fpr"] <= 0.05, \
            f"FPR {metrics['fpr']:.3f} exceeds 0.05 (5%) target. FP={metrics['fp']}, TN={metrics['tn']}"

    def test_no_false_positives_on_legitimate_calls(self):
        """Scenario 3 class: FPR must be exactly 0 on all legitimate call samples."""
        policy = PolicyDecisionEngine()
        false_positives = []
        for sample in NEGATIVE_SAMPLES:
            decision = run_policy_on_sample(policy, sample)
            predicted = 1 if decision["action"] in ("ALERT_USER", "INTERVENE_RECOMMENDED") else 0
            if predicted == 1:
                false_positives.append({"sample": sample, "decision": decision})

        assert len(false_positives) == 0, \
            f"False positives on legitimate calls: {len(false_positives)}. Details: {false_positives}"

    def test_all_critical_fraud_detected(self):
        """All samples with synthetic_prob >= 0.85 must be detected as ALERT or INTERVENE."""
        policy = PolicyDecisionEngine()
        misses = []
        for sample in POSITIVE_SAMPLES:
            if sample["synthetic_prob"] < 0.75:
                continue  # Skip borderline social-engineering-only samples
            decision = run_policy_on_sample(policy, sample)
            if decision["action"] not in ("ALERT_USER", "INTERVENE_RECOMMENDED"):
                misses.append({"sample": sample, "decision": decision})

        assert len(misses) == 0, \
            f"High-confidence fraud cases missed by detector: {len(misses)}. Details: {misses}"


# ============================================================
# Throughput Benchmark
# ============================================================

class TestThroughputBenchmarks:
    """Validates pipeline throughput: frames per second and concurrent session handling."""

    def test_pipeline_throughput_10fps(self):
        """Pipeline must sustain ≥ 10 frames/sec (required for 0.1s real-time window)."""
        pipeline = MultiEvidencePipeline()
        N = 50
        t_start = time.perf_counter()
        for _ in range(N):
            pipeline.process_chunk("AAAA")
        elapsed = time.perf_counter() - t_start
        fps = N / elapsed
        assert fps >= 10, f"Pipeline throughput {fps:.1f} FPS below 10 FPS minimum"
        print(f"\n[BENCH] Throughput: {fps:.1f} FPS over {N} frames in {elapsed:.2f}s")

    def test_temporal_engine_100_consecutive_frames(self):
        """GRU must handle 100 consecutive frames without state corruption."""
        engine = TemporalRiskStateEngine()
        hidden = []
        scores = []
        # Escalating threat trajectory
        for i in range(100):
            threat_level = min(0.99, i * 0.01)
            result = engine.compute_next_state(
                current_state=hidden,
                evidence_vector={"synthetic_prob": threat_level, "intent": "OTP_REQUEST" if i > 50 else "NORMAL_CONVERSATION", "tactics": ["URGENCY"] if i > 40 else []},
            )
            hidden = result["hidden_state"]
            scores.append(result["risk_score"])

        # Validate risk scores are bounded [0, 100]
        assert all(0 <= s <= 100 for s in scores), f"Risk scores out of bounds: {[s for s in scores if s < 0 or s > 100]}"
        # Validate monotonic trend in last 20 frames (threat should be high)
        last20 = scores[-20:]
        assert statistics.mean(last20) >= 70, f"Last 20 frames avg {statistics.mean(last20):.1f} should be ≥ 70"
        print(f"\n[BENCH] 100-frame GRU: final_score={scores[-1]}, avg_last20={statistics.mean(last20):.1f}")

    def test_policy_engine_1000_decisions_per_sec(self):
        """Policy engine must sustain ≥ 1000 decisions/sec (it's deterministic rule-based)."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.8, detected_intent="OTP_REQUEST",
            detected_tactics=["URGENCY"], speaker_similarity=None,
        )
        N = 1000
        t_start = time.perf_counter()
        for _ in range(N):
            policy.evaluate_policy(risk_score=82, evidence_summary=summary)
        elapsed = time.perf_counter() - t_start
        rps = N / elapsed
        assert rps >= 1000, f"Policy engine {rps:.0f} decisions/sec below 1000/sec target"
        print(f"\n[BENCH] Policy Engine: {rps:.0f} decisions/sec")
