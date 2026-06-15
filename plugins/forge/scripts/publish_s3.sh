#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"
forge_load_config

usage() {
  echo "usage: publish_s3.sh <file-or-dir> [--public] [--url]"
  exit 2
}
[ $# -ge 1 ] || usage
src="$1"
shift

want_url=0
for arg in "$@"; do
  case "$arg" in
    --public) FORGE_S3_PUBLIC=true ;;
    --url) want_url=1 ;;
    *) usage ;;
  esac
done

[ -n "${FORGE_S3_BUCKET:-}" ] || {
  echo "FORGE_S3_BUCKET not set (see config.example / infra/)"
  exit 1
}
[ -e "$src" ] || {
  echo "no such path: $src"
  exit 1
}

aws_args=()
[ -n "${FORGE_AWS_PROFILE:-}" ] && aws_args+=(--profile "$FORGE_AWS_PROFILE")
[ -n "${FORGE_S3_REGION:-}" ] && aws_args+=(--region "$FORGE_S3_REGION")

acl=()
[ "$FORGE_S3_PUBLIC" = "true" ] && acl+=(--acl public-read)

base="s3://$FORGE_S3_BUCKET/$FORGE_S3_PREFIX"
name="$(basename "$src")"
if [ -d "$src" ]; then
  aws "${aws_args[@]}" s3 cp --recursive "${acl[@]}" "$src" "$base/$name/"
  key="$FORGE_S3_PREFIX/$name/"
else
  aws "${aws_args[@]}" s3 cp "${acl[@]}" "$src" "$base/$name"
  key="$FORGE_S3_PREFIX/$name"
fi
echo "uploaded: s3://$FORGE_S3_BUCKET/$key"

if [ "$want_url" = 1 ] && [ -f "$src" ]; then
  if [ -n "${FORGE_CDN_DOMAIN:-}" ] && [ -n "${FORGE_CDN_KEY_PAIR_ID:-}" ] && [ -n "${FORGE_CDN_PRIVATE_KEY:-}" ]; then
    echo "url: $("$HERE/cloudfront_sign.sh" "https://$FORGE_CDN_DOMAIN/$key" "$FORGE_CDN_KEY_PAIR_ID" "$FORGE_CDN_PRIVATE_KEY" "${FORGE_CDN_TTL:-3600}")"
  elif [ -n "${FORGE_CDN_DOMAIN:-}" ]; then
    echo "url: https://$FORGE_CDN_DOMAIN/$key"
  elif [ "$FORGE_S3_PUBLIC" = "true" ]; then
    echo "url: https://$FORGE_S3_BUCKET.s3.${FORGE_S3_REGION:-us-east-1}.amazonaws.com/$key"
  else
    aws "${aws_args[@]}" s3 presign "s3://$FORGE_S3_BUCKET/$key" --expires-in 86400
    echo "(presigned 24h; with temporary/STS credentials the URL expires when the session does, <=12h)"
  fi
fi
