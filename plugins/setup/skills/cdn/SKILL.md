---
name: cdn
description: Provision the headless download CDN on AWS — a private S3 bucket fronted by CloudFront, optionally with signed/gated URLs and a custom domain — via the bundled Terraform module, then wire the forge config. Use whenever the user wants to set up, provision, or deploy the download/publishing infrastructure, e.g. "set up the CDN", "provision downloads", "deploy the S3/CloudFront", "set up headless downloads", "enable signed/gated downloads". Plans first and never applies without explicit confirmation.
---

# setup:cdn — provision the headless download CDN

Provision S3 + CloudFront for artifact downloads via the `forge-cdn` Terraform module,
then wire the config so `/forge:publish` works. Run it from a checkout of the repo — the
Terraform lives in `infra/`.

## 1. Prerequisites
- **Terraform** on PATH (the repo pins a version in `infra/.terraform-version`; use tfenv).
- **Active AWS credentials** — authenticate however you normally do. Verify with
  `aws sts get-caller-identity`.

## 2. Decide the shape (ask the user)
- **Gated or open?** `--signed` = private, expiring links; omit for public permanent links.
- **Custom domain?** `--domain <fqdn> --zone <route53-zone>` auto-creates the ACM cert
  (us-east-1) + DNS; omit for the free `*.cloudfront.net` domain.
- **Region** (`--region`).

## 3. Plan (never applies)

    "${CLAUDE_PLUGIN_ROOT}/scripts/setup_cdn.sh" --region <region> \
      [--signed] [--domain <fqdn> --zone <zone>] [--bucket <name>]

Runs preflight (terraform + creds), generates a signing keypair if `--signed` and none
exists (private key stays local, `0600`), writes `infra/terraform.tfvars`, and prints
`terraform plan`. **Show the plan and get the user's explicit OK before applying.**

## 4. Apply (only after confirmation)

    "${CLAUDE_PLUGIN_ROOT}/scripts/setup_cdn.sh" … --apply

Prints `FORGE_*` lines — write them into the forge config (`~/.config/forge/config` or
`/etc/forge/config`) so `/forge:publish` can sign + publish.

## 5. Verify
Publish a test file with `/forge:publish`. A signed deployment returns 200 for the
signed URL and 403 for the same URL without the signature.

## Notes
- No Terraform? `infra/bootstrap_s3.sh <bucket> [region]` makes just the private bucket.
- Local Terraform state by default; copy `infra/backend.tf.example` → `infra/backend.tf`
  for remote state.
- The private signing key never enters Terraform, state, or the repo.
