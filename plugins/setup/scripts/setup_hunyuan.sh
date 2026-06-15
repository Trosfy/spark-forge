#!/usr/bin/env bash
# Provision Hunyuan3D-2.1 (image-to-3D) inside the ComfyUI container: clone the repo and
# install the Python deps. The ~7GB shape weights (tencent/Hunyuan3D-2.1) auto-download
# from Hugging Face on the first /forge:model run. Idempotent; re-run after a rebuild.
set -euo pipefail

# config: env > ~/.config/forge/config > /etc/forge/config
for cfg in "${FORGE_CONFIG:-}" "${XDG_CONFIG_HOME:-$HOME/.config}/forge/config" /etc/forge/config; do
  if [ -n "$cfg" ] && [ -f "$cfg" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$cfg"
    set +a
    break
  fi
done

container="${FORGE_COMFY_CONTAINER:-comfyui}"
repo="${FORGE_HUNYUAN_REPO:-/root/work/Hunyuan3D-2.1}"
cache="${FORGE_HY3D_CACHE:-/root/.cache/hy3dgen}"
upstream="https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git"
work="$(dirname "$repo")"

docker exec "$container" true 2>/dev/null || {
  echo "ComfyUI container '$container' not available" >&2
  exit 1
}

if docker exec "$container" test -d "$repo/hy3dshape"; then
  echo "Hunyuan3D already present: $container:$repo"
else
  echo "cloning Hunyuan3D-2.1 -> $container:$repo"
  docker exec "$container" bash -lc "mkdir -p '$work' && git clone --depth=1 '$upstream' '$repo'"
fi

echo "installing python deps in $container ..."
docker exec "$container" pip install -q \
  diffusers trimesh pymeshlab pygltflib accelerate rembg onnxruntime omegaconf scikit-image

echo "Hunyuan3D ready in $container. Shape weights (~7GB) auto-download to $cache on the first /forge:model run."
