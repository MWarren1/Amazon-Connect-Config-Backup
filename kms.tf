resource "aws_kms_key" "sns" {
  count = var.encyrpt_sns ? 1 : 0

  description = "amazon connect backup - used for sns encryption"
  policy = <<POLICY
  {
    "Sid": "Allow_Publish_Alarms",
    "Effect": "Allow",
    "Principal":
    {
        "Service": [
            "cloudwatch.amazonaws.com"
        ]
    },
    "Action": "sns:Publish",
    "Resource": "*"
}
POLICY

  tags = var.parent_tags
}

resource "aws_kms_alias" "sns" {
  count = var.encyrpt_sns ? 1 : 0

  name          = "alias/amazon-connect-backup-sns-${random_id.rand.dec}"
  target_key_id = aws_kms_key.sns[0].key_id
}