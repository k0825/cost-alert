resource "aws_cloudwatch_event_rule" "event_rule" {
  name                = "daily_alert_event"
  description         = "Daily alert Event"
  schedule_expression = "cron(0 0 * * ? *)"
}

resource "aws_cloudwatch_event_target" "event_target" {
  rule      = aws_cloudwatch_event_rule.event_rule.name
  target_id = "daily_alert"
  arn       = aws_lambda_function.function.arn
}
