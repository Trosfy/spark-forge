#!/usr/bin/env bash
# Provision the forge download CDN (S3 + CloudFront) via the forge-cdn Terraform
# module, then print the FORGE_* config lines. Plans by default; --apply to create.
# Credentials: uses the ambient AWS credential chain — authenticate first however you
# normally do (SSO, profile, assumed role, instance role).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA="${FORGE_INFRA_DIR:-$(cd "$HERE/../../../infra" 2>/dev/null && pwd || true)}"

region="us-east-1"
bucket=""
domain=""
zone=""
signed=0
apply=0
keyfile="${FORGE_CDN_PRIVATE_KEY:-/etc/forge/cloudfront_private_key.pem}"

while [ $# -gt 0 ]; do
  case "$1" in
    --region) region="$2"; shift 2 ;;
    --bucket) bucket="$2"; shift 2 ;;
    --domain) domain="$2"; shift 2 ;;
    --zone) zone="$2"; shift 2 ;;
    --key) keyfile="$2"; shift 2 ;;
    --signed) signed=1; shift ;;
    --apply) apply=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -n "$INFRA" ] && [ -d "$INFRA" ] || {
  echo "infra/ not found — run from a clone of the spark-forge repo, or set FORGE_INFRA_DIR" >&2
  exit 1
}
command -v terraform >/dev/null || { echo "terraform not found (install via tfenv)" >&2; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || {
  echo "AWS credentials not active — authenticate first, then retry" >&2
  exit 1
}

pubkey=""
if [ "$signed" = 1 ]; then
  pubkey="$(dirname "$keyfile")/cloudfront_public_key.pem"
  if [ ! -f "$keyfile" ]; then
    mkdir -p "$(dirname "$keyfile")"
    (umask 077 && openssl genrsa -out "$keyfile" 2048 2>/dev/null)
    chmod 600 "$keyfile"
    echo "generated signing private key: $keyfile"
  fi
  openssl rsa -pubout -in "$keyfile" -out "$pubkey" 2>/dev/null
  chmod 644 "$pubkey"
fi

tfvars="$INFRA/terraform.tfvars"
{
  echo "region            = \"$region\""
  echo "enable_cloudfront = true"
  [ -n "$bucket" ] && echo "bucket_name       = \"$bucket\""
  [ -n "$domain" ] && echo "domain_name       = \"$domain\""
  [ -n "$zone" ] && echo "route53_zone_name = \"$zone\""
  if [ "$signed" = 1 ]; then
    echo "cloudfront_signed          = true"
    echo "cloudfront_public_key_path = \"$pubkey\""
  fi
} >"$tfvars"
echo "wrote $tfvars"

terraform -chdir="$INFRA" init -input=false >/dev/null
terraform -chdir="$INFRA" plan -input=false

if [ "$apply" != 1 ]; then
  echo
  echo "plan only — re-run with --apply to create the resources"
  exit 0
fi

terraform -chdir="$INFRA" apply -auto-approve -input=false

echo
echo "=== forge config (add these to your forge config) ==="
echo "FORGE_S3_BUCKET=$(terraform -chdir="$INFRA" output -raw bucket)"
echo "FORGE_S3_REGION=$region"
base="$(terraform -chdir="$INFRA" output -raw download_base_url 2>/dev/null || true)"
[ -n "$base" ] && echo "FORGE_CDN_DOMAIN=${base#https://}"
if [ "$signed" = 1 ]; then
  echo "FORGE_CDN_KEY_PAIR_ID=$(terraform -chdir="$INFRA" output -raw cloudfront_key_pair_id 2>/dev/null || true)"
  echo "FORGE_CDN_PRIVATE_KEY=$keyfile"
fi
