"""
full_stem_analyzer.py
----------------------

This module provides a high‑level analysis of a vocal stem.  It reads an
audio file, extracts global statistics (energy, brightness, pitch range,
voiced ratio, etc.) and produces a JSON file describing both the global
features and simplified timeline curves.  The result is a dictionary that
can be saved as a profile in the `presets/` directory.

The analysis is deliberately lightweight; it does not attempt to model
pronunciation or perform source separation.  Instead it focuses on
attributes that are useful for downstream vocal matching, such as
loudness distribution, spectral brightness, and pitch statistics.  If
additional features are needed (e.g., vibrato rate or syllable timing),
they can be added later in a backward‑compatible manner.

Usage::

    python full_stem_analyzer.py /path/to/vocal_stem.wav song_name

This will produce a JSON file named ``song_name.json`` in the ``presets``
folder.  See the accompanying README and docs for more details.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np


def compute_pitch_stats(f0: np.ndarray) -> Dict[str, float]:
    """Compute summary statistics from an array of fundamental frequency values.

    Parameters
    ----------
    f0 : np.ndarray
        Array of instantaneous pitch values in Hertz.  Unvoiced frames are
        encoded as ``np.nan``.

    Returns
    -------
    stats : dict
        A dictionary containing mean, median, min, max and standard deviation
        of the voiced pitch values.  Values are 0.0 if no pitch is detected.
    """
    voiced = f0[np.isfinite(f0) & (f0 > 0)]
    if len(voiced) == 0:
        return {
            "pitch_mean_hz": 0.0,
            "pitch_median_hz": 0.0,
            "pitch_std_hz": 0.0,
            "pitch_min_hz": 0.0,
            "pitch_max_hz": 0.0,
        }
    return {
        "pitch_mean_hz": float(np.mean(voiced)),
        "pitch_median_hz": float(np.median(voiced)),
        "pitch_std_hz": float(np.std(voiced)),
        "pitch_min_hz": float(np.min(voiced)),
        "pitch_max_hz": float(np.max(voiced)),
    }


def analyze_audio(audio_path: Path) -> Dict[str, object]:
    """Analyze a vocal stem and return a feature profile.

    This function loads the audio file at ``audio_path`` and computes a
    variety of features:

    * RMS (energy) mean and standard deviation
    * Spectral centroid mean and standard deviation (brightness)
    * Zero crossing rate mean (spectral roughness)
    * Pitch statistics (mean, median, min, max, standard deviation)
    * Voiced ratio (fraction of frames with a detected pitch)
    * Timeline curves for RMS and spectral centroid (downsampled for
      efficiency)

    Parameters
    ----------
    audio_path : Path
        Path to the audio file to analyze.

    Returns
    -------
    profile : dict
        Dictionary with keys ``file``, ``sample_rate``, ``duration_sec``,
        ``global_features``, and ``timeline_features``.
    """
    # Load audio in mono with native sample rate
    y, sr = librosa.load(audio_path.as_posix(), sr=None, mono=True)
    if y.size == 0:
        raise ValueError(f"Audio file is empty: {audio_path}")

    duration_sec = float(len(y) / sr)

    # Use a moderate hop length for feature extraction
    hop_length = 1024

    # RMS energy
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))

    # Spectral centroid (brightness)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    centroid_mean = float(np.mean(spectral_centroid))
    centroid_std = float(np.std(spectral_centroid))

    # Zero crossing rate (roughness)
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
    zcr_mean = float(np.mean(zcr))

    # Pitch tracking using librosa.yin (faster than pYIN)
    f0 = librosa.yin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C6"), sr=sr, hop_length=hop_length)
    pitch_stats = compute_pitch_stats(f0)
    voiced_ratio = float(np.mean(np.isfinite(f0) & (f0 > 0)))

    # Downsample timeline curves to at most 1000 points for storage
    def downsample_curve(curve: np.ndarray, max_points: int = 1000) -> List[float]:
        if len(curve) <= max_points:
            return curve.tolist()
        factor = int(np.ceil(len(curve) / max_points))
        return curve[::factor].tolist()

    timeline_features = {
        "rms_curve": downsample_curve(rms),
        "spectral_centroid_curve": downsample_curve(spectral_centroid),
        # Convert pitch curve to list, replacing NaNs with 0 for JSON serialisation
        "pitch_curve": downsample_curve(np.nan_to_num(f0, nan=0.0)),
    }

    profile = {
        "file": audio_path.name,
        "sample_rate": sr,
        "duration_sec": round(duration_sec, 3),
        "global_features": {
            "rms_mean": round(rms_mean, 6),
            "rms_std": round(rms_std, 6),
            "spectral_centroid_mean": round(centroid_mean, 3),
            "spectral_centroid_std": round(centroid_std, 3),
            "zero_crossing_rate_mean": round(zcr_mean, 6),
            "voiced_ratio": round(voiced_ratio, 6),
            **{k: round(v, 3) for k, v in pitch_stats.items()},
        },
        "timeline_features": timeline_features,
    }

    return profile


def save_profile(profile: Dict[str, object], profile_name: str, presets_dir: Path) -> Path:
    """Save an analysis profile to a JSON file.

    Parameters
    ----------
    profile : dict
        The profile to save.
    profile_name : str
        The base filename (without extension) to use for saving.
    presets_dir : Path
        Directory to place the JSON file.  Will be created if missing.

    Returns
    -------
    output_path : Path
        The path to the written JSON file.
    """
    presets_dir.mkdir(parents=True, exist_ok=True)
    output_path = presets_dir / f"{profile_name}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return output_path


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Analyze a vocal stem and save a profile to presets/.")
    parser.add_argument("audio_file", type=str, help="Path to the vocal stem audio file")
    parser.add_argument("profile_name", type=str, nargs="?", default=None, help="Name of the profile (defaults to stem filename without extension)")
    parser.add_argument("--presets-dir", type=str, default=str(Path(__file__).resolve().parent.parent / "presets"), help="Directory to save analysis profiles")
    args = parser.parse_args(argv)

    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    profile_name = args.profile_name or audio_path.stem
    profile = analyze_audio(audio_path)
    output_path = save_profile(profile, profile_name, Path(args.presets_dir))
    print(f"Saved analysis profile to {output_path}")


if __name__ == "__main__":
    main()