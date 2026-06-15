terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# CloudFront ACM certificates must live in us-east-1.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

module "forge_cdn" {
  source = "./modules/forge-cdn"
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  bucket_name               = var.bucket_name
  public_read               = var.public_read
  expire_days               = var.expire_days
  noncurrent_expire_days    = var.noncurrent_expire_days
  abort_multipart_days      = var.abort_multipart_days
  enable_cloudfront         = var.enable_cloudfront
  cloudfront_price_class    = var.cloudfront_price_class
  cloudfront_signed         = var.cloudfront_signed
  cloudfront_public_key_pem = var.cloudfront_public_key_path != "" ? file(var.cloudfront_public_key_path) : var.cloudfront_public_key_pem
  domain_name               = var.domain_name
  route53_zone_name         = var.route53_zone_name
  acm_certificate_arn       = var.acm_certificate_arn
}
