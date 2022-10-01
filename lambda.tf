# #*##############################*#
# #* Amazon Connect Backup Lambda *#
# #*##############################*#

# module "connect_backup" {
#   source = "github.com/Hyde-Housing-Association-Limited/tf-common-modules.git//infra/hyde-lambda?ref=v0.16.0"

#   lambda_name        = "connect_backup-${var.environment}"
#   lambda_description = "this lambda backups up amazon connect instances"
#   lambda_filepath    = "${path.module}/app-code/dist/connect_backup.zip"
#   lambda_handler     = "connect_backup.lambda_handler"
#   lambda_runtime     = "python3.9"
#   lambda_timeout     = 600
#   lambda_memory      = 128
#   lambda_environmental_variables = {
#     OUTPUT_S3_BUCKET = aws_s3_bucket.connect_backup.id
#   }
#   cloudwatch_retention = 60
#   iam_role_permissions = {
#     actions : [
#       "s3:PutObject",
#       "connect:List*",
#       "connect:Describe*",
#       "connect:Get*"
#     ],
#     resources : [
#       aws_s3_bucket.connect_backup.arn,
#       "${aws_s3_bucket.connect_backup.arn}/*",
#       "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*"
#     ]
#   }
#   parent_tags = merge(
#     var.parent_tags,
#     {
#       application = "connect-backup"
#     }
#   )
# }
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
  timeout          = 600
  environment {
    variables = {
      OUTPUT_S3_BUCKET = aws_s3_bucket.connect_backup.id
    }
  }
  tags = var.parent_tags
}