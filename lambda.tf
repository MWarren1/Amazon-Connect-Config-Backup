#*##############################*#
#* Amazon Connect Backup Lambda *#
#*##############################*#

locals {
  # This local is used in the lambda and log group resources
  lambda_function_name = "amazon-connect-backup-${var.environment}-${random_id.rand.dec}"
}

# Lambda function backup amazon connect
resource "aws_lambda_function" "connect_backup" {
  description      = "this lambda backups up amazon connect instances"
  filename         = "${path.module}/app-code/dist/connect_backup.zip"
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "connect_backup.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/app-code/dist/connect_backup.zip")
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = var.lambda_timeout
  environment {
    variables = {
      OUTPUT_S3_BUCKET = aws_s3_bucket.connect_backup.id
    }
  }
  tags = var.parent_tags
}