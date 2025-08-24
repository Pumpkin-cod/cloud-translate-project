output "requests_bucket" {
  description = "Requests S3 bucket resource"
  value       = aws_s3_bucket.requests
}

output "responses_bucket" {
  description = "Responses S3 bucket resource"
  value       = aws_s3_bucket.responses
}

output "requests_bucket_name" {
  description = "Requests S3 bucket name"
  value       = aws_s3_bucket.requests.bucket
}

output "responses_bucket_name" {
  description = "Responses S3 bucket name"
  value       = aws_s3_bucket.responses.bucket
}