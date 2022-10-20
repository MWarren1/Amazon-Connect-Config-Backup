#*##############################*#
#* Amazon Connect Backup Bucket *#
#*##############################*#

# spliting up bucket name creation to make it easier to read
locals {
  bucket_name_prefix = var.s3_name_prefix == "" ? "" : "${var.s3_name_prefix}-"
  bucket_name_suffix = var.environment == "" ? "connect-backup-${random_id.rand.dec}" : "connect-backup-${var.environment}-${random_id.rand.dec}"
}

resource "aws_s3_bucket" "connect_backup" {
  bucket = "${local.bucket_name_prefix}${local.bucket_name_suffix}"

  tags = var.parent_tags
}

resource "aws_s3_bucket_acl" "connect_backup" {
  bucket = aws_s3_bucket.connect_backup.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "connect_backup" {
  bucket = aws_s3_bucket.connect_backup.id

  rule {
    id     = "connect-backup-daily-retention"
    status = "Enabled"
    filter {
      prefix = "daily/"
    }
    expiration {
      days = var.retention_daily_backups
    }
  }
  rule {
    id     = "connect-backup-weekly-retention"
    status = "Enabled"
    filter {
      prefix = "weekly/"
    }
    expiration {
      days = (var.retention_weekly_backups * 7)
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "connect_backup" {
  bucket = aws_s3_bucket.connect_backup.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "connect_backup" {
  bucket = aws_s3_bucket.connect_backup.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "connect_backup" {
  bucket = aws_s3_bucket.connect_backup.id
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "PutObjPolicy",
  "Statement": [
    {
      "Sid": "AllowSSLRequestsOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
          "arn:aws:s3:::${aws_s3_bucket.connect_backup.id}/*",
          "arn:aws:s3:::${aws_s3_bucket.connect_backup.id}"
      ],
      "Condition": {
          "Bool": {
              "aws:SecureTransport": "false"
          }
      }
    }
  ]
}
POLICY

}