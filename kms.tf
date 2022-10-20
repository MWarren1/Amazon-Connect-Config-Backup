resource "aws_kms_key" "sns" {
  count = var.encyrpt_sns ? 1 : 0

  description = "amazon connect backup - used for sns encryption"
  policy      = <<POLICY
  {
    "Version": "2012-10-17",
    "Id": "key-default-1",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::119511693873:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow_CloudWatch_alarms",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudwatch.amazonaws.com"
            },
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey*"
            ],
            "Resource": "*"
        }
    ]
}
POLICY

  tags = var.parent_tags
}

resource "aws_kms_alias" "sns" {
  count = var.encyrpt_sns ? 1 : 0

  name          = "alias/amazon-connect-backup-sns-${random_id.rand.dec}"
  target_key_id = aws_kms_key.sns[0].key_id
}