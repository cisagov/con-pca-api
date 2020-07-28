variable "env" {
  type = string
}

variable "app" {
  type    = string
  default = "con-pca"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "image_repo" {
  type    = string
  default = "780016325729.dkr.ecr.us-east-1.amazonaws.com/con-pca-api"
}

variable "image_tag" {
  type = string
}
