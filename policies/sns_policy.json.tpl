{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "budgets.amazonaws.com"
      },
      "Action": [
        "sns:Publish"
      ],
      "Resource": "${topic_arn}",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "${account_id}"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:budgets::${account_id}:*"
        }
      }
    }
  ]
}
