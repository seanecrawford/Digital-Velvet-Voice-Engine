"""
catalog_scanner.py
------------------

This script scans a music library for lead vocal stems and generates
analysis profiles for each song.  The library is expected to have a
structure where each song is contained in its own folder and the vocal
stem filenames include the substring ``(Vocals)``.  Files containing
``(Backing Vocals)`` are ignored.

Example usage::

    python analysis/catalog_scanner.py --music-root "E:\\Music_Production\\Music"

This will walk through all subfolders under ``E:\\Music_Production\\Music``,
find audio files matching the pattern, and call the analyzer on each.  The
resulting profiles will be saved to the ``presets/`` directory in the
repository.

The script avoids re‑creating profiles for songs that already have a
profile file in ``presets/``.  To force re‑analysis, remove the
corresponding JSON file in ``presets`` before running the scanner.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Generator, Iterable, Tuple

from .full_stem_analyzer import analyze_audio, save_profile


def iter_lead_vocal_stems(music_root: Path, extensions: Tuple[str, ...] = (".wav", ".flac", ".mp3", ".m4a")) -> Generator[Tuple[Path, str], None, None]:
    """Yield paths to lead vocal stems under ``music_root``.

    A lead vocal stem is defined as a file whose name contains the substring
    ``(Vocals)`` but does not contain ``(Backing Vocals)``.  The song
    identifier is derived from the parent directory name and normalised by
    replacing spaces with underscores and converting to lowercase.

    Parameters
    ----------
    music_root : Path
        Root directory to search.
    extensions : tuple of str, optional
        Audio file extensions to include.

    Yields
    ------
    (stem_path, song_key)
        The path to the vocal stem and the derived song key.
    """
    for file_path in music_root.rglob("*"):
        if file_path.suffix.lower() in extensions:
            name_lower = file_path.name.lower()
            if "(vocals)" in name_lower and "(backing vocals)" not in name_lower:
                # Use the parent directory as the song identifier
                song_key = file_path.parent.name.replace(" ", "_").lower()
                yield file_path, song_key


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Scan a music library and generate analysis profiles for lead vocal stems.")
    parser.add_argument("--music-root", type=str, required=True, help="Root directory of the music library to scan")
    parser.add_argument("--presets-dir", type=str, default=str(Path(__file__).resolve().parent.parent / "presets"), help="Directory to store analysis profiles")
    args = parser.parse_args(list(argv) if argv is not None else None)

    music_root = Path(args.music_root)
    if not music_root.exists() or not music_root.is_dir():
        print(f"Music root does not exist or is not a directory: {music_root}", file=sys.stderr)
        sys.exit(1)

    presets_dir = Path(args.presets_dir)
    generated = 0
    scanned = 0
    for stem_path, song_key in iter_lead_vocal_stems(music_root):
        scanned += 1
        output_file = presets_dir / f"{song_key}.json"
        if output_file.exists():
            print(f"[skip] Profile exists for {song_key}")
            continue
        print(f"[analyse] {stem_path} -> {song_key}")
        try:
            profile = analyze_audio(stem_path)
        except Exception as e:
            print(f"[error] Failed to analyse {stem_path}: {e}", file=sys.stderr)
            continue
        save_profile(profile, song_key, presets_dir)
        generated += 1
        print(f"[done] Saved profile for {song_key}")

    print(f"Scanned {scanned} vocal stems, generated {generated} new profiles.")


if __name__ == "__main__":
    main()