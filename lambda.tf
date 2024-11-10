#*##############################*#
#* Amazon Connect Backup Lambda *#
#*##############################*#

locals {
  # This local is used in the lambda and log group resources
  lambda_function_name = var.environment == "" ? "amazon-connect-backup-${var.environment}-${random_id.rand.dec}" : "amazon-connect-backup-${random_id.rand.dec}"
}

# Lambda function backup amazon connect
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/app-code/src/connect_backup"
  output_path = "${path.module}/app-code/dist/connect_backup.zip"
}

resource "aws_lambda_function" "connect_backup" {
  description      = "this lambda backups up amazon connect instances"
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "connect_backup.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 900
  environment {
    variables = {
      DAILY_BACKUP_S3_BUCKET  = aws_s3_bucket.connect_backup_daily.id
      WEEKLY_BACKUP_S3_BUCKET = aws_s3_bucket.connect_backup_weekly.id
    }
  }
  tracing_config {
    mode = "Active"
  }
  tags = var.parent_tags
}
