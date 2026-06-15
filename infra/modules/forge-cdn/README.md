# forge-cdn

A private S3 bucket for generated artifacts, optionally fronted by CloudFront for
stable, headless downloads. The bucket stays private (Origin Access Control);
options add signed URLs, a custom domain (auto-creates + DNS-validates an ACM cert
and the Route53 alias), and configurable lifecycle. Defaults are free: a private
bucket and, if CloudFront is enabled, the `*.cloudfront.net` domain + default cert.

## Usage

The module needs **two AWS providers** — the default (bucket region) and a
`us_east_1` alias (CloudFront requires its ACM cert in us-east-1):

```hcl
provider "aws" { region = "us-east-1" }
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

module "forge_cdn" {
  source = "./modules/forge-cdn"
  # or remote: "github.com/Trosfy/spark-forge//infra/modules/forge-cdn?ref=v0.1.0"
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  enable_cloudfront = true
  domain_name       = "downloads.example.com" # omit for the free *.cloudfront.net domain
  route53_zone_name = "example.com"           # set -> auto cert + DNS records + alias
  # bucket_name defaults to spark-forge-<account-id>-<region>
}

output "download_base_url" { value = module.forge_cdn.download_base_url }
```

## Signed URLs (private key)

Signing uses a CloudFront key pair. **You** generate it; the private key never
enters Terraform, state, or the repo:

```bash
openssl genrsa -out /etc/forge/cloudfront_private_key.pem 2048
openssl rsa -pubout -in /etc/forge/cloudfront_private_key.pem -out cloudfront_public_key.pem
```

Pass only the **public** key and enable signing:

```hcl
cloudfront_signed         = true
cloudfront_public_key_pem = file("cloudfront_public_key.pem")
```

The private key stays at `FORGE_CDN_PRIVATE_KEY` (gitignored `*.pem`); the publish
script signs URLs with it at runtime.

## Key inputs

| Input | Default | Notes |
|---|---|---|
| `bucket_name` | `""` | empty → `spark-forge-<account>-<region>` |
| `enable_cloudfront` | `false` | front the bucket with a CDN |
| `domain_name` / `route53_zone_name` | `""` | both set → custom domain + auto ACM/DNS |
| `acm_certificate_arn` | `""` | reuse an existing us-east-1 cert instead of creating one |
| `cloudfront_signed` / `cloudfront_public_key_pem` | `false` / `""` | gated downloads |
| `expire_days` / `noncurrent_expire_days` / `abort_multipart_days` | `90` / `30` / `7` | lifecycle (0 disables) |

## Outputs

`bucket`, `download_base_url`, `cloudfront_domain`, `cloudfront_key_pair_id`.
