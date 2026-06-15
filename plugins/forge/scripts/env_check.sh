#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"
forge_load_config

rc=0

code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$FORGE_COMFY_URL/" || true)"
if [ "$code" = "200" ]; then
  echo "ok    ComfyUI reachable at $FORGE_COMFY_URL"
else
  echo "FAIL  ComfyUI not reachable at $FORGE_COMFY_URL (http=$code)"
  rc=1
fi

if status="$(docker inspect -f '{{.State.Health.Status}}' "$FORGE_COMFY_CONTAINER" 2>/dev/null)"; then
  echo "ok    container '$FORGE_COMFY_CONTAINER' health=$status"
else
  echo "warn  container '$FORGE_COMFY_CONTAINER' not found (only needed for image-to-3D)"
fi

avail_gb=$(($(awk '/MemAvailable/{print $2}' /proc/meminfo) / 1024 / 1024))
echo "info  MemAvailable ${avail_gb}GB"
if [ "$avail_gb" -lt 40 ]; then
  echo "warn  < 40GB free: FLUX.2 may partial-offload and slow down."
  echo "      try: sysctl -w vm.drop_caches=3   (and stop other GPU services)"
fi

echo
echo "stale CUDA context (cudaErrorDevicesUnavailable)? restart it:"
echo "  docker restart $FORGE_COMFY_CONTAINER"
exit "$rc"
