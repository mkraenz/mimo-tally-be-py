terraform {
  required_version = ">= 1.12"
  required_providers {
    google = ">= 6.37.0"
  }

}

provider "google" {
  project     = "mimo-tally-2025"
  region      = "europe-west1"
  zone        = "europe-west1-c"
  default_labels = {
    environment = "development"
  }
  add_terraform_attribution_label = true
}

# resource "google_compute_network" "default" {
#   name                    = "mimo-tally-network"
#   auto_create_subnetworks = false
# }

# resource "google_storage_bucket" "mimo_tally_bucket_test" {
#     name = "mimo-tally-bucket-test"
#     location = "EU"
# }
