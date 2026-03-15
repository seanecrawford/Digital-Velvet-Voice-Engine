import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYZER = PROJECT_ROOT / "analysis" / "fingerprint_prototype.py"
MUSIC_ROOT = Path(r"E:\Music_Production\Music")

def is_lead_vocal(file_path: Path) -> bool:
    name = file_path.name.lower()
    return "(vocals)" in name and "(backing vocals)" not in name

def profile_name_from_file(file_path: Path) -> str:
    return file_path.parent.name.lower().replace(" ", "_")

def main():
    if not MUSIC_ROOT.exists():
        print(f"Music root not found: {MUSIC_ROOT}")
        sys.exit(1)

    audio_files = []
    for ext in ("*.wav","*.flac","*.mp3","*.m4a"):
        audio_files.extend(MUSIC_ROOT.rglob(ext))

    lead_vocals = [f for f in audio_files if is_lead_vocal(f)]

    print(f"Found {len(lead_vocals)} vocal stems")

    for stem in lead_vocals:
        profile_name = profile_name_from_file(stem)

        cmd = [
            sys.executable,
            str(ANALYZER),
            str(stem),
            profile_name
        ]

        subprocess.run(cmd)

    print("Catalog scan complete")

if __name__ == "__main__":
    main()
