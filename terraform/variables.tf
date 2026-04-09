variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "sa_cicd_name" {
  description = "CI/CD Service Account name"
  type        = string
}

variable "sa_runtime_name" {
  description = "Runtime Service Account name"
  type        = string
}
