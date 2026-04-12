# One Secret Manager secret per environment variable
resource "google_secret_manager_secret" "env_secrets" {
  for_each = toset(var.secret_ids)

  project   = var.project_id
  secret_id = each.key

  replication {
    auto {}
  }

  labels = {
    app = "job-scouting"
  }
}
