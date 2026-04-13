# ======= DATA SOURCES =======
data "google_project" "current" {
  project_id = var.project_id
}

locals {
  project_number = data.google_project.current.number
  wif_prefix     = "principalSet://iam.googleapis.com/projects/${local.project_number}/locations/global"

  wif_member = join("/", [
    local.wif_prefix,
    "workloadIdentityPools/${var.wif_pool_id}",
    "attribute.repository/${var.github_repo}",
  ])
}

# ======= WORKLOAD IDENTITY =======

resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.sa_cicd.name
  role               = "roles/iam.workloadIdentityUser"

  member = local.wif_member

}
# ======= RUNTIME =======

# (sa_runtime) can READ the Artifact Registry
resource "google_artifact_registry_repository_iam_member" "runtime_run_reader" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.artifacts_repository.name

  role   = "roles/artifactregistry.reader"
  member = "serviceAccount:${google_service_account.sa_runtime.email}"
}

# (sa_runtime) can ACCESS every secret
resource "google_secret_manager_secret_iam_member" "runtime_secret_accessor" {
  for_each = google_secret_manager_secret.env_secrets

  project   = var.project_id
  secret_id = each.value.secret_id

  role   = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.sa_runtime.email}"
}

# ======= CI/CD =======

# (sa_cicd) can PUSH images to Artifact Registry
resource "google_artifact_registry_repository_iam_member" "cicd_ar_writer" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.artifacts_repository.name

  role   = "roles/artifactregistry.writer"
  member = "serviceAccount:${google_service_account.sa_cicd.email}"
}

# (sa_cicd) can UPDATE the Cloud Run Job (deploy new revisions)
resource "google_cloud_run_v2_job_iam_member" "cicd_run_developer" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.job_scouting.name

  role   = "roles/run.developer"
  member = "serviceAccount:${google_service_account.sa_cicd.email}"
}

# (sa_cicd) can ACT AS the runtime SA (required to deploy with that SA)
resource "google_service_account_iam_member" "cicd_act_as_runtime" {
  service_account_id = google_service_account.sa_runtime.name

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${google_service_account.sa_cicd.email}"
}
