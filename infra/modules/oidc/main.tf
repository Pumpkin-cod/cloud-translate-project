resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list   = ["sts.amazonaws.com"]
  thumbprint_list  = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

locals {
  github_subs = [for b in var.allowed_branches : "repo:${var.github_owner}/${var.github_repo}:ref:refs/heads/${b}"]
}

data "aws_iam_policy_document" "github_oidc_trust" {
  statement {
    sid     = "GitHubOIDCTrust"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.github_subs
    }
  }
}

resource "aws_iam_role" "github_oidc_role" {
  name               = var.github_oidc_role_name
  assume_role_policy = data.aws_iam_policy_document.github_oidc_trust.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "admin_attach" {
  count      = var.enable_admin_attachment ? 1 : 0
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

data "aws_iam_policy_document" "least_priv" {
  statement {
    sid       = "S3"
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = ["*"]
  }
  statement {
    sid       = "Lambda"
    effect    = "Allow"
    actions   = ["lambda:*"]
    resources = ["*"]
  }
  statement {
    sid       = "ApiGwV2"
    effect    = "Allow"
    actions   = ["apigateway:*"]
    resources = ["*"]
  }
  statement {
    sid       = "Translate"
    effect    = "Allow"
    actions   = ["translate:*"]
    resources = ["*"]
  }
  statement {
    sid       = "LogsCW"
    effect    = "Allow"
    actions   = ["logs:*", "cloudwatch:*"]
    resources = ["*"]
  }
  statement {
    sid       = "SNS"
    effect    = "Allow"
    actions   = ["sns:*"]
    resources = ["*"]
  }
  statement {
    sid    = "IAMForProject"
    effect = "Allow"
    actions = [
      "iam:CreateRole","iam:DeleteRole","iam:PassRole","iam:GetRole",
      "iam:PutRolePolicy","iam:DeleteRolePolicy","iam:AttachRolePolicy","iam:DetachRolePolicy",
      "iam:CreatePolicy","iam:DeletePolicy","iam:GetPolicy","iam:GetPolicyVersion",
      "iam:CreatePolicyVersion","iam:DeletePolicyVersion","iam:ListAttachedRolePolicies","iam:ListRolePolicies"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "least_priv" {
  count  = var.enable_admin_attachment ? 0 : 1
  name   = "${var.github_oidc_role_name}-least-priv"
  policy = data.aws_iam_policy_document.least_priv.json
}

resource "aws_iam_role_policy_attachment" "least_priv_attach" {
  count      = var.enable_admin_attachment ? 0 : 1
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.least_priv[0].arn
}