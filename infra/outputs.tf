output "api_endpoint" {
  description = "HTTP API base URL"
  value       = module.api.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.lambda_name
}

output "github_oidc_role_arn" {
  description = "GitHub OIDC role ARN"
  value       = module.oidc.github_oidc_role_arn
}