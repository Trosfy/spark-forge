#!/usr/bin/env bash
# Mint a CloudFront canned-policy signed URL with openssl (no extra deps).
# usage: cloudfront_sign.sh <url> <key-pair-id> <private-key-path> [ttl-seconds]
set -euo pipefail

url="${1:?url}"
kpid="${2:?key-pair-id}"
key="${3:?private-key-path}"
ttl="${4:-3600}"
[ -f "$key" ] || {
  echo "private key not found: $key" >&2
  exit 1
}

expires=$(($(date +%s) + ttl))
policy="{\"Statement\":[{\"Resource\":\"${url}\",\"Condition\":{\"DateLessThan\":{\"AWS:EpochTime\":${expires}}}}]}"
sig="$(printf '%s' "$policy" | openssl dgst -sha1 -sign "$key" | openssl base64 -A | tr '+=/' '-_~')"
printf '%s?Expires=%s&Signature=%s&Key-Pair-Id=%s\n' "$url" "$expires" "$sig" "$kpid"
