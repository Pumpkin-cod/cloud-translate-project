output "lambda_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.translate_handler.arn
}

output "lambda_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.translate_handler.function_name
}