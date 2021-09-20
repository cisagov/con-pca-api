"""Auth views."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging

# Third-Party Libraries
import botocore
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from utils.aws import Cognito

cognito = Cognito()


class RegisterView(MethodView):
    """RegisterView."""

    def post(self):
        """Register."""
        try:
            data = request.json
            cognito.sign_up(data["username"], data["password"], data["email"])
            return jsonify(success=True)
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            return e.response["Error"]["Message"], 400


class LoginView(MethodView):
    """LoginView."""

    def post(self):
        """Login."""
        data = request.json
        try:
            response = cognito.authenticate(data["username"], data["password"])
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            return e.response["Error"]["Message"], 400
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "expires_at": datetime.utcnow()
                + timedelta(seconds=response["AuthenticationResult"]["ExpiresIn"]),
                "username": data["username"],
            }
        )


class RefreshTokenView(MethodView):
    """RefreshTokenView."""

    def post(self):
        """Refresh token."""
        data = request.json
        response = cognito.refresh(data["refreshToken"])
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": data["refreshToken"],
                "expires_at": datetime.utcnow()
                + timedelta(seconds=response["AuthenticationResult"]["ExpiresIn"]),
                "username": data["username"],
            }
        )
