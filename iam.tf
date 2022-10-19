# create iam role for lambda function
resource "aws_iam_role" "lambda_role" {
  name = var.environment == "" ? "lambda-connect-backup-${var.environment}-${random_id.rand.dec}" : "lambda-connect-backup-${random_id.rand.dec}"
  path = "/service-role/"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Effect" : "Allow",
        "Sid" : ""
      }
    ]
  })
  tags = var.parent_tags
}

# create iam policy for lambda to create and access a cloudwatch log group
resource "aws_iam_role_policy" "lambda_role_policy_cloudwatch" {
  name = "CloudwatchConnectBackUp${random_id.rand.dec}"
  role = aws_iam_role.lambda_role.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
        ],
        "Resource" : [
          aws_cloudwatch_log_group.log_group.arn,
          "${aws_cloudwatch_log_group.log_group.arn}:*",
        ]
      },
      {
        "Action" : "kms:Decrypt",
        "Effect" : "Allow",
        "Resource" : "*"
      },
    ]
    }
  )
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = [
      "s3:PutObject"
    ]
    resources = [
      aws_s3_bucket.connect_backup.arn,
      "${aws_s3_bucket.connect_backup.arn}/*",
    ]
  }
  statement {
    actions = [
      "connect:Describe*",
      "connect:List*",
    ]
    resources = [
      "*"
    ]
  }
  statement {
    actions = [
      "ds:DescribeDirectories",
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "ConnectBackUpPolicy${random_id.rand.dec}"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_policy_attachment" "lambda_policy-attach" {
  name       = "ConnectBackUpAttach${random_id.rand.dec}"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.lambda_policy.arn
}