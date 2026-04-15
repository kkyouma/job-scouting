output "cicd_sa_email" {
  value = google_service_account.sa_cicd.email
}

output "job_name" {
  value = google_cloud_run_v2_job.job_scouting.name
}

output "job_uri" {
  value = google_cloud_run_v2_job.job_scouting.id
}
