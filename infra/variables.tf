# Root inputs — forwarded to the forge-cdn module. See modules/forge-cdn for details.

variable "region" {
  type        = string
  description = "AWS region for the bucket + provider."
  default     = "us-east-1"
}

variable "bucket_name" {
  type        = string
  description = "Override bucket name. Empty = spark-forge-<account-id>-<region>."
  default     = ""
}

variable "public_read" {
  type    = bool
  default = false
}

variable "expire_days" {
  type    = number
  default = 90
}

variable "noncurrent_expire_days" {
  type    = number
  default = 30
}

variable "abort_multipart_days" {
  type    = number
  default = 7
}

variable "enable_cloudfront" {
  type    = bool
  default = false
}

variable "cloudfront_price_class" {
  type    = string
  default = "PriceClass_100"
}

variable "cloudfront_signed" {
  type    = bool
  default = false
}

variable "cloudfront_public_key_pem" {
  type    = string
  default = ""
}

variable "cloudfront_public_key_path" {
  type        = string
  description = "Path to a PEM public key for signed URLs (read at apply via file()). Easier than pasting PEM; alternative to cloudfront_public_key_pem."
  default     = ""
}

variable "domain_name" {
  type    = string
  default = ""
}

variable "route53_zone_name" {
  type    = string
  default = ""
}

variable "acm_certificate_arn" {
  type    = string
  default = ""
}
