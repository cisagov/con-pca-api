"""
Setting.py.

Here we set all setting needed for djnago apps within this repo.
"""
# Standard Python Libraries
import os

from socket import gethostname, gethostbyname

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]"
).split()

try:
    ALLOWED_HOSTS.append(gethostname())
    ALLOWED_HOSTS.append(gethostbyname(gethostname()))
except Exception:
    print("Error getting hostname. Probably running in AWS.")

CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = [
#     "http://localhost:4200",
#     "https://localhost:3333",
#     "http://localhost:8080",
# ]

DB_CONFIG = {
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PW": os.getenv("DB_PW"),
    "DB_PORT": os.getenv("DB_PORT"),
}

# Cognito
# Determine deployment mode, default ot prod
COGNITO_DEPLOYMENT_MODE = os.getenv("COGNITO_DEPLOYMENT_MODE")
print(COGNITO_DEPLOYMENT_MODE)
if COGNITO_DEPLOYMENT_MODE != "Development":
    COGNITO_DEPLOYMENT_MODE = "Production"
COGNITO_AWS_REGION = os.getenv("COGNITO_AWS_REGION")
COGNITO_USER_POOL = os.getenv("COGNITO_USER_POOL")
COGNITO_AUDIENCE = os.getenv("COGNITO_AUDIENCE")
COGNITO_PUBLIC_KEYS_CACHING_ENABLED = True
COGNITO_PUBLIC_KEYS_CACHING_TIMEOUT = 60 * 60  # One hour caching, default is 300s

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_smtp_ssl",
    "corsheaders",
    "storages",
    # third party
    "rest_framework",
    "drf_yasg",
    # local
    "authentication",
    "reports",
    "api",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)s] [%(asctime)s] [%(pathname)s - %(funcName)s - %(lineno)d] %(message)s",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Email
# Email Settings for EMAIL_BACKEND
EMAIL_HOST = os.environ.get("SMTP_HOST", "")
EMAIL_HOST_USER = os.environ.get("SMTP_USER")
EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASS")
SERVER_EMAIL = os.environ.get("SMTP_FROM")
SES_ASSUME_ROLE_ARN = os.environ.get("SES_ASSUME_ROLE_ARN")
USE_SES = int(os.environ.get("USE_SES", default=0))

EXTRA_BCC_EMAILS = os.environ.get("EXTRA_BCC_EMAILS", [])
if EXTRA_BCC_EMAILS:
    EXTRA_BCC_EMAILS = EXTRA_BCC_EMAILS.split(",")

if DEBUG == 0:
    # Note: in prod, Port must be 465 to use SSL
    EMAIL_PORT = 465
    EMAIL_BACKEND = "django_smtp_ssl.SSLEmailBackend"
    EMAIL_USE_SSL = True
else:
    EMAIL_PORT = os.environ.get("SMTP_PORT", 587)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_USE_TLS = True

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "authentication.backend.JSONWebTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# Reports
REPORTS_ENDPOINT = os.environ.get("REPORTS_ENDPOINT", "pca-web:4200")
BROWSERLESS_ENDPOINT = os.environ.get("BROWSERLESS_ENDPOINT", "pca-browserless:3000")

# GoPhish
GP_URL = os.environ.get("GP_URL", "")
GP_API_KEY = os.environ.get("GP_API_KEY", "")
PHISH_URL = os.environ.get("PHISH_URL", "")

# AWS
DEFAULT_FILE_STORAGE = os.environ.get("DEFAULT_FILE_STORAGE")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_STORAGE_BUCKET_IMAGES_NAME = os.environ.get("AWS_STORAGE_BUCKET_IMAGES_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = False

# API Key for running local scripts
LOCAL_API_KEY = os.environ.get("LOCAL_API_KEY")
