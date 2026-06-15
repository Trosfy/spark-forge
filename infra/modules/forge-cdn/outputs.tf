output "bucket" {
  value       = aws_s3_bucket.artifacts.id
  description = "Bucket name — set as FORGE_S3_BUCKET."
}

output "cloudfront_domain" {
  value       = try(aws_cloudfront_distribution.artifacts[0].domain_name, null)
  description = "CloudFront distribution domain (null when disabled)."
}

output "cloudfront_key_pair_id" {
  value       = try(aws_cloudfront_public_key.signer[0].id, null)
  description = "CloudFront key-pair ID — set as FORGE_CDN_KEY_PAIR_ID for signed URLs (null when unsigned)."
}

output "download_base_url" {
  value       = var.enable_cloudfront ? "https://${var.domain_name != "" ? var.domain_name : try(aws_cloudfront_distribution.artifacts[0].domain_name, "")}" : null
  description = "Base download URL (custom domain if set, else CloudFront domain) — set as FORGE_CDN_DOMAIN."
}
