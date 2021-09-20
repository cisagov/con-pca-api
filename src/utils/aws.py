"""Aws clients."""
# Standard Python Libraries
import logging

# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError

# cisagov Libraries
from api.config import COGNITO_CLIENT_ID, COGNITO_USER_POOL_ID, SES_ASSUME_ROLE_ARN
from utils.emails import build_message


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
        resp = self.client.assume_role(
            RoleArn=role_arn, RoleSessionName=f"{service}_session"
        )

        return boto3.client(
            service,
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"],
        )


class SES(AWS):
    """SES."""

    def __init__(self):
        """Init."""
        if SES_ASSUME_ROLE_ARN:
            sts = STS()
            self.client = sts.assume_role_client("ses", SES_ASSUME_ROLE_ARN)
        else:
            super().__init__("ses")

    def send_email(
        self, source: str, to: list, subject: str, html: str, attachments=[]
    ):
        """Send email via SES."""
        try:
            message = build_message(
                subject=subject,
                from_email=source,
                bcc_recipients=to,
                html=html,
                attachments=attachments,
            )

            return self.client.send_raw_email(
                RawMessage={"Data": message},
            )
        except ClientError as e:
            logging.exception(e)
            return e.response["Error"]
