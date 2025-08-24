variable "requests_bucket_name" {
  description = "Name for the requests S3 bucket"
  type        = string
}

variable "responses_bucket_name" {
  description = "Name for the responses S3 bucket"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}