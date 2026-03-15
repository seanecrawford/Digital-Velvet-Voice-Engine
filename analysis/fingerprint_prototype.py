import json
import sys
from pathlib import Path

import librosa
import numpy as np


def estimate_vibrato(f0_values: np.ndarray, sr_hz: float) -> tuple[float, float]:
    valid = f0_values[np.isfinite(f0_values)]
    if len(valid) < 16:
        return 0.0, 0.0

    centered = valid - np.mean(valid)
    if np.allclose(centered, 0):
        return 0.0, 0.0

    spectrum = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(len(centered), d=1.0 / sr_hz)

    mask = (freqs >= 3.0) & (freqs <= 9.0)
    if not np.any(mask):
        return 0.0, 0.0

    band_spectrum = np.abs(spectrum[mask])
    band_freqs = freqs[mask]
    peak_idx = int(np.argmax(band_spectrum))

    vibrato_rate = float(band_freqs[peak_idx])
    vibrato_depth = float(np.std(centered))

    return vibrato_rate, vibrato_depth


def analyze_audio(audio_path: Path) -> dict:
    y, sr = librosa.load(audio_path.as_posix(), sr=None, mono=True)

    if y.size == 0:
        raise ValueError("Audio file appears to be empty.")

    duration_sec = float(len(y) / sr)

    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))

    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_mean = float(np.mean(spectral_centroid))
    centroid_std = float(np.std(spectral_centroid))

    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sr,
    )

    valid_f0 = f0[np.isfinite(f0)]
    if len(valid_f0) > 0:
        pitch_mean_hz = float(np.mean(valid_f0))
        pitch_std_hz = float(np.std(valid_f0))
        voiced_ratio = float(np.mean(np.isfinite(f0)))
    else:
        pitch_mean_hz = 0.0
        pitch_std_hz = 0.0
        voiced_ratio = 0.0

    hop_length = 512
    frame_rate_hz = sr / hop_length
    vibrato_rate, vibrato_depth = estimate_vibrato(f0, frame_rate_hz)

    profile = {
        "file": audio_path.name,
        "sample_rate": sr,
        "duration_sec": round(duration_sec, 3),
        "features": {
            "rms_mean": round(rms_mean, 6),
            "rms_std": round(rms_std, 6),
            "spectral_centroid_mean": round(centroid_mean, 3),
            "spectral_centroid_std": round(centroid_std, 3),
            "zero_crossing_rate_mean": round(zcr_mean, 6),
            "pitch_mean_hz": round(pitch_mean_hz, 3),
            "pitch_std_hz": round(pitch_std_hz, 3),
            "voiced_ratio": round(voiced_ratio, 6),
            "vibrato_rate_hz": round(vibrato_rate, 3),
            "vibrato_depth_hz": round(vibrato_depth, 3),
        },
    }

    return profile


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analysis/fingerprint_prototype.py <audio_file> [profile_name]")
        sys.exit(1)

    audio_path = Path(sys.argv[1]).resolve()
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        sys.exit(1)

    profile_name = sys.argv[2] if len(sys.argv) > 2 else audio_path.stem
    output_dir = Path(__file__).resolve().parent.parent / "presets"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{profile_name}.json"

    profile = analyze_audio(audio_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print(f"Saved profile to: {output_path}")


if __name__ == "__main__":
    main()