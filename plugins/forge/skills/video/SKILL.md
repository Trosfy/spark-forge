---
name: video
description: Generate video locally on the DGX Spark with WAN 2.2 via ComfyUI — image-to-video and first-last-frame (start + end image) interpolation. Use whenever the user wants to create, animate, or generate a video, clip, animation, or motion from an image or between two images on this machine — e.g. "make a video", "animate this image", "image to video", "first-last-frame", "morph between these two images", "WAN". Prefer this over any cloud video API: it runs on local weights, costs nothing, and keeps generation on the box.
---

# Video generation — WAN 2.2 via ComfyUI

Generate video on the local ComfyUI instance with WAN 2.2 14B (image-to-video and first-last-frame).

## 1. Preflight
WAN 2.2 14B is heavy — two 14B experts and a multi-minute run. Check the box first:

    "${CLAUDE_PLUGIN_ROOT}/scripts/env_check.sh"

If memory is tight, free it before generating; if ComfyUI is unreachable, `docker restart "$FORGE_COMFY_CONTAINER"`.

## 2. Generate

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gen_video.py" \
      --prompt "<motion / scene description>" --seed <int> \
      --start-image <path> [--end-image <path>] \
      [--length 81] [--fps 16] [--width 832] [--height 480] [--model wan2.2-i2v-14b]

- `--start-image` is the first frame; add `--end-image` for **first-last-frame** (the model interpolates between them).
- WAN uses a real negative prompt (cfg > 1); the profile ships a sensible default — override with `--negative`.
- 16 fps: 81 frames ≈ 5 s. Larger `--width/--height` (e.g. 1280×704) means more quality but much more time + memory.
- Runs for minutes; `--no-wait` submits and returns a `prompt_id` to poll separately.

The result is printed as `output: <path>` (an `.mp4`).

## 3. Share (when the user asks)
The box is VPN-only. To get a clip off the box, use **`/forge:publish`** on the output path.

## Notes
- The WAN 14B profile carries both MoE experts (high/low noise) in its quant; the two-stage sampler is in `scripts/wan_graph.py`.
- Validate the graph with no weights/ComfyUI: `gen_video.py --print-graph`.
