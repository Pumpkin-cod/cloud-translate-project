terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  project = var.project_name
  tags = {
    Project     = local.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  requests_bucket_name  = var.requests_bucket_name
  responses_bucket_name = var.responses_bucket_name
  tags                  = local.tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"
  
  project_name      = local.project
  environment       = var.environment
  aws_region        = var.aws_region
  requests_bucket   = module.s3.requests_bucket
  responses_bucket  = module.s3.responses_bucket
  tags              = local.tags
}

# Lambda Module
module "lambda" {
  source = "./modules/lambda"
  
  project_name      = local.project
  environment       = var.environment
  aws_region        = var.aws_region
  lambda_role_arn   = module.iam.lambda_role_arn
  requests_bucket   = module.s3.requests_bucket_name
  responses_bucket  = module.s3.responses_bucket_name
  memory_size       = var.lambda_memory_mb
  timeout           = var.lambda_timeout_s
  log_retention     = var.log_retention_days
  tags              = local.tags
}

# API Gateway Module
module "api" {
  source = "./modules/api"
  
  project_name     = local.project
  environment      = var.environment
  lambda_arn       = module.lambda.lambda_arn
  lambda_name      = module.lambda.lambda_name
  tags             = local.tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name         = local.project
  environment          = var.environment
  billing_alert_email  = var.billing_alert_email
  tags                 = local.tags
}

# OIDC Module
module "oidc" {
  source = "./modules/oidc"
  
  github_owner             = var.github_owner
  github_repo              = var.github_repo
  allowed_branches         = var.allowed_branches
  github_oidc_role_name    = var.github_oidc_role_name
  enable_admin_attachment  = var.enable_admin_attachment
  tags                     = local.tags
}
