output "github_oidc_role_arn" {
  description = "GitHub OIDC role ARN"
  value       = aws_iam_role.github_oidc_role.arn
}