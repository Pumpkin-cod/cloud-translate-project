output "sns_topic_arn" {
  description = "SNS topic ARN for billing alerts"
  value       = aws_sns_topic.billing_alerts.arn
}