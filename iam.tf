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
    sid = "ConnectBackUpS3${random_id.rand.dec}"
    actions = [
      "s3:PutObject"
    ]
    resources = [
      aws_s3_bucket.connect_backup.arn,
      "${aws_s3_bucket.connect_backup.arn}/*",
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:ListInstances",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance",
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:ListContactFlow",
      "connect:ListRoutingProfiles",
      "connect:ListUserHierarchyGroups",
      "connect:ListUsers",
      "connect:ListPrompts",
      "connect:ListHoursOfOperations",
      "connect:ListQueues",
      "connect:ListLambdaFunctions",
      "connect:DescribeUserHierarchyStructure",
      "connect:DescribeInstance",
      "connect:DescribeQueue",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*",
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:DescribeContactFlow",
      "connect:ListContactFlows",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/contact-flow/*"
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:DescribeUser",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/agent/*"
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:DescribeRoutingProfile",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/routing-profile/*"
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:DescribeUserHierarchyGroup",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/agent-group/*"
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:ListQuickConnects",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/transfer-destination/*"
      # "*"
    ]
  }
  statement {
    # sid = "ConnectBackUpConnect${random_id.rand.dec}"
    actions = [
      "connect:DescribeHoursOfOperation",
      # "*"
    ]
    resources = [
      "arn:aws:connect:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:instance/*/operating-hours/*"
      # "*"
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