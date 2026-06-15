---
name: hunyuan
description: Provision Hunyuan3D-2.1 (image-to-3D) inside the ComfyUI container so /forge:model works — clones the repo and installs the Python deps; the ~7GB shape weights auto-download on first use. Use when the user wants to set up, install, or enable image-to-3D / Hunyuan3D / the 3D model generator, or needs to re-provision after rebuilding the ComfyUI container.
---

# setup:hunyuan — provision Hunyuan3D-2.1 (image-to-3D)

`/forge:model` runs Hunyuan3D-2.1 inside the ComfyUI container. This installs it there
(clone + Python deps). The ~7 GB shape weights download from Hugging Face on the first
`/forge:model` run.

## Run

    "${CLAUDE_PLUGIN_ROOT}/scripts/setup_hunyuan.sh"

Idempotent — skips the clone if already present, and safe to re-run after a container
rebuild.

## Config (env or forge config)
- `FORGE_COMFY_CONTAINER` (default `comfyui`) — the container to install into.
- `FORGE_HUNYUAN_REPO` (default `/root/work/Hunyuan3D-2.1`) and `FORGE_HY3D_CACHE`
  (default `/root/.cache/hy3dgen`).

## Notes
- Requires the ComfyUI container running + internet access (clone + weight download).
- **Durability:** the repo and weight cache live in the container's writable layer, so a
  `docker rm`/recreate wipes them — just re-run this. To persist, bind-mount those paths.
- FLUX.2 image weights are separate — those come with your ComfyUI install (see
  `setup/models.manifest`), not this skill.
