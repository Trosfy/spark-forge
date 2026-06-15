#!/usr/bin/env bash
# Create the artifacts bucket without Terraform (private, versioned).
# Creds come from the standard AWS credential chain (env, profile, SSO, instance role).
# usage: bootstrap_s3.sh <bucket> [region]
set -euo pipefail

bucket="${1:-${FORGE_S3_BUCKET:-}}"
region="${2:-${FORGE_S3_REGION:-us-east-1}}"
[ -n "$bucket" ] || {
  echo "usage: bootstrap_s3.sh <bucket> [region]"
  exit 2
}

if [ "$region" = "us-east-1" ]; then
  aws s3api create-bucket --bucket "$bucket" --region "$region"
else
  aws s3api create-bucket --bucket "$bucket" --region "$region" \
    --create-bucket-configuration LocationConstraint="$region"
fi

aws s3api put-bucket-versioning --bucket "$bucket" \
  --versioning-configuration Status=Enabled

aws s3api put-public-access-block --bucket "$bucket" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "created s3://$bucket ($region) — set FORGE_S3_BUCKET / FORGE_S3_REGION in your config"
