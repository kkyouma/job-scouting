terraform {
  required_version = ">= 1.14.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "terraform-state-kyoumas"
    prefix = "projects/job-scouting"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Artifacts Registry Repository
resource "google_artifact_registry_repository" "artifacts_repository" {
  project       = var.project_id
  location      = var.region
  repository_id = "job-scouting-images"
  format        = "DOCKER"
  description   = "Artifacts repository for job-scouting"
}
