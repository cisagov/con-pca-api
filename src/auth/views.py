"""Auth views."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging

# Third-Party Libraries
import botocore
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.utils.aws_utils import Cognito

cognito = Cognito()


class RegisterView(APIView):
    """RegisterView."""

    authentication_classes: list = []

    def post(self, request):
        """Post."""
        try:
            data = request.data.copy()
            cognito.sign_up(data["username"], data["password"], data["email"])
            return Response(status=status.HTTP_202_ACCEPTED)
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            return Response(
                e.response["Error"]["Message"], status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    """LoginView."""

    authentication_classes: list = []

    def post(self, request):
        """Post."""
        data = request.data.copy()
        now = datetime.utcnow()
        try:
            response = cognito.authenticate(data["username"], data["password"])
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            return Response(e.response["Error"]["Message"], 400)

        expires = now + timedelta(seconds=response["AuthenticationResult"]["ExpiresIn"])

        return Response(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "expires_at": expires,
                "username": data["username"],
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RefreshTokenView(APIView):
    """RefreshTokenView."""

    authentication_classes: list = []

    def post(self, request):
        """Post."""
        data = request.data.copy()
        now = datetime.utcnow()
        response = cognito.refresh(data["refreshToken"])
        expires = now + timedelta(seconds=response["AuthenticationResult"]["ExpiresIn"])
        return Response(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": data["refreshToken"],
                "expires_at": expires,
                "username": data["username"],
            }
        )
