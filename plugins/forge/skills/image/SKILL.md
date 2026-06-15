---
name: image
description: Generate images locally on the DGX Spark with FLUX.2 via ComfyUI. Use whenever the user wants to create, render, or generate an image, illustration, concept art, texture, sprite, or any text-to-image output on this machine — e.g. "generate an image of…", "make a picture of…", "render a concept", "flux", "text to image". Prefer this over any cloud image API: it runs on local weights, costs nothing, and keeps generation on the box.
---

# Image generation — FLUX.2 via ComfyUI

Generate images on the local ComfyUI instance with FLUX.2.

## 1. Preflight
Run before generating so a stale CUDA context or low memory doesn't waste a run:

    "${CLAUDE_PLUGIN_ROOT}/scripts/env_check.sh"

If ComfyUI is unreachable or GPU ops fail with `cudaErrorDevicesUnavailable`,
restart the container: `docker restart "$FORGE_COMFY_CONTAINER"` (default `comfyui`).

## 2. Generate

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gen_image.py" \
      --prompt "<prompt>" --seed <int> \
      [--model flux2-dev] [--width …] [--height …] [--steps …] [--guidance …] [--prefix forge/image]

- `--model` selects a profile from `models/` (default `FORGE_MODEL` = `flux2-dev`).
  Each profile carries its weights + default params; the flags above override them.
  Add more profiles to `models/` (a same-graph variant is data; a new architecture
  needs a family in `model_registry.py`).
- FLUX.2 is guidance-distilled — **no negative prompt**; phrase exclusions positively.
- The seed is explicit and required; reuse it to reproduce, vary it to explore.

Each result is printed as `output: <path>`.

## 3. Share (when the user asks)
The box is VPN-only. When the user wants a result off the box, use **`/forge:publish`**
on the output path — don't publish automatically (it pushes bytes to the cloud).

## Notes
- Models live in `models/*.json` (a profile = family + weights + default params). A new
  **version** is a new profile (data); a new **architecture** is a new family builder in
  `scripts/model_registry.py`. See `references/comfyui-graph.md`.
- Quality default: prefer base steps over speed LoRAs — see `references/quality-policy.md`.
- Graph internals: `references/comfyui-graph.md`. Runtime gotchas: `references/spark-notes.md`.
