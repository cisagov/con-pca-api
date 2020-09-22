# ===================================
# Lambda Layer
# ===================================
data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${path.module}/layer/"
  output_path = "${path.module}/output/layer.zip"
}

resource "aws_lambda_layer_version" "layer" {
  filename         = data.archive_file.layer.output_path
  source_code_hash = data.archive_file.layer.output_path
  layer_name       = "${var.app}-${var.env}-layer"

  compatible_runtimes = ["python3.8"]

  lifecycle {
    create_before_destroy = true
  }
}

data "archive_file" "scikit" {
  type        = "zip"
  source_dir  = "${path.module}/layers/scikit"
  output_path = "${path.module}/output/scikit.zip"
}

resource "aws_lambda_layer_version" "scikit" {
  filename         = data.archive_file.scikit.output_path
  source_code_hash = data.archive_file.scikit.output_path
  layer_name       = "${var.app}-${var.env}-scikit"

  compatible_runtimes = ["python3.8"]

  lifecycle {
    create_before_destroy = true
  }
}


# ===================================
# Lambda Function
# ===================================
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/"
  output_path = "${path.module}/output/code.zip"
}

resource "aws_lambda_function" "tasks" {
  filename         = data.archive_file.code.output_path
  function_name    = "${var.app}-${var.env}-tasks"
  handler          = "lambda_functions.tasks.handler.lambda_handler"
  role             = aws_iam_role.lambda_exec_role.arn
  memory_size      = 1024
  runtime          = "python3.8"
  source_code_hash = data.archive_file.code.output_base64sha256
  timeout          = 300

  layers = [
    "arn:aws:lambda:us-east-1:668099181075:layer:AWSLambda-Python38-SciPy1x:29",
    aws_lambda_layer_version.layer.arn,
    aws_lambda_layer_version.scikit.arn
  ]

  environment {
    variables = local.environment
  }

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.api.id]
  }
}

# ===================================
# IAM Roles
# ===================================
resource "aws_iam_role" "lambda_exec_role" {
  name               = "${var.app}-${var.env}-lambda"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    sid    = "AllowCreatingLogGroups"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:*"
    ]

    actions = [
      "logs:CreateLogGroup"
    ]
  }

  statement {
    sid    = "AllowWritingLogs"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:log-group:/aws/lambda/*:*"
    ]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }

  statement {
    sid    = "AllowVPC"
    effect = "Allow"

    resources = [
      "*"
    ]

    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
  }

  statement {
    actions = [
      "s3:*",
      "route53:*"
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]

    resources = [
      data.aws_ssm_parameter.ses_assume_role_arn.value
    ]
  }
}

resource "aws_iam_policy" "lambda_iam_policy" {
  name   = "${var.app}-${var.env}-lambda"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_iam_policy.arn
  role       = aws_iam_role.lambda_exec_role.name
}

# ===================================
# Cloudwatch Event rule
# ===================================
resource "aws_cloudwatch_event_rule" "tasks" {
  name                = "${var.app}-${var.env}-tasks"
  description         = "Every 5 minutes"
  schedule_expression = "rate(5 minutes)"
}
resource "aws_cloudwatch_event_target" "tasks" {
  rule      = aws_cloudwatch_event_rule.tasks.name
  target_id = "lambda"
  arn       = aws_lambda_function.tasks.arn
}
resource "aws_lambda_permission" "tasks" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tasks.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tasks.arn
}
