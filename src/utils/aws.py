"""Aws clients."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError

# cisagov Libraries
from api.config.environment import COGNITO_CLIENT_ID, COGNITO_USER_POOL_ID
from api.manager import UserManager
from utils.logging import setLogger

logger = setLogger(__name__)

user_manager = UserManager()


class AWS:
    """Base AWS Class."""

    def __init__(self, service):
        """Initialize client."""
        self.client = boto3.client(service_name=service)


class Cognito(AWS):
    """Cognito."""

    def __init__(self):
        """Create cognito client."""
        super().__init__("cognito-idp")

    def list_users(self):
        """List users."""
        resp = self.client.list_users(UserPoolId=COGNITO_USER_POOL_ID)["Users"]
        users = []
        for user in resp:
            email = next(
                filter(
                    lambda x: x["Name"] == "email",
                    user["Attributes"],
                )
            )["Value"]
            users.append(
                {
                    "username": user["Username"],
                    "email": email,
                    "status": user["UserStatus"],
                    "enabled": user["Enabled"],
                    "created": user["UserCreateDate"],
                    "modified": user["UserLastModifiedDate"],
                }
            )
        return users

    def delete_user(self, username):
        """Delete user."""
        return self.client.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def confirm_user(self, username):
        """Confirm user."""
        return self.client.admin_confirm_sign_up(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def sign_up(self, username, password, email):
        """Sign up user."""
        return self.client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )

    def authenticate(self, username, password):
        """Authenticate user."""
        if not user_manager.exists(parameters={"username": username}):
            user_manager.save({"username": username, "last_login": datetime.now()})
        else:
            user_manager.find_one_and_update(
                params={
                    "username": {"$eq": username},
                },
                data={"last_login": datetime.now()},
            )
        return self.client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientMetadata={
                "username": username,
                "password": password,
            },
        )

    def auto_verify_user_email(self, username: str):
        """Auto verify user email."""
        return self.client.admin_update_user_attributes(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            UserAttributes=[{"Name": "email_verified", "Value": "true"}],
        )

    def confirm_forgot_password(
        self, username: str, confirmation_code: str, password: str
    ):
        """Prompt a user to enter a confirmation code to reset a forgotten password."""
        return self.client.confirm_forgot_password(
            ClientId=COGNITO_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code,
            Password=password,
        )

    def reset_password(self, username: str):
        """Reset password by sending a confirm code to user email."""
        return self.client.admin_reset_user_password(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def refresh(self, token):
        """Refresh auth token."""
        return self.client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": token},
        )


class STS(AWS):
    """STS."""

    def __init__(self):
        """Create STS client."""
        super().__init__("sts")

    def assume_role_client(self, service, role_arn):
        """Assume Role via STS."""
        try:
            resp = self.client.assume_role(
                RoleArn=role_arn, RoleSessionName=f"{service}_session"
            )
        except ClientError as e:
            logger.error(e)
            return

        return boto3.client(
            service,
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"],
        )


class SES(AWS):
    """SES."""

    def __init__(self, assume_role_arn=None):
        """Init."""
        if assume_role_arn:
            sts = STS()
            self.client = sts.assume_role_client("ses", assume_role_arn)
        else:
            super().__init__("ses")

    def send_email(self, message):
        """Send email via SES."""
        if not self.client:
            logger.error("Error: There's an issue with the role assumed for SES")
            return None

        try:
            return self.client.send_raw_email(RawMessage={"Data": message})
        except ClientError as e:
            logger.exception(e)
            return e.response["Error"]
