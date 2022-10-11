resource "aws_cloudwatch_metric_alarm" "failed_backup" {
  count = (length(var.sns-subscription-email)+length(var.sns-subscription-sqs)) > 0 ? 1 : 0

  alarm_name          = var.environment == "" ? "amazon-connect-backup-alarm-${var.environment}-${random_id.rand.dec}" : "amazon-connect-backup-alarm-${random_id.rand.dec}"
  alarm_description  = "Trigger an alert when amazon connect backup has failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  threshold           = "0"
  metric_query {
    id = "m1"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"

      dimensions = {
        FunctionName = local.lambda_function_name
      }
    }
  }
 
  alarm_actions      = [aws_sns_topic.topic[0].arn]
  treat_missing_data = "missing"

  tags = var.parent_tags
}