"""
Utility for selecting the most appropriate profile for the Digital Velvet Voice
Engine.  A "profile" is a JSON document describing the characteristics of a
song or style derived from analysis of a vocal stem.  When the engine is
invoked for live processing it consults this resolver to decide which profile
to load.

Profiles live in the ``presets`` directory.  There are three tiers of
profiles:

* **Song profiles** – one JSON file per analysed track.  These are named
  after the song, for example ``sweet_dreams.json``.
* **Style profiles** – aggregated characteristics of a genre or style.  These
  files are prefixed with ``style_``, for example ``style_pop.json``.
* **Default profile** – a fallback when neither a song nor style match is
  available.  This file is called ``digital_velvet_default.json``.

The resolver checks for a song profile first.  If none exists it falls back
to a style profile.  Finally, it returns the default profile.  The caller can
explicitly specify a style to override the default fallback behaviour.

This module is intentionally minimal; it abstracts the profile lookup logic
away from the main processing pipeline and makes it easy to evolve the
matching strategy without modifying client code.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


# Directory containing analysis results.  The folder is located two levels
# above this file: ``digital-velvet-voice-engine/presets``.
PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"


def _load_profile(name: str) -> Optional[Dict[str, Any]]:
    """Load a profile by filename without the ``.json`` extension.

    Parameters
    ----------
    name:
        Name of the profile file without the ``.json`` suffix.

    Returns
    -------
    dict or None
        The parsed JSON profile or ``None`` if the file does not exist.
    """
    path = PRESETS_DIR / f"{name}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_profile(song_name: Optional[str] = None, *, style: Optional[str] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Resolve a song or style profile, falling back to the default profile.

    The resolver attempts to load a specific song profile if ``song_name`` is
    provided.  If that fails, it attempts to load a style profile prefixed
    with ``style_`` using the provided ``style`` parameter.  If both lookups
    fail, it loads the global default profile.  A tuple of the profile
    ``level`` (``"song"``, ``"style"`` or ``"default"``) and the profile
    dictionary (or ``None`` if even the default is missing) is returned.

    Parameters
    ----------
    song_name:
        The canonical name of the song whose profile should be loaded.  The
        filename must exist under the ``presets`` directory without a
        ``.json`` suffix.  This argument is case-sensitive.

    style:
        Optional style name to use as a secondary lookup.  Style profiles are
        expected to be named with a ``style_`` prefix, such as
        ``style_pop.json`` or ``style_reggae.json``.

    Returns
    -------
    (str, dict or None)
        A tuple of the level used (``"song"``, ``"style"`` or ``"default"``)
        and the parsed profile dictionary.  The profile may be ``None`` only
        if no default profile exists.  Callers should handle this case
        gracefully.
    """
    # Try to load a song-specific profile first
    if song_name:
        song_profile = _load_profile(song_name)
        if song_profile is not None:
            return "song", song_profile

    # If no song profile was loaded and a style was specified, attempt to
    # retrieve the style profile.  Style files are prefixed with ``style_``.
    if style:
        style_key = f"style_{style}"
        style_profile = _load_profile(style_key)
        if style_profile is not None:
            return "style", style_profile

    # Finally fall back to the default profile
    default_profile = _load_profile("digital_velvet_default")
    return "default", default_profile


if __name__ == "__main__":
    # Rudimentary CLI for manual testing
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a Digital Velvet Voice Engine profile.")
    parser.add_argument("--song", help="Song name for which to load a profile", default=None)
    parser.add_argument("--style", help="Style name to use if the song profile is not found", default=None)
    args = parser.parse_args()

    level, profile = resolve_profile(song_name=args.song, style=args.style)
    print(f"Resolved profile level: {level}")
    if profile is not None:
        print(json.dumps(profile, indent=2))
    else:
        print("No profile found.")