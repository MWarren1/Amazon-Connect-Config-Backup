resource "aws_kms_key" "sns" {
  count = var.encyrpt_sns ? 1 : 0

  description = "amazon connect backup - used for sns encryption"
  tags = var.parent_tags
}

resource "aws_kms_alias" "sns" {
  count = var.encyrpt_sns ? 1 : 0
  
  name          = "alias/amamzon-connect-backup-sns-${random_id.rand.dec}"
  target_key_id = aws_kms_key.sns[0].key_id
}