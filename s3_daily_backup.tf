#*####################################*#
#* Amazon Connect Daily Backup Bucket *#
#*####################################*#

# spliting up bucket name creation to make it easier to read
locals {
  daily_bucket_name_prefix = var.s3_name_prefix == "" ? "" : "${var.s3_name_prefix}-"
  daily_bucket_name_suffix = var.environment == "" ? "connect-backup-daily-${random_id.rand.dec}" : "connect-backup-daily-${var.environment}-${random_id.rand.dec}"
}

resource "aws_s3_bucket" "connect_backup_daily" {
  bucket = "${local.daily_bucket_name_prefix}${local.daily_bucket_name_suffix}"

  tags = var.parent_tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "connect_backup_daily" {
  bucket = aws_s3_bucket.connect_backup_daily.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "connect_backup_daily" {
  bucket = aws_s3_bucket.connect_backup_daily.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "connect_backup_daily" {
  count = var.log_bucket_name != "" ? 1 : 0
  ## add logs into a specific bucket
  bucket        = aws_s3_bucket.connect_backup_daily.id
  target_bucket = var.log_bucket_name
  target_prefix = "log/s3/${data.aws_caller_identity.current.account_id}/${aws_s3_bucket.connect_backup_daily.id}/"
}

resource "aws_s3_bucket_policy" "connect_backup_daily" {
  bucket = aws_s3_bucket.connect_backup_daily.id
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
          "arn:aws:s3:::${aws_s3_bucket.connect_backup_daily.id}/*",
          "arn:aws:s3:::${aws_s3_bucket.connect_backup_daily.id}"
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

resource "aws_s3_bucket_versioning" "connect_backup_daily" {
  bucket = aws_s3_bucket.connect_backup_daily.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "connect_backup_daily" {
  count = var.object_lock_enabled ? 1 : 0

  bucket              = aws_s3_bucket.connect_backup_daily.id
  object_lock_enabled = "Enabled"
  rule {
    default_retention {
      mode = var.object_lock_mode
      days = var.retention_daily_backups
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "connect_backup_daily" {
  bucket = aws_s3_bucket.connect_backup_daily.id

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
}
