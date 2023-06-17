data "aws_caller_identity" "current" {}

data "aws_secretsmanager_secret" "secret" {
  name = "LINE_CHANNEL_ACCESS_TOKEN"
}
