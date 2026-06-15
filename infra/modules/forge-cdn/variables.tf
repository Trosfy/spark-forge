variable "bucket_name" {
  type        = string
  description = "Override the artifacts bucket name. Empty = spark-forge-<account-id>-<region> (AWS best practice for global uniqueness)."
  default     = ""
}

variable "public_read" {
  type        = bool
  description = "Allow public-read objects for direct S3 URLs. Off by default (CloudFront+OAC is preferred)."
  default     = false
}

variable "expire_days" {
  type        = number
  description = "Delete current objects older than N days (0 disables)."
  default     = 90
}

variable "noncurrent_expire_days" {
  type        = number
  description = "Delete noncurrent (versioned) object versions after N days (0 disables)."
  default     = 30
}

variable "abort_multipart_days" {
  type        = number
  description = "Abort incomplete multipart uploads after N days (0 disables)."
  default     = 7
}

variable "enable_cloudfront" {
  type        = bool
  description = "Provision a CloudFront distribution (OAC, bucket stays private) for stable download URLs."
  default     = false
}

variable "cloudfront_price_class" {
  type        = string
  description = "CloudFront price class (PriceClass_100 = cheapest: North America + Europe)."
  default     = "PriceClass_100"
}

variable "cloudfront_signed" {
  type        = bool
  description = "Require CloudFront signed URLs (gated downloads via a trusted key group)."
  default     = false
}

variable "cloudfront_public_key_pem" {
  type        = string
  description = "PEM PUBLIC key for signed URLs (required when cloudfront_signed=true). The matching private key never goes to Terraform."
  default     = ""
}

variable "domain_name" {
  type        = string
  description = "Custom domain (CNAME). Empty = free *.cloudfront.net default domain + cert."
  default     = ""
}

variable "route53_zone_name" {
  type        = string
  description = "Route53 hosted zone for the domain (e.g. example.com). Set with domain_name to auto-create the cert + DNS records and the alias."
  default     = ""
}

variable "acm_certificate_arn" {
  type        = string
  description = "Reuse an existing ACM cert (us-east-1) instead of creating one. Empty + route53_zone_name set => a cert is created automatically."
  default     = ""
}
