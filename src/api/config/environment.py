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
DELAY_MINUTES = int(os.environ.get("DELAY_MINUTES", 3))
EMAIL_MINUTES = int(os.environ.get("EMAIL_MINUTES", 1))
TASK_MINUTES = int(os.environ.get("TASK_MINUTES", 5))

# https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html
API_HOST = os.environ.get("API_HOST", "0.0.0.0")  # nosec
API_PORT = os.environ.get("API_PORT", 5000)

# about
DEPLOYED_DATE = os.environ.get("DEPLOYED_DATE")
API_COMMIT_ID = os.environ.get("API_COMMIT_ID")
UI_COMMIT_ID = os.environ.get("UI_COMMIT_ID")

if os.environ.get("PYTESTING"):
    DB = mongomock.MongoClient().db
else:
    DB = get_db()

# about
DEPLOYED_DATE = os.environ.get("DEPLOYED_DATE")
API_COMMIT_ID = os.environ.get("API_COMMIT_ID")
UI_COMMIT_ID = os.environ.get("UI_COMMIT_ID")
