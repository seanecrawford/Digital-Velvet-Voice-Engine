# Digital Velvet Voice Engine

The **Digital Velvet Voice Engine** is an internal tool for matching live vocal
performances to the sound and polish of your released tracks.  It is **not**
intended to clone other singers but to preserve the artist’s own identity
while applying the tonal balance, pitch behaviour and production sheen of a
reference song.  The engine analyses vocal stems, extracts song‑specific
features and generates preset files that control a real‑time audio plugin.

## Quick start

1. Drop your music library (containing individual song folders with vocal
   stems labelled `(Vocals)` and backing stems labelled `(Backing Vocals)`) into
   a directory, for example `E:\Music_Production\Music`.
2. Run `catalog_scanner.py` from the `analysis` folder to generate analysis
   profiles in `presets/`:

   ```bash
   python analysis/catalog_scanner.py --music-root "E:\\Music_Production\\Music"
   ```

3. Convert analysis profiles into engine presets:

   ```bash
   python analysis/profile_to_preset.py
   ```

4. (Optional) Create manual presets in `engine_presets/manual` for songs
   that don’t have stems yet.
5. Load the presets into your audio plugin (to be implemented in `plugin/`)
   and adjust the macro knobs (*brightness*, *warmth*, *pitch tightness*, etc.)
   during your performance.

## Repository structure

```
digital-velvet-voice-engine/
│
├── analysis/            # Python scripts for analysing stems and managing profiles
│   ├── full_stem_analyzer.py      # Extracts global and timeline features from a vocal stem
│   ├── catalog_scanner.py         # Recursively scans a music library and builds analysis profiles
│   ├── profile_to_preset.py       # Converts analysis profiles into engine presets
│   └── match_resolver.py          # Returns the appropriate preset for a given song
│
├── presets/             # Raw analysis profiles (JSON)
│
├── engine_presets/      # Engine presets consumed by the plugin
│   └── manual/          # Hand‑crafted presets for songs without stems
│
├── plugin/              # Future location for JUCE-based audio plugin implementation
│
└── Docs/                # Design documents and roadmap
    ├── architecture.md
    └── roadmap.md
```

See `Docs/architecture.md` for a more detailed description of the system and
`Docs/roadmap.md` for a high‑level development plan.