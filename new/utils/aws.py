"""Aws clients."""
# Third-Party Libraries
import boto3

# cisagov Libraries
from api.config import COGNITO_CLIENT_ID, COGNITO_USER_POOL_ID


class AWS:
    """Base AWS Class."""

    client = None

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
