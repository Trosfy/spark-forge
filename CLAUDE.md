# CLAUDE.md — spark-forge

Claude Code plugins for local generative AI on DGX Spark: `forge` (image/model/publish)
and `setup` (cdn/hunyuan), plus the `forge-cdn` Terraform module. Public: Trosfy/spark-forge.

## Releases
- One **GPG-signed** semver tag per release, matching `plugins/forge/.claude-plugin/plugin.json`
  `version` (bump `setup`'s too when it changes): `git tag -s vX.Y.Z -m "spark-forge vX.Y.Z"`, then push it.
- Publish from the tag: `gh release create vX.Y.Z --title "spark-forge vX.Y.Z" --notes …`.
- Version **code only** — no binary assets (generated artifacts go to S3/CloudFront, never releases).
- Squash-merged PRs accumulate into the next tag. Users pin via the plugin `version` and module `?ref=vX.Y.Z`.

## Workflow (main is protected)
- **No direct pushes to `main`** (enforced for admins too). Every change: branch → PR →
  CI (`lint` + `secrets`) green → **squash-merge** (branch auto-deletes).
- Commits and tags are GPG-signed; no `Co-Authored-By` / "Generated with Claude Code" trailers.

## Conventions
- Two plugins; the `:` namespace is the plugin name. `forge` = use the stack, `setup` = provision it.
- Model registry (`plugins/forge/models/*.json`): **family = graph (code), model = profile (data),
  quant = a `quants` entry** that overrides only the weights that change. New quant → an entry; new
  model → a profile JSON; new architecture → a family in `scripts/model_registry.py`. Modality is by
  family (`AUDIO_FAMILIES` / `VIDEO_FAMILIES`) → `gen_image.py` / `gen_audio.py` / `gen_video.py`, all
  sharing the registry. Validate with `--print-graph` (CI builds every model × quant, no weights needed).
- FLUX.2 weights are a ComfyUI **prerequisite** (see `setup/models.manifest`), not installed by this repo.
- **Keep the repo platform-agnostic:** no account IDs, profiles, domains, or keys in tracked files —
  deploy specifics live in gitignored `infra/terraform.tfvars` / `infra/backend.tf` and `/etc/forge/`.
