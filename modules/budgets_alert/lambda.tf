locals {
  lambda_function_name = "budgets-alert-lambda"
}

resource "aws_lambda_function" "function" {
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  runtime          = "python3.10"

  depends_on = [
    aws_iam_role_policy_attachment.lambda_role_policy_attachment,
    aws_cloudwatch_log_group.log_group
  ]

  environment {
    variables = {
      LINE_BROADCAST_WEBHOOK_URL    = "https://api.line.me/v2/bot/message/broadcast"
      LINE_CHANNEL_ACCESS_TOKEN_ARN = data.aws_secretsmanager_secret.secret.arn
    }
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/src"
  output_path = "${path.module}/lambda/build/lambda.zip"
}

resource "aws_lambda_permission" "sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.topic.arn
}
