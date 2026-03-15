# Digital Velvet Voice Engine Architecture

This document provides an overview of the architecture for the **Digital
Velvet Voice Engine**, an internal tool designed to help live performances and
recordings match the sonic identity of their studio-produced releases.  The
system is composed of several layers that interact to analyse vocal stems,
generate profiles, convert profiles into processing presets and apply those
presets in real time via a plugin.

## High‑Level Components

1. **Stem analysis** – A suite of Python scripts that take a raw vocal
   stem as input and extract quantitative descriptors.  These metrics
   characterise attributes such as loudness, brightness (spectral centroid),
   pitch distribution and dynamic range.  See
   [`analysis/full_stem_analyzer.py`](../analysis/full_stem_analyzer.py).

2. **Profile generation** – Scripts that convert the raw analysis into
   song, style or global profiles.  Song profiles capture individual track
   characteristics; style profiles aggregate songs of the same genre or vibe;
   a global default profile provides a fallback.  See
   [`analysis/profile_to_preset.py`](../analysis/profile_to_preset.py) for an
   example mapping.

3. **Profile resolution** – A lightweight module that selects the most
   appropriate profile for a given context.  It falls back from song to
   style to default if necessary.  See
   [`analysis/match_resolver.py`](../analysis/match_resolver.py).

4. **Preset conversion** – Once a profile is resolved, its metrics are
   converted into a set of high‑level parameters (e.g. brightness, pitch
   tightness, formant shift).  These parameters directly control the audio
   processing chain that shapes the live vocal.  The mapping from analysis
   features to preset values is defined in
   [`analysis/profile_to_preset.py`](../analysis/profile_to_preset.py).

5. **Processing plugin** – A real‑time audio processor (to be implemented
   using JUCE or a similar framework) that applies the preset to incoming
   microphone audio.  It performs pitch correction, formant shaping, EQ
   matching, compression and ambience generation to achieve the target
   character.

## Data Flow

The typical workflow is as follows:

```
Vocal stem → analysis → song profile → preset conversion → live processing
```

1. A dry or near‑dry vocal stem is analysed via `full_stem_analyzer.py`.
2. The analysis script stores a JSON file in the `presets/` directory with
   measured features for that song.
3. `profile_to_preset.py` maps the measured features into a more abstract
   preset.  These presets live in the `engine_presets/` directory.
4. At runtime the plugin calls the resolver to find the correct preset given
   a song name or style.
5. The preset parameters drive DSP modules inside the plugin (pitch
   correction, formant shifting, EQ matching, compression, saturation and
   ambience) to produce a processed live vocal that matches the production
   aesthetic of the reference track.

## Evolution and Extensibility

* **Analysis improvements** – Future versions of the analyser may extract
  additional features such as phoneme timing, transient density or
  per‑section statistics.  The architecture isolates this logic in
  `analysis/full_stem_analyzer.py`, making upgrades easy.

* **Style and group profiles** – Today the resolver supports song, style and
  global profiles.  Additional aggregation schemes (e.g. per‑album or
  mood‑based profiles) can be implemented by extending the profile
  generation scripts.

* **Plugin implementation** – Although not yet implemented in this
  repository, the real‑time processing component should adhere to the
  profile schema and expose macro controls that correspond to the preset
  parameters.  The DSP can be refined over time without changing the
  analysis logic.

This layered design allows individual pieces to evolve independently while
maintaining a clear flow from analysis to live processing.