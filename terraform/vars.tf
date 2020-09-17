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
