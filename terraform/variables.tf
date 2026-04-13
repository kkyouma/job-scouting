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

variable "cloud_run_job_name" {
  description = "Cloud Run Job name"
  type        = string
}

variable "secret_ids" {
  description = "List of secret names to create in Secret Manager (must match .env keys)"
  type        = list(string)
}

variable "cloud_run_cpu" {
  description = "CPU limit for the Cloud Run Job container"
  type        = string
  default     = "1"
}

variable "cloud_run_memory" {
  description = "Memory limit for the Cloud Run Job container"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_timeout" {
  description = "Maximum execution time for the Cloud Run Job (e.g. 900s)"
  type        = string
  default     = "900s"
}

variable "wif_pool_id" {
  description = "Workload Identity Pool ID"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "kkyouma/job-scouting"
}
