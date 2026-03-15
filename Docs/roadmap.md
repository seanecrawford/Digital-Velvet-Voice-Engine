# Roadmap for Digital Velvet Voice Engine

This roadmap outlines the planned development stages for the Digital Velvet
Voice Engine.  It is meant as a living document to guide future work on
analysis tools, profile generation, preset mapping and real‑time
processing.

## Phase 1 – Analysis and Profile Creation

* **Establish repository structure** – Define directories for analysis,
  presets, engine presets, documentation and the plugin skeleton.  *Status:
  complete.*

* **Implement full‑stem analysis** – Develop a script to analyse complete
  vocal stems.  Extract basic features such as RMS energy, spectral
  centroid, zero crossing rate and pitch statistics.  Store results as
  song‑specific JSON files in `presets/`.  *Status: complete.*

* **Build a catalogue scanner** – Automate the detection and analysis of
  vocal stems across a music library.  Identify lead vocal files and
  generate profiles in bulk.  *Status: partial – scanning implemented,
  improvements to analysis underway.*

* **Map analysis to presets** – Create a script to convert raw analysis
  features into high‑level preset parameters (brightness, pitch tightness,
  compression density, etc.).  Generate a per‑song preset and a global
  default preset.  *Status: complete.*

* **Add profile resolver** – Provide a simple mechanism to select a profile
  based on a song or style name, falling back to the default.  *Status:
  complete.*

## Phase 2 – Style Aggregation and Metadata

* **Define song metadata** – Create a JSON document listing each analysed
  song with its associated style and optional sub‑style.  This will drive
  the creation of style profiles.

* **Generate style profiles** – Aggregate song profiles by style and
  produce a style‑level preset.  Allow the resolver to use style presets
  when no song match is found.

* **Design UI for manual preset entry** – Provide an interface to create
  or edit presets manually when stems are not yet analysed.  These manual
  presets should coexist with automatically generated presets.

## Phase 3 – Real‑Time Processing Plugin

* **Develop JUCE plugin prototype** – Start a C++ project using JUCE
  (or another audio framework) that can load a preset and apply its
  parameters to an incoming audio stream.  Basic modules should include
  pitch correction, formant shifting, EQ matching, compression and
  ambience.

* **Integrate resolver and preset loader** – The plugin should query the
  preset resolver at load time (or when the song changes) and apply the
  selected preset.

* **Implement macro controls** – Expose macro knobs or sliders for
  brightness, warmth, tightness and effect depth.  These controls allow
  fine‑tuning during performance while preserving the base preset.

* **Add automation and section‑aware processing** – As the analysis
  improves to include section delineation, implement automation in the
  plugin that adapts processing across song sections (e.g. chorus vs.
  verse).

## Phase 4 – Advanced Features

* **Enhanced analysis** – Incorporate phoneme timing, spectral flux,
  transient density and other advanced features to better capture
  expressive nuances.  Use these to refine the mapping between analysis
  output and preset parameters.

* **Style learning and clustering** – Develop algorithms to automatically
  infer styles or clusters from song profiles rather than relying solely on
  manual tags.

* **Machine learning aided processing** – Explore neural network models for
  timbre transfer or expressive synthesis that maintain the vocalist’s
  identity while adapting to different production aesthetics.

* **Interactive preset editor** – Build a graphical editor that allows
  producers to visualise analysis data, adjust mapping functions and hear
  the results in real time.

This roadmap is subject to change as the project evolves.  Contributions
and suggestions are welcome, and further phases may be added to address
emerging needs.