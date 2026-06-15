# spark-forge

Local generative-AI skills for the **NVIDIA DGX Spark** (GB10 / Blackwell), packaged
as a Claude Code plugin. Generate **images** with FLUX.2 and **3D models** with
Hunyuan3D — on local weights, through a local ComfyUI — and publish results to S3.

[![ci](https://github.com/Trosfy/spark-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/Trosfy/spark-forge/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This repo is both a **Claude Code plugin marketplace** (the `forge` plugin) and the
**Spark setup** to stand the stack up. The code is MIT; the models are not — see
[THIRD_PARTY.md](THIRD_PARTY.md) (several are non-commercial).

## What's inside

| Path | What |
|---|---|
| `plugins/forge/` | The `forge` plugin: skills `forge:image` and `forge:model`, plus the scripts they run |
| `infra/` | Terraform (and a no-Terraform fallback) for a private S3 artifact bucket |
| `setup/` | Spark provisioning — model manifest + Hunyuan3D setup (the delta on top of NVIDIA's base) |
| `config.example` | Copy to `~/.config/forge/config` |

## Skills

**`forge`** — use the stack:
- **`/forge:image`** — text-to-image with FLUX.2 via ComfyUI.
- **`/forge:model`** — image-to-3D (GLB) with Hunyuan3D-2.1; optional decimation to low-poly.
- **`/forge:publish`** — push a local file/result off the headless box to S3+CloudFront and return a shareable (signed) download URL.

**`setup`** — provision the stack:
- **`/setup:cdn`** — provision the S3 + CloudFront download infra (Terraform) and wire the config; plans first, applies on confirmation.
- **`/setup:hunyuan`** — install Hunyuan3D-2.1 (image-to-3D) into the ComfyUI container for `/forge:model`.

## Prerequisites

- A DGX Spark (or any box) running **ComfyUI with the FLUX.2 nodes** in a container,
  with `input/` and `output/` bind-mounted to the host.
- **Docker**, **Claude Code**, and the **AWS CLI** (for publishing). Optional:
  **Terraform** (bucket IaC) and **Blender** (mesh decimation).
- Models downloaded per [`setup/models.manifest`](setup/models.manifest).

Base OS/driver/container provisioning builds on NVIDIA's official
[DGX Spark Playbooks](https://github.com/NVIDIA/dgx-spark-playbooks); this repo
documents only the generation-stack delta in [`setup/`](setup/README.md).

## Install (Claude Code plugins)

```
/plugin marketplace add Trosfy/spark-forge
/plugin install forge@spark-forge    # use:       image / model / publish
/plugin install setup@spark-forge    # provision: cdn (optional)
```

Add via Git (as above), not a raw file URL — the marketplace serves the plugin by
relative path, which only resolves over Git.

## Configure (optional)

With ComfyUI in a container, the host input/output dirs are auto-detected from its
mounts and the defaults cover the rest — you can start with **no config**. Add config
only to override a default or to set S3:

```
sudo install -d /etc/forge && sudo cp config.example /etc/forge/config        # system-wide
# or: mkdir -p ~/.config/forge && cp config.example ~/.config/forge/config    # per-user
```

Search order: `$FORGE_CONFIG` > `~/.config/forge/config` > `/etc/forge/config`;
per key, environment > file > built-in default. See `config.example` for all keys.

## Use

In Claude Code:

```
/forge:image      # "generate an image of a brass astrolabe on dark velvet, seed 1234"
/forge:model      # "turn that image into a 3D model"
```

Or call the scripts directly:

```
python3 plugins/forge/scripts/gen_image.py --prompt "a brass astrolabe on dark velvet" --seed 7
python3 plugins/forge/scripts/gen_model.py --image <path>.png --decimate 1500
```

## Outputs → S3 ("acting as cloud")

The Spark is VPN-only, so results are pushed to S3.

```
# one-time: create the bucket (Terraform)
cd infra && cp terraform.tfvars.example terraform.tfvars && $EDITOR terraform.tfvars
terraform init && terraform apply
# ...or without Terraform:
./infra/bootstrap_s3.sh my-bucket us-east-1

# publish a result
plugins/forge/scripts/publish_s3.sh <file> --url
```

Set `FORGE_S3_BUCKET` / `FORGE_S3_REGION` in your config. Credentials come from the
standard AWS credential chain (environment, a named profile, SSO, or an instance role)
— provide them however you normally do.

**Optional CloudFront (stable, headless download URLs).** Presigned URLs expire (≤12h
with temporary/STS credentials). For durable links, enable the optional CDN — the bucket
stays **private** and CloudFront serves it via Origin Access Control:

```
cd infra && terraform apply -var enable_cloudfront=true
# set FORGE_CDN_DOMAIN to the `cloudfront_domain` output; then `publish_s3.sh <file> --url`
# prints https://<domain>/<key> with no expiry. Anyone can run this in their own AWS account.
```

For **gated** downloads, enable signed URLs — bucket and CDN stay private and the
script mints short-lived signed URLs (signed with a CloudFront key, so unlike the S3
presign they aren't tied to your STS session):

```
openssl genrsa -out /etc/forge/cloudfront_private_key.pem 2048
openssl rsa -pubout -in /etc/forge/cloudfront_private_key.pem -out /etc/forge/cloudfront_public_key.pem
cd infra && terraform apply -var enable_cloudfront=true -var cloudfront_signed=true \
  -var cloudfront_public_key_path=/etc/forge/cloudfront_public_key.pem
# then set FORGE_CDN_KEY_PAIR_ID (cloudfront_key_pair_id output) + FORGE_CDN_PRIVATE_KEY in /etc/forge/config
```

**Terraform options.** State is **local** by default; for shared/remote state copy
`infra/backend.tf.example` → `infra/backend.tf` (S3 backend with native lockfile, no
DynamoDB; Terraform ≥ 1.10). Lifecycle is configurable — `expire_days`,
`noncurrent_expire_days`, `abort_multipart_days`. Custom domain: set `domain_name` +
`route53_zone_name` and the ACM cert (us-east-1) + DNS records are created and validated
automatically; or pass `acm_certificate_arn` to reuse an existing cert (e.g. a wildcard).
`public_read` / `--public` stays a simpler alternative for direct S3 URLs.

## Roadmap

Direction, not commitments — `spark-forge` ships FLUX.2 + Hunyuan3D today, and the model
registry and two-plugin layout are built to grow:

- **More image models** — SDXL, Qwen-Image, Z-Image, FLUX.1-Schnell as registry *families*
  (a ComfyUI graph + profiles), added as each is installed and tested.
- **More modalities** — `forge:video` (image-to-video) and `forge:audio` as sibling skills.
- **`setup:models`** — scripted model-weight provisioning, once there's a clean per-platform source.
- **Multi-platform** — model profiles for non-DGX-Spark hosts (e.g. Ryzen AI / ROCm); the ComfyUI
  engine is already platform-agnostic, so this is mostly profiles + setup docs.
- **Hunyuan3D durability** — bind-mount the repo + weights out of the container's writable layer.

## Licenses

Code: [MIT](LICENSE). Models: see [THIRD_PARTY.md](THIRD_PARTY.md) — FLUX.2-dev and
Hunyuan3D-2.1 carry their own terms, **some non-commercial**. Provided **as-is** as a
personal project: no warranty, no support.
