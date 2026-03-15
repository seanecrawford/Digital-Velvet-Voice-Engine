# Architecture

## Product Concept
A reference-aware live vocal engine for internal Digital Velvet use.

## Core Workflow
1. Import a reference stem from a released or guide vocal
2. Analyze tonal, pitch, timing, and formant characteristics
3. Build a target vocal fingerprint
4. Apply live DSP to incoming mic audio to move toward that target
5. Save song-specific profiles

## MVP
- Offline reference analysis
- Profile export
- Live DSP chain with:
  - pitch correction
  - formant shaping
  - EQ match
  - compression
  - saturation
  - ambience macros

## Non-Goals
- Voice cloning
- Artist impersonation
- External marketplace release
