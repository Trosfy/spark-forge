# Optional CloudFront distribution for stable, headless download URLs.
# Bucket stays private (OAC). Optionally: signed URLs (key group), a custom domain,
# and an auto-provisioned ACM cert + Route53 records. With no custom domain it serves
# the free *.cloudfront.net domain + default cert.

locals {
  use_custom_domain = var.enable_cloudfront && var.domain_name != ""
  manage_dns        = local.use_custom_domain && var.route53_zone_name != ""
  create_cert       = local.use_custom_domain && var.acm_certificate_arn == "" && var.route53_zone_name != ""
  cert_arn          = var.acm_certificate_arn != "" ? var.acm_certificate_arn : try(one(aws_acm_certificate_validation.cdn[*].certificate_arn), null)
  has_cert          = local.cert_arn != null && local.cert_arn != ""
}

data "aws_cloudfront_cache_policy" "optimized" {
  count = var.enable_cloudfront ? 1 : 0
  name  = "Managed-CachingOptimized"
}

resource "aws_cloudfront_origin_access_control" "artifacts" {
  count                             = var.enable_cloudfront ? 1 : 0
  name                              = "${local.bucket_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_public_key" "signer" {
  count       = var.enable_cloudfront && var.cloudfront_signed ? 1 : 0
  name        = "${local.bucket_name}-signer"
  encoded_key = var.cloudfront_public_key_pem
  comment     = "forge signed-URL public key"
}

resource "aws_cloudfront_key_group" "signers" {
  count = var.enable_cloudfront && var.cloudfront_signed ? 1 : 0
  name  = "${local.bucket_name}-signers"
  items = [aws_cloudfront_public_key.signer[0].id]
}

resource "aws_acm_certificate" "cdn" {
  count             = local.create_cert ? 1 : 0
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_route53_zone" "domain" {
  count        = local.manage_dns ? 1 : 0
  name         = var.route53_zone_name
  private_zone = false
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in flatten([for c in aws_acm_certificate.cdn : c.domain_validation_options]) :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id         = data.aws_route53_zone.domain[0].zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 60
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "cdn" {
  count                   = local.create_cert ? 1 : 0
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.cdn[0].arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

resource "aws_cloudfront_distribution" "artifacts" {
  count       = var.enable_cloudfront ? 1 : 0
  enabled     = true
  comment     = "forge artifacts: ${local.bucket_name}"
  price_class = var.cloudfront_price_class
  aliases     = local.has_cert ? [var.domain_name] : []

  origin {
    domain_name              = aws_s3_bucket.artifacts.bucket_regional_domain_name
    origin_id                = "s3-${local.bucket_name}"
    origin_access_control_id = aws_cloudfront_origin_access_control.artifacts[0].id
  }

  default_cache_behavior {
    target_origin_id       = "s3-${local.bucket_name}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized[0].id
    trusted_key_groups     = var.cloudfront_signed ? [aws_cloudfront_key_group.signers[0].id] : []
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = local.has_cert ? null : true
    acm_certificate_arn            = local.has_cert ? local.cert_arn : null
    ssl_support_method             = local.has_cert ? "sni-only" : null
    minimum_protocol_version       = local.has_cert ? "TLSv1.2_2021" : null
  }

  depends_on = [aws_acm_certificate_validation.cdn]
}

resource "aws_route53_record" "alias" {
  count   = local.manage_dns ? 1 : 0
  zone_id = data.aws_route53_zone.domain[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.artifacts[0].domain_name
    zone_id                = aws_cloudfront_distribution.artifacts[0].hosted_zone_id
    evaluate_target_health = false
  }
}

data "aws_iam_policy_document" "cloudfront_oac" {
  count = var.enable_cloudfront ? 1 : 0

  statement {
    sid       = "AllowCloudFrontRead"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.artifacts.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.artifacts[0].arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudfront_oac" {
  count  = var.enable_cloudfront ? 1 : 0
  bucket = aws_s3_bucket.artifacts.id
  policy = data.aws_iam_policy_document.cloudfront_oac[0].json
}
