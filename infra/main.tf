terraform {
  required_version = ">= 1.12"
  required_providers {
    google = ">= 6.37.0"
  }
}

provider "google" {
  project = "mimo-tally-2025"
  region  = "europe-west1"
  zone    = "europe-west1-c"
  default_labels = {
    environment = "development"
  }
  add_terraform_attribution_label = true
}

############### Variables for the Cloud Run service ################

variable "postgres_server" {
  type = string
}
variable "postgres_port" {
  type = string
}
variable "postgres_db" {
  type = string
}
variable "postgres_user" {
  type = string
}
variable "postgres_password" {
  type      = string
  sensitive = true
}


# # just for testing that tf apply works
# resource "google_storage_bucket" "mimo_tally_bucket_test" {
#     name = "mimo-tally-bucket-test"
#     location = "EU"
# }

################ Container Image Registry ################

resource "google_artifact_registry_repository" "image-repository" {
  location      = "europe-west1"
  repository_id = "mimo-tally-repo"
  description   = "Mimo Tally Artifact Registry Repository"
  format        = "DOCKER"
}

################ Publicly accessible Cloud Run service ################

resource "google_cloud_run_v2_service" "mimo_tally_python_service" {
  name                = "cloudrun-service"
  location            = "europe-west1"
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {

    containers {
      image = "europe-west1-docker.pkg.dev/mimo-tally-2025/mimo-tally-repo/mimo-tally-py-backend:latest"
      ports {
        container_port = 8000
      }
      resources {
        limits = {
          cpu    = "2"
          memory = "1024Mi"
        }
      }
      env {
        name  = "ENVIRONMENT"
        value = "staging"
      }
      env {
        name  = "PROJECT_NAME"
        value = "Mimo Tally API"
      }
      env {
        name = "BACKEND_CORS_ORIGINS"
        value = "https://tally.kraenz.eu"
      }
      env {
        name  = "POSTGRES_SERVER"
        value = var.postgres_server
      }
      env {
        name  = "POSTGRES_PORT"
        value = var.postgres_port
      }
      env {
        name  = "POSTGRES_DB"
        value = var.postgres_db
      }
      env {
        name  = "POSTGRES_USER"
        value = var.postgres_user
      }
      # TODO this should really be an encrypted secret e.g. in GCP Secret Manager
      env {
        name  = "POSTGRES_PASSWORD"
        value = var.postgres_password
      }
      env {
        name  = "CLERK_DOMAIN"
        value = "clerk.tally.kraenz.eu"
      }
      env {
        name  = "CLERK_AUDIENCE"
        value = "FAKE"
      }
      env {
        name  = "CLERK_ISSUER"
        value = "https://clerk.tally.kraenz.eu"
      }
      env {
        name = "INSECURE_SKIP_JWT_EXPIRATION_CHECK"
        # TODO only for testing
        value = "true"
      }
    }
  }
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_v2_service.mimo_tally_python_service.location
  project  = google_cloud_run_v2_service.mimo_tally_python_service.project
  service  = google_cloud_run_v2_service.mimo_tally_python_service.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

# TODO connectivity from cloud run to cloud sql instance. But I guess that's for a different time. I'll just quickly use railway with a public postgres instance for now + env vars
# resource "google_sql_database" "database" {
#   name     = "mimo-tally-py-db"
#   instance = google_sql_database_instance.sql_db_instance.name
# }

# no backups, no replication, no nothing. obviously not for production use
# resource "google_sql_database_instance" "sql_db_instance" {
#   name             = "mimo-tally-py-db-instance"
#   region           = "europe-west1"
#   database_version = "POSTGRES_15"
#   settings {
#     tier = "db-f1-micro"
#   }

#   deletion_protection = false # set to true in production
# }
