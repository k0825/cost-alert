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
