resource "google_service_account" "sa_cicd" {
  project      = var.project_id
  account_id   = var.sa_cicd_name
  display_name = "CI/CD service account"
}

resource "google_service_account" "sa_runtime" {
  project      = var.project_id
  account_id   = var.sa_runtime_name
  display_name = "Runtime service account"
}
