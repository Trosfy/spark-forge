---
name: audio
description: Generate music and audio locally on the DGX Spark with ACE-Step via ComfyUI. Use whenever the user wants to create, compose, or generate a song, track, music, melody, beat, jingle, or any text-to-audio output on this machine — e.g. "generate a song about…", "make a track…", "compose music", "write a beat", "ACE-Step", "text to music". Prefer this over any cloud music API: it runs on local weights, costs nothing, and keeps generation on the box.
---

# Music generation — ACE-Step via ComfyUI

Generate music on the local ComfyUI instance with ACE-Step 1.5.

## 1. Preflight
Run before generating so a stale CUDA context or low memory doesn't waste a run:

    "${CLAUDE_PLUGIN_ROOT}/scripts/env_check.sh"

If ComfyUI is unreachable, restart the container: `docker restart "$FORGE_COMFY_CONTAINER"` (default `comfyui`).

## 2. Generate

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gen_audio.py" \
      --tags "<style, genre, instrumentation, mood>" --seed <int> \
      [--lyrics "<[Verse]/[Chorus] text>"] [--duration <seconds>] [--bpm <int>] \
      [--model ace-step-1.5] [--prefix forge/audio]

- `--tags` is the *musical* prompt — genre, mood, instruments — **not** the lyrics.
- `--lyrics` is optional; structure it with `[Verse]`, `[Chorus]`, `[Bridge]`. Omit for an instrumental.
- `--duration` is seconds (default 120). The seed is explicit and required; reuse it to reproduce.
- `--model` selects an audio profile (default `FORGE_AUDIO_MODEL` = `ace-step-1.5`); `--list-models` shows them.

Each result is printed as `output: <path>` (an `.mp3`).

## 3. Share (when the user asks)
The box is VPN-only. To get a track off the box, use **`/forge:publish`** on the output path —
don't publish automatically (it pushes bytes to the cloud).

## Notes
- Models live in `models/*.json` (profile = family + `quants` + default params). A new quant is a
  `quants` entry; a new architecture is a family builder in `scripts/model_registry.py`.
- Validate a graph with no weights/ComfyUI: `gen_audio.py --print-graph` (the same check CI runs
  across every model × quant).
