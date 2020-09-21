locals {
  api_container_port     = 80
  api_load_balancer_port = 8043

  environment = {
    "SECRET_KEY" : random_string.django_secret_key.result,
    "DEBUG" : 0,
    "DJANGO_ALLOWED_HOSTS" : "localhost 127.0.0.1 [::1] ${data.aws_lb.public.dns_name} ${var.domain_name}",
    "DB_HOST" : module.documentdb.endpoint,
    "DB_PORT" : 27017,
    "GP_URL" : "https://${var.domain_name}:3333/"
    "PHISH_URL" : "http://${var.domain_name}/"
    "WEBHOOK_URL" : "http://${var.domain_name}:8000/api/v1/inboundwebhook/"
    "AWS_S3_IMAGE_BUCKET" : aws_s3_bucket.images.id,
    "DEFAULT_FILE_STORAGE" : "storages.backends.s3boto3.S3Boto3Storage",
    "WORKERS" : 4,
    "COGNITO_DEPLOYMENT_MODE" : "Production",
    "COGNITO_AWS_REGION" : var.region,
    "COGNITO_USER_POOL" : element(tolist(data.aws_cognito_user_pools.users.ids), 0),
    "LOCAL_API_KEY" : random_string.local_api_key.result,
    "MONGO_TYPE" : "DOCUMENTDB",
    "REPORTS_ENDPOINT" : "https://${var.domain_name}",
    "BROWSERLESS_ENDPOINT" : module.browserless.lb_dns_name,
    "EXTRA_BCC_EMAILS" : "william.martin@inl.gov",
    "USE_SES" : 1,
    "TASKS_CRONTAB" : "*/5 * * * *",
    "DEFAULT_X_GOPHISH_CONTACT": "vulnerability@cisa.dhs.gov",
    "CYCLE_MINUTES": var.cycle_minutes,
    "MONTHLY_MINUTES": var.monthly_minutes,
    "YEARLY_MINUTES": var.yearly_minutes,
    "DB_USER" : aws_ssm_parameter.docdb_username.value,
    "DB_PW" : aws_ssm_parameter.docdb_password.value,
    "GP_API_KEY" : data.aws_ssm_parameter.gp_api_key.value,
    "GP_SMTP_HOST" : data.aws_ssm_parameter.gp_smtp_host.value,
    "GP_SMTP_FROM" : data.aws_ssm_parameter.gp_smtp_from.value,
    "GP_SMTP_USER" : data.aws_ssm_parameter.gp_smtp_user.value,
    "GP_SMTP_PASS" : data.aws_ssm_parameter.gp_smtp_pass.value,
    "SMTP_HOST" : data.aws_ssm_parameter.smtp_host.value,
    "SMTP_PORT" : data.aws_ssm_parameter.smtp_port.value,
    "SMTP_PASS" : data.aws_ssm_parameter.smtp_pass.value,
    "SMTP_FROM" : data.aws_ssm_parameter.smtp_from.value,
    "SMTP_USER" : data.aws_ssm_parameter.smtp_user.value,
    "COGNITO_AUDIENCE" : data.aws_ssm_parameter.client_id.value,
    "SES_ASSUME_ROLE_ARN" : data.aws_ssm_parameter.ses_assume_role_arn.value
  }
}