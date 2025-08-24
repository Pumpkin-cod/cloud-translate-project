output "api_endpoint" {
  description = "HTTP API base URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}