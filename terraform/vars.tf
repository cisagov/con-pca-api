variable "env" {
  type = string
}

variable "app" {
  type = string
}

variable "region" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "image_repo" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "cycle_minutes" {
  type    = string
  default = "129600"
}

variable "monthly_minutes" {
  type    = string
  default = "43200"
}

variable "yearly_minutes" {
  type    = string
  default = "525600"
}

variable "documentdb_cluster_size" {
  type    = number
  default = 1
}

variable "documentdb_instance_class" {
  type    = string
  default = "db.r5.large"
}

variable "log_retention_days" {
  type    = number
  default = 7
}

variable "api_container_cpu" {
  type    = number
  default = 2048
}

variable "api_container_memory" {
  type    = number
  default = 4096
}

variable "lambda_tasks_memory" {
  type    = number
  default = 1024
}

variable "lambda_tasks_schedule" {
  type    = string
  default = "rate(5 minutes)"
}
