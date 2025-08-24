variable "aws_region" { default = "us-east-1" }
variable "project_name" { default = "cloud-translate-project" }
variable "environment" { default = "dev" }

variable "requests_bucket_name" { default = "ctp-requests-us-east-1" }
variable "responses_bucket_name" { default = "ctp-responses-us-east-1" }

variable "log_retention_days" { default = 14 }

# Billing alarm email
variable "billing_alert_email" { 
  description = "Email to receive billing alerts" 
  type = string 
}

# GitHub OIDC inputs
variable "github_owner" { 
  description = "GitHub org/user" 
  type = string 
}
variable "github_repo" { 
  description = "GitHub repo name" 
  type = string 
}
variable "allowed_branches" { 
  type = list(string) 
  default = ["main"] 
}
variable "github_oidc_role_name" { 
  default = "GitHubOIDCRole" 
}
variable "enable_admin_attachment" { 
  type = bool 
  default = true 
}

# Lambda settings
variable "lambda_memory_mb" { default = 512 }
variable "lambda_timeout_s" { default = 10 }