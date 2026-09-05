import base64
import logging
import numpy as np
from typing import Dict, Any
from backend.services.ai.audio_processor import decode_pcm_b64

logger = logging.getLogger("vaanirakshak.attack_lab.degradation")


class TelecomDegradationSimulator:
    """Simulates real-world cellular network codecs, bandpass filtering, and acoustic noise impairments."""

    def apply_telephony_filter(self, signal: np.ndarray, low_cut: float = 300.0, high_cut: float = 3400.0, sample_rate: int = 16000) -> np.ndarray:
        """Simulates telephony narrowband (300Hz - 3.4kHz) or wideband (50Hz - 7kHz) bandpass frequency response."""
        if len(signal) == 0:
            return signal

        fft_vals = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1.0 / sample_rate)

        # Apply smooth frequency mask
        mask = (freqs >= low_cut) & (freqs <= high_cut)
        fft_vals[~mask] *= 0.05

        filtered_signal = np.fft.irfft(fft_vals, n=len(signal))
        return filtered_signal.astype(np.float32)

    def inject_noise(self, signal: np.ndarray, snr_db: float = 15.0) -> np.ndarray:
        """Injects acoustic background noise at specified Signal-to-Noise Ratio (SNR dB)."""
        if len(signal) == 0:
            return signal

        signal_power = np.mean(signal ** 2)
        if signal_power == 0:
            return signal

        noise_power = signal_power / (10 ** (snr_db / 10.0))
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        degraded = signal + noise
        return np.clip(degraded, -1.0, 1.0).astype(np.float32)

    def apply_amr_codec_compression(self, signal: np.ndarray) -> np.ndarray:
        """Simulates AMR-WB (Adaptive Multi-Rate Wideband) low-bitrate quantization noise."""
        if len(signal) == 0:
            return signal

        # 4-bit quantization simulation to mimic AMR-WB 12.65kbps compression artifacts
        quant_levels = 16.0
        quantized = np.round(signal * quant_levels) / quant_levels
        return quantized.astype(np.float32)

    def degrade_audio_chunk(
        self,
        pcm_b64: str,
        codec: str = "AMR-WB",
        snr_db: float = 15.0,
        narrowband: bool = True
    ) -> str:
        """Passes raw PCM chunk through full telecom degradation pipeline and returns degraded base64 PCM string."""
        signal = decode_pcm_b64(pcm_b64)
        if len(signal) == 0:
            return pcm_b64

        # 1. Telephony Bandpass Filter
        if narrowband:
            signal = self.apply_telephony_filter(signal, low_cut=300.0, high_cut=3400.0)

        # 2. Codec Quantization Noise
        if codec in ["AMR-WB", "AMR-NB", "G.711"]:
            signal = self.apply_amr_codec_compression(signal)

        # 3. Background Noise Injection
        if snr_db < 30.0:
            signal = self.inject_noise(signal, snr_db=snr_db)

        # Re-encode to 16-bit PCM base64
        int16_array = (signal * 32767.0).astype(np.int16)
        raw_bytes = int16_array.tobytes()
        return base64.b64encode(raw_bytes).decode("utf-8")


degradation_simulator = TelecomDegradationSimulator()
