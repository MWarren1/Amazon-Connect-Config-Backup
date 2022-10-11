# creates sns topic for cloudwatch alarm
resource "aws_sns_topic" "topic" {
  count = (length(var.sns-subscription-email)+length(var.sns-subscription-sqs)) > 0 ? 1 : 0

  name_prefix = var.environment == "" ? "amazon-connect-backup-alarm-${var.environment}-" : "amazon-connect-backup-alarm-"
  tags = var.parent_tags
}

# subscribes email addresses to sns topic
resource "aws_sns_topic_subscription" "alarm-sns-subscription-email" {
  for_each = toset(var.sns-subscription-email)

  topic_arn     = aws_sns_topic.topic[0].arn
  protocol      = "email"
  endpoint      = each.key
  filter_policy = ""
}

# subscribes sqs queues to sns topic
resource "aws_sns_topic_subscription" "alarm-sns-subscription-sqs" {
  for_each = toset(var.sns-subscription-sqs)

  topic_arn            = aws_sns_topic.topic[0].arn
  protocol             = "sqs"
  endpoint             = each.key
  raw_message_delivery = true
  filter_policy        = ""
}