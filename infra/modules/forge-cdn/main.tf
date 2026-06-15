data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  # AWS best practice: globally-unique, account- and region-scoped name.
  bucket_name = var.bucket_name != "" ? var.bucket_name : "spark-forge-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
}

resource "aws_s3_bucket" "artifacts" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = !var.public_read
  block_public_policy     = !var.public_read
  ignore_public_acls      = !var.public_read
  restrict_public_buckets = !var.public_read
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  count  = (var.expire_days > 0 || var.noncurrent_expire_days > 0 || var.abort_multipart_days > 0) ? 1 : 0
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "forge-artifacts"
    status = "Enabled"
    filter {}

    dynamic "expiration" {
      for_each = var.expire_days > 0 ? [1] : []
      content {
        days = var.expire_days
      }
    }

    dynamic "noncurrent_version_expiration" {
      for_each = var.noncurrent_expire_days > 0 ? [1] : []
      content {
        noncurrent_days = var.noncurrent_expire_days
      }
    }

    dynamic "abort_incomplete_multipart_upload" {
      for_each = var.abort_multipart_days > 0 ? [1] : []
      content {
        days_after_initiation = var.abort_multipart_days
      }
    }
  }
}
