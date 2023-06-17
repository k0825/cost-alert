data "aws_caller_identity" "current" {}

resource "aws_budgets_budget" "budget" {
  name              = "Monthly 100 USD Budget"
  limit_amount      = "100"
  limit_unit        = "USD"
  time_period_start = "2020-01-01_00:00"
  time_period_end   = "2040-12-31_23:59"
  time_unit         = "MONTHLY"
  budget_type       = "COST"
  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_sns_topic_arns = [aws_sns_topic.topic.arn]
  }
}

resource "aws_sns_topic" "topic" {
  name = "budgets-alert-topic"
}

resource "aws_sns_topic_policy" "topic_policy" {
  arn = aws_sns_topic.topic.arn
  policy = templatefile("policies/sns_policy.json.tpl", {
    topic_arn  = aws_sns_topic.topic.arn
    account_id = data.aws_caller_identity.current.account_id
  })
}
