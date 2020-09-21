# ===========================
# DOCDB CREDS
# ===========================
resource "random_string" "docdb_username" {
  length  = 8
  number  = false
  special = false
  upper   = false
}

resource "aws_ssm_parameter" "docdb_username" {
  name        = "/${var.env}/${var.app}/api/docdb/username/master"
  description = "The username for document db"
  type        = "SecureString"
  value       = random_string.docdb_username.result
}

resource "random_password" "docdb_password" {
  length           = 32
  special          = true
  override_special = "!_#&"
}

resource "aws_ssm_parameter" "docdb_password" {
  name        = "/${var.env}/${var.app}/api/docdb/password/master"
  description = "The password for document db"
  type        = "SecureString"
  value       = random_password.docdb_password.result
}


# ===========================
# DOCUMENT DB
# ===========================
module "documentdb" {
  source                  = "github.com/cloudposse/terraform-aws-documentdb-cluster"
  stage                   = "${var.env}"
  name                    = "${var.env}-${var.app}-docdb"
  cluster_size            = 1
  master_username         = random_string.docdb_username.result
  master_password         = random_password.docdb_password.result
  instance_class          = "db.r5.large"
  vpc_id                  = var.vpc_id
  subnet_ids              = var.public_subnet_ids
  allowed_cidr_blocks     = ["0.0.0.0/0"]
  allowed_security_groups = [aws_security_group.api.id]
  skip_final_snapshot     = true
}

#=================================================
#  S3
#=================================================
resource "aws_s3_bucket" "images" {
  bucket = "${var.app}-${var.env}-template-images"
  acl    = "public-read"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Public",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.app}-${var.env}-template-images/*"
    }
  ]
}
POLICY
}


# ===========================
# APP CREDENTIALS
# ===========================
resource "random_string" "django_secret_key" {
  length  = 32
  number  = false
  special = false
  upper   = true
}

resource "random_string" "local_api_key" {
  length  = 32
  number  = false
  special = false
  upper   = true
}

resource "random_string" "basic_auth_username" {
  length  = 8
  number  = false
  special = false
  upper   = false
}

resource "random_password" "basic_auth_password" {
  length           = 32
  number           = true
  special          = false
  override_special = "!_#&"
}

# ===========================
# BROWSERLESS
# ===========================
module "browserless" {
  source    = "github.com/cisagov/fargate-browserless-tf-module"
  region    = var.region
  namespace = var.app
  stage     = var.env
  name      = "browserless"

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids
  lb_port    = 3000
}

# ===========================
# API FARGATE
# ===========================
module "container" {
  source    = "github.com/cisagov/fargate-container-def-tf-module"
  namespace = var.app
  stage     = var.env
  name      = "api"

  container_name  = "pca-api"
  container_image = "${var.image_repo}:${var.image_tag}"
  container_port  = local.api_container_port
  region          = var.region
  log_retention   = 7
  environment     = local.environment
}

data "aws_iam_policy_document" "api" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]

    resources = [
      data.aws_ssm_parameter.ses_assume_role_arn.value
    ]
  }
}

module "api" {
  source    = "github.com/cisagov/fargate-service-tf-module"
  namespace = "${var.app}"
  stage     = "${var.env}"
  name      = "api"

  https_cert_arn        = data.aws_acm_certificate.cert.arn
  container_port        = local.api_container_port
  container_definition  = module.container.json
  container_name        = "pca-api"
  cpu                   = 2048
  memory                = 4096
  vpc_id                = var.vpc_id
  health_check_interval = 60
  health_check_path     = "/"
  health_check_codes    = "307,202,200,404"
  iam_policy_document   = data.aws_iam_policy_document.api.json
  load_balancer_arn     = data.aws_lb.public.arn
  load_balancer_port    = local.api_load_balancer_port
  desired_count         = 1
  subnet_ids            = var.private_subnet_ids
  security_group_ids    = [aws_security_group.api.id]
}

# Need an http listener in order to get webhooks to work from gophish
# There is no way to specify for gophish to not verify cert.
# Once we have good certs, can remove this.
resource "aws_lb_listener" "api_http" {
  load_balancer_arn = data.aws_lb.public.arn
  port              = 8000
  protocol          = "HTTP"

  default_action {
    target_group_arn = module.api.target_group_arn
    type             = "forward"
  }
}

# ===========================
# SECURITY GROUP
# ===========================
resource "aws_security_group" "api" {
  name        = "${var.app}-${var.env}-api-alb"
  description = "Allow traffic for api from alb"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow container port from ALB"
    from_port       = local.api_container_port
    to_port         = local.api_container_port
    protocol        = "tcp"
    security_groups = [data.aws_security_group.alb.id]
    self            = true
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    "Name" = "${var.app}-${var.env}-api-alb"
  }
}
