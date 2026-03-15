import json
from pathlib import Path

def build_placeholder_profile(song_name: str) -> dict:
    return {
        "song": song_name,
        "brightness": 0.0,
        "formant_shift": 0.0,
        "pitch_tightness": 0.0,
        "vibrato_rate": 0.0,
        "vibrato_depth": 0.0,
        "compression_density": 0.0
    }

def save_profile(song_name: str, output_dir: str = "../presets") -> Path:
    profile = build_placeholder_profile(song_name)
    output_path = Path(__file__).resolve().parent / output_dir / f"{song_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    return output_path

if __name__ == "__main__":
    path = save_profile("example_song")
    print(f"Saved profile to: {path}")
