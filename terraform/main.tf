terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Example only. A real OpenShift cluster connection is deliberately not configured.
module "customer_profile" {
  source       = "./modules/openshift_workload"
  name         = "customer-profile"
  namespace    = "sre-demo"
  replicas     = 3
  memory_limit = "256Mi"
}
