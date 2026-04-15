# Cloud Run Job — executes the job-scouting pipeline
resource "google_cloud_run_v2_job" "job_scouting" {
  project  = var.project_id
  name     = var.cloud_run_job_name
  location = var.region

  template {
    template {
      service_account = google_service_account.sa_runtime.email

      containers {
        # image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.artifacts_repository.repository_id}/${var.cloud_run_job_name}:latest"
        image = "us-docker.pkg.dev/cloudrun/container/hello"

        # Inject every secret as an environment variable
        dynamic "env" {
          for_each = google_secret_manager_secret.env_secrets
          content {
            name = env.key # e.g. JSEARCH_API_KEY
            value_source {
              secret_key_ref {
                secret  = env.value.secret_id
                version = "latest"
              }
            }
          }
        }

        resources {
          limits = {
            cpu    = var.cloud_run_cpu
            memory = var.cloud_run_memory
          }
        }
      }

      timeout     = var.cloud_run_timeout
      max_retries = 1
    }
  }

  lifecycle {
    ignore_changes = [
      # Allow CI/CD to update the image tag without Terraform drift
      template[0].template[0].containers[0].image,
    ]
  }

  depends_on = [
    google_secret_manager_secret.env_secrets,
  ]
}

# Schedule Cloud Run Job to run every Monday to Friday at 8pm
resource "google_cloud_scheduler_job" "run_job_trigger" {
  project   = var.project_id
  name      = var.cloud_run_job_name
  schedule  = "0 20 * * 1-5"
  time_zone = "America/Santiago"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job_scouting.name}:run"

    oidc_token {
      service_account_email = google_service_account.sa_scheduler.email
    }
  }
}
