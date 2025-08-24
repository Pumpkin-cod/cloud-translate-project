resource "aws_s3_bucket" "requests" {
  bucket = var.requests_bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket" "responses" {
  bucket = var.responses_bucket_name
  tags   = var.tags
}

# Block public access
resource "aws_s3_bucket_public_access_block" "requests" {
  bucket                  = aws_s3_bucket.requests.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "responses" {
  bucket                  = aws_s3_bucket.responses.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning
resource "aws_s3_bucket_versioning" "requests" {
  bucket = aws_s3_bucket.requests.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "responses" {
  bucket = aws_s3_bucket.responses.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Default encryption (SSE-S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "requests" {
  bucket = aws_s3_bucket.requests.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "responses" {
  bucket = aws_s3_bucket.responses.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bucket policies
data "aws_iam_policy_document" "s3_requests_policy" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = [
      aws_s3_bucket.requests.arn,
      "${aws_s3_bucket.requests.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
  statement {
    sid     = "DenyUnEncryptedObjectUploads"
    effect  = "Deny"
    actions = ["s3:PutObject"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = ["${aws_s3_bucket.requests.arn}/*"]
    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["AES256"]
    }
  }
}

resource "aws_s3_bucket_policy" "requests" {
  bucket = aws_s3_bucket.requests.id
  policy = data.aws_iam_policy_document.s3_requests_policy.json
}

data "aws_iam_policy_document" "s3_responses_policy" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = [
      aws_s3_bucket.responses.arn,
      "${aws_s3_bucket.responses.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
  statement {
    sid     = "DenyUnEncryptedObjectUploads"
    effect  = "Deny"
    actions = ["s3:PutObject"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = ["${aws_s3_bucket.responses.arn}/*"]
    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["AES256"]
    }
  }
}

resource "aws_s3_bucket_policy" "responses" {
  bucket = aws_s3_bucket.responses.id
  policy = data.aws_iam_policy_document.s3_responses_policy.json
}