data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda"
  output_path = "${path.root}/.terraform/lambda_package.zip"
}

resource "aws_lambda_function" "translate_handler" {
  function_name = "${var.project_name}-${var.environment}-translate-handler"
  role          = var.lambda_role_arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  memory_size   = var.memory_size
  timeout       = var.timeout

  environment {
    variables = {
      REQUESTS_BUCKET  = var.requests_bucket
      RESPONSES_BUCKET = var.responses_bucket
    }
  }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_lg" {
  name              = "/aws/lambda/${aws_lambda_function.translate_handler.function_name}"
  retention_in_days = var.log_retention
  tags              = var.tags
}