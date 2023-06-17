resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 14
}
