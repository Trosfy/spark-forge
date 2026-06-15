# DGX Spark runtime notes (unified memory + ComfyUI)

The Spark shares one ~119 GB pool across CPU, GPU, containers, and page cache.
Generation is reliable when there is real headroom; `env_check.sh` checks for it.

- **Free-memory headroom.** Below ~40 GB free, FLUX.2 partial-offloads and slows
  sharply. Page cache masks true free memory — drop it before big loads:
  `sysctl -w vm.drop_caches=3`. Stop other GPU services if needed.
- **Stale CUDA context.** A long-lived ComfyUI container can wedge new GPU work
  (`cudaErrorDevicesUnavailable`, or it refuses small allocations with GBs free).
  Fix: `docker restart <container>` — this does not touch cached weights or
  separate download processes.
- **NVFP4 single-load.** With the patched loader, FLUX.2 NVFP4 loads once
  (~50 GB for a generation). The first (cold) image pays the weight-load cost;
  subsequent images are much faster while weights stay resident.
