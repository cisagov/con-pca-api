"""Environment variables."""
# Standard Python Libraries
import os  # aws

# Third-Party Libraries
import mongomock

from .db import get_db

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION

# cognito
COGNTIO_ENABLED = bool(int(os.environ.get("AWS_COGNITO_ENABLED", 0)))
COGNITO_DEFAULT_ADMIN = bool(int(os.environ.get("AWS_DEFAULT_USER_TO_ADMIN", 0)))
COGNITO_ADMIN_GROUP = os.environ.get("AWS_COGNITO_ADMIN_GROUP_NAME")
COGNITO_CLIENT_ID = os.environ.get("AWS_COGNITO_USER_POOL_CLIENT_ID")
COGNITO_USER_POOL_ID = os.environ.get("AWS_COGNITO_USER_POOL_ID")

# application config settings
EMAIL_MINUTES = int(os.environ.get("EMAIL_MINUTES", 1))
TASK_MINUTES = int(os.environ.get("TASK_MINUTES", 5))
FAILED_EMAIL_MINUTES = int(os.environ.get("FAILED_EMAIL_MINUTES", 1440))

# Mailgun API
MAILGUN_API_KEY = str(os.environ.get("MAILGUN_API_KEY"))

# Archival Email Address
ARCHIVAL_EMAIL_ADDRESS = str(os.environ.get("ARCHIVAL_EMAIL_ADDRESS"))

# https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html
API_HOST = os.environ.get("API_HOST", "0.0.0.0")  # nosec
API_PORT = int(os.environ.get("API_PORT", 5000))

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# About
DEPLOYED_DATE = os.environ.get("DEPLOYED_DATE")
API_COMMIT_ID = os.environ.get("API_COMMIT_ID")
UI_COMMIT_ID = os.environ.get("UI_COMMIT_ID")

# Unit tests
TESTING = int(os.environ.get("TESTING", 0))
if TESTING:
    DB = mongomock.MongoClient().db
else:
    DB = get_db()

# about
DEPLOYED_DATE = os.environ.get("DEPLOYED_DATE")
API_COMMIT_ID = os.environ.get("API_COMMIT_ID")
UI_COMMIT_ID = os.environ.get("UI_COMMIT_ID")
