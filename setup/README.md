# Spark setup (generation-stack delta)

This covers only what's specific to the generation stack. For base DGX Spark setup
(OS, drivers, Docker, CUDA), follow NVIDIA's official
[DGX Spark Playbooks](https://github.com/NVIDIA/dgx-spark-playbooks).

## 1. ComfyUI + FLUX.2

Run ComfyUI with the FLUX.2 nodes in a container (e.g. a SparkyUI image), with the
host `input/` and `output/` dirs bind-mounted. Download the weights listed in
[`models.manifest`](models.manifest) into ComfyUI's `diffusion_models/`,
`text_encoders/`, and `vae/` dirs.

Verify with `plugins/forge/scripts/env_check.sh` — it should report ComfyUI reachable.

## 2. Hunyuan3D-2.1 (for `forge:model`)

The shape pipeline runs inside the ComfyUI container. Provision it once:

```
docker exec -it <container> bash
mkdir -p /root/work && cd /root/work
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git
pip install diffusers trimesh pymeshlab pygltflib accelerate rembg onnxruntime omegaconf scikit-image
```

The ~7 GB shape weights (`tencent/Hunyuan3D-2.1`) download automatically on the first
generation, into `/root/.cache/hy3dgen`. The defaults for `FORGE_HUNYUAN_REPO` and
`FORGE_HY3D_CACHE` already match the paths above.

> **Durability.** `/root/work` and `/root/.cache/hy3dgen` live in the container's
> writable layer — they survive `restart` but a `docker rm`/recreate wipes them. To
> make image-to-3D survive container recreation, bind-mount a host dir for the repo +
> weight cache (and re-point the two config vars), or bake the steps above into the
> image. `gen_model.py` vendors its own copy of the inference script, so only the repo
> and weights need to persist.

## 3. forge config (optional)

With ComfyUI in a container, host input/output dirs are auto-detected from its mounts
and defaults cover the rest — no config is needed to start. Add config only to
override a default or to set S3:

```
sudo install -d /etc/forge && sudo cp ../config.example /etc/forge/config
$EDITOR /etc/forge/config
```

`/etc/forge/config` is system-wide; `~/.config/forge/config` works for a single user.
See the search order documented in `config.example`.

## 4. S3 (optional)

For publishing results, see the repo README → "Outputs → S3". `infra/` has Terraform
and a `bootstrap_s3.sh` fallback.
