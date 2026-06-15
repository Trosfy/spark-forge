---
name: publish
description: Publish/export a local file or result off this headless box to the forge S3 + CloudFront store and return a shareable download URL. Use whenever the user wants to get a file out of the box — "publish this", "share this file", "upload to the CDN", "get this off the box", "give me a link for this", "export this result", "send this somewhere I can download it". Returns a signed (gated) or direct URL.
---

# Publish — get a file off the headless box

Upload a local artifact to the forge S3 store (fronted by CloudFront) and return a
download URL. This is how results leave the VPN-only box.

## Prerequisites
- The download infra exists — run `/forge:setup-cdn` once — and the forge config has
  `FORGE_S3_BUCKET` (plus `FORGE_CDN_*` for CDN / signed URLs).
- Active AWS credentials (authenticate however you normally do; verify with
  `aws sts get-caller-identity`).

## Publish

    "${CLAUDE_PLUGIN_ROOT}/scripts/publish_s3.sh" <file-or-dir> --url

Prints `uploaded: s3://…` and, with `--url`, a shareable link. The URL kind is chosen
automatically by what's configured:
- **signed CloudFront** (time-limited, gated) when `FORGE_CDN_DOMAIN` + key are set,
- else **plain CloudFront**, else **public S3** (`--public`), else an **S3 presigned** URL.

## Notes
- Signed URLs expire after `FORGE_CDN_TTL` (default 1h); set up signing with
  `/forge:setup-cdn --signed`.
- Typical flow: `/forge:image` or `/forge:model` → `/forge:publish` the result.
- Directories upload recursively; `--url` is for single files.
