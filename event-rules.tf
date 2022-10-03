#*##############*#
#* Daily Backup *#
#*##############*#

resource "aws_cloudwatch_event_rule" "connect_backup_daily" {
  name                = "connect_backup_daily-${random_id.rand.dec}"
  description         = "Event Rule for daily backup of amazon connect config"
  schedule_expression = "cron(0 1 * * ? *)"
  tags                = var.parent_tags
}

resource "aws_cloudwatch_event_target" "connect_backup_daily" {
  rule  = aws_cloudwatch_event_rule.connect_backup_daily.name
  arn   = aws_lambda_function.connect_backup.arn
  input = "{  \"backup-type\": \"daily\" }"
}

resource "aws_lambda_permission" "connect_backup_daily" {
  statement_id   = "AllowExecutionFromCloudWatch-Connect-Backup-Daily"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.connect_backup.arn
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.connect_backup_daily.arn
  source_account = data.aws_caller_identity.current.account_id
}

#*###############*#
#* Weekly Backup *#
#*###############*#

locals {
  # weekly_backup_day = "cron(0 1 * * ${var.weekly_backup_day} *)"
  weekly_backup_day = "cron(0 1 * * SUN *)"
}

resource "aws_cloudwatch_event_rule" "connect_backup_weekly" {
  name                = "connect_backup_weekly-${random_id.rand.dec}"
  description         = "Event Rule for weekly backup of amazon connect config"
  schedule_expression = local.weekly_backup_day
  tags                = var.parent_tags
}

resource "aws_cloudwatch_event_target" "connect_backup_weekly" {
  rule  = aws_cloudwatch_event_rule.connect_backup_weekly.name
  arn   = aws_lambda_function.connect_backup.arn
  input = "{  \"backup-type\": \"weekly\" }"
}

resource "aws_lambda_permission" "connect_backup_weekly" {
  statement_id   = "AllowExecutionFromCloudWatch-Connect-Backup-Weekly"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.connect_backup.arn
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.connect_backup_weekly.arn
  source_account = data.aws_caller_identity.current.account_id
}