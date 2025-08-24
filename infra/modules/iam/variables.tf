variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "requests_bucket" {
  description = "Requests S3 bucket resource"
}

variable "responses_bucket" {
  description = "Responses S3 bucket resource"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}