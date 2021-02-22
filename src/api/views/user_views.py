"""User Views."""
# Third-Party Libraries
import boto3
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from config.settings import COGNITO_USER_POOL

cognito = boto3.client("cognito-idp")


class UsersView(APIView):
    """UsersView."""

    def get(self, request):
        """Get."""
        return Response(cognito.list_users(UserPoolId=COGNITO_USER_POOL)["Users"])


class UserView(APIView):
    """UserView."""

    def delete(self, request, username):
        """Delete."""
        return Response(
            cognito.admin_delete_user(UserPoolId=COGNITO_USER_POOL, Username=username)
        )


class UserConfirmView(APIView):
    """UserConfirmView."""

    def get(self, request, username):
        """Get."""
        return Response(
            cognito.admin_confirm_sign_up(
                UserPoolId=COGNITO_USER_POOL, Username=username
            )
        )
