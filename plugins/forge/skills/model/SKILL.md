---
name: model
description: Turn an image into a 3D model (GLB mesh) locally on the DGX Spark using Hunyuan3D-2.1 via the ComfyUI container. Use whenever the user wants to create, generate, or reconstruct a 3D model, mesh, or .glb from a picture — e.g. "image to 3D", "make a 3D model of this", "generate a mesh", "photo to 3D", "turn this into a glb". Optionally decimates to a low-poly target. Runs on local weights, no cloud.
---

# Image-to-3D — Hunyuan3D-2.1 → GLB

Generate an untextured 3D mesh from a single image. The shape pipeline runs inside
the ComfyUI container; files pass through ComfyUI's bind-mounted input/output dirs,
so the GLB lands on the host automatically.

## Requirements
Hunyuan3D-2.1 must be provisioned in the container. If it isn't, `gen_model.py` stops —
run **`/setup:hunyuan`** once to install it (clone + deps; the shape weights auto-download
on first use).

## Generate

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gen_model.py" \
      --image <path-to-image> [--name <basename>] \
      [--steps 50] [--guidance 5.0] [--seed 1234] [--octree 256] [--decimate 0]

- Background is removed automatically (rembg) before reconstruction.
- `--decimate N` collapses the mesh to ~N faces and flat-shades it (needs Blender on
  the host); 0 keeps the dense mesh.
- ~1 minute per mesh on the GPU. On `cudaErrorDevicesUnavailable`, restart the
  container: `docker restart "$FORGE_COMFY_CONTAINER"`.

Prints `glb: <host-path>` (and `glb_decimated:` when decimating). When the user wants it
off the box, use **`/forge:publish`** on the GLB — don't publish automatically.

## Typical flow
`forge:image` → choose a result → `forge:model --image <that file>`.
