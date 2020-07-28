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

  tags = {
    environment = "${var.env}"
    app         = "${var.app}"
  }
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

  tags = {
    environment = "${var.env}"
    app         = "${var.app}"
  }
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
  vpc_id                  = data.aws_vpc.vpc.id
  subnet_ids              = data.aws_subnet_ids.public.ids
  allowed_cidr_blocks     = ["0.0.0.0/0"]
  allowed_security_groups = [aws_security_group.api.id]
  skip_final_snapshot     = true
}

#=================================================
#  S3
#=================================================
module "s3_images" {
  source        = "github.com/cloudposse/terraform-aws-s3-bucket"
  namespace     = "${var.app}"
  stage         = "${var.env}"
  name          = "images"
  acl           = "public-read"
  sse_algorithm = "AES256"
}

resource "aws_s3_bucket" "websites" {
  bucket = "${var.app}-${var.env}-websites"
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
      "Resource": "arn:aws:s3:::${var.app}-${var.env}-websites/*"
    }
  ]
}
POLICY

  website {
    index_document = "index.html"
  }
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
# FARGATE
# ===========================
locals {
  api_container_port     = 80
  api_load_balancer_port = 8043

  environment = {
    "SECRET_KEY" : random_string.django_secret_key.result,
    "DEBUG" : 0,
    "DJANGO_ALLOWED_HOSTS" : "localhost 127.0.0.1 [::1] ${data.aws_lb.public.dns_name}",
    "DB_HOST" : module.documentdb.endpoint,
    "DB_PORT" : 27017,
    "GP_URL" : "https://${data.aws_lb.public.dns_name}:3333/"
    "PHISH_URL" : "http://${data.aws_lb.public.dns_name}/"
    "WEBHOOK_URL" : "http://${data.aws_lb.public.dns_name}:8000/api/v1/inboundwebhook/"
    "AWS_S3_IMAGE_BUCKET" : "${var.app}-${var.env}-images",
    "DEFAULT_FILE_STORAGE" : "storages.backends.s3boto3.S3Boto3Storage",
    "WORKERS" : 4,
    "COGNITO_DEPLOYMENT_MODE" : "Production",
    "COGNITO_AWS_REGION" : var.region,
    "COGNITO_USER_POOL" : element(tolist(data.aws_cognito_user_pools.users.ids), 0),
    "LOCAL_API_KEY" : random_string.local_api_key.result,
    "MONGO_TYPE" : "DOCUMENTDB",
    "REPORTS_API" : "https://${data.aws_lb.private.dns_name}:3030"
  }

  secrets = {
    "DB_USER" : aws_ssm_parameter.docdb_username.arn,
    "DB_PW" : aws_ssm_parameter.docdb_password.arn,
    "GP_API_KEY" : data.aws_ssm_parameter.gp_api_key.arn,
    "GP_SMTP_HOST" : data.aws_ssm_parameter.gp_smtp_host.arn,
    "GP_SMTP_FROM" : data.aws_ssm_parameter.gp_smtp_from.arn,
    "GP_SMTP_USER" : data.aws_ssm_parameter.gp_smtp_user.arn,
    "GP_SMTP_PASS" : data.aws_ssm_parameter.gp_smtp_pass.arn,
    "SMTP_HOST" : data.aws_ssm_parameter.smtp_host.arn,
    "SMTP_PORT" : data.aws_ssm_parameter.smtp_port.arn,
    "SMTP_PASS" : data.aws_ssm_parameter.smtp_pass.arn,
    "SMTP_FROM" : data.aws_ssm_parameter.smtp_from.arn,
    "SMTP_USER" : data.aws_ssm_parameter.smtp_user.arn,
    "COGNITO_AUDIENCE" : data.aws_ssm_parameter.client_id.arn
  }
}

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
  secrets         = local.secrets
}

module "api" {
  source    = "github.com/cisagov/fargate-service-tf-module"
  namespace = "${var.app}"
  stage     = "${var.env}"
  name      = "api"

  iam_server_cert_arn   = data.aws_iam_server_certificate.self.arn
  container_port        = local.api_container_port
  container_definition  = module.container.json
  container_name        = "pca-api"
  cpu                   = 2048
  memory                = 4096
  vpc_id                = data.aws_vpc.vpc.id
  health_check_interval = 60
  health_check_path     = "/"
  health_check_codes    = "307,202,200,404"
  load_balancer_arn     = data.aws_lb.public.arn
  load_balancer_port    = local.api_load_balancer_port
  desired_count         = 1
  subnet_ids            = data.aws_subnet_ids.private.ids
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
  vpc_id      = data.aws_vpc.vpc.id

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
