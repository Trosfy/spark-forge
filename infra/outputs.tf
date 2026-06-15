output "bucket" {
  value       = module.forge_cdn.bucket
  description = "Bucket name — set as FORGE_S3_BUCKET."
}

output "region" {
  value       = var.region
  description = "Bucket region — set as FORGE_S3_REGION."
}

output "cloudfront_domain" {
  value       = module.forge_cdn.cloudfront_domain
  description = "CloudFront distribution domain (null when disabled)."
}

output "cloudfront_key_pair_id" {
  value       = module.forge_cdn.cloudfront_key_pair_id
  description = "CloudFront key-pair ID for signed URLs (null when unsigned)."
}

output "download_base_url" {
  value       = module.forge_cdn.download_base_url
  description = "Base download URL — set as FORGE_CDN_DOMAIN."
}
