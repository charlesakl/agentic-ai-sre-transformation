variable "name" { type = string }
variable "namespace" { type = string }
variable "replicas" { type = number }
variable "memory_limit" { type = string }

resource "kubernetes_deployment_v1" "workload" {
  metadata {
    name      = var.name
    namespace = var.namespace
    labels    = { app = var.name }
  }
  spec {
    replicas = var.replicas
    selector { match_labels = { app = var.name } }
    template {
      metadata { labels = { app = var.name } }
      spec {
        container {
          name  = var.name
          image = "nginx:1.27" # Placeholder image, not the demo service image
          resources {
            limits   = { memory = var.memory_limit }
            requests = { memory = "128Mi" }
          }
        }
      }
    }
  }
}
