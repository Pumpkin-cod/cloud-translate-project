variable "github_owner" {
  description = "GitHub org/user"
  type        = string
}

variable "github_repo" {
  description = "GitHub repo name"
  type        = string
}

variable "allowed_branches" {
  description = "List of allowed branches"
  type        = list(string)
  default     = ["main"]
}

variable "github_oidc_role_name" {
  description = "Name for the GitHub OIDC role"
  type        = string
  default     = "GitHubOIDCRole"
}

variable "enable_admin_attachment" {
  description = "Whether to attach admin policy"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}