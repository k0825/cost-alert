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
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "./lambda/src"
  output_path = "./build/lambda.zip"
}

resource "aws_lambda_permission" "sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.topic.arn
}
