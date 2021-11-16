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
            cognito.auto_verify_user_email(username=data["username"])
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
            return e.response["Error"]["Message"], 403
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
        try:
            response = cognito.refresh(data["refreshToken"])
        except botocore.exceptions.ClientError as e:
            return e.response["Error"]["Message"], 403
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": data["refreshToken"],
                "expires_at": datetime.utcnow()
                + timedelta(seconds=response["AuthenticationResult"]["ExpiresIn"]),
                "username": data["username"],
            }
        )


class ResetPasswordView(MethodView):
    """Reset User Password."""

    def post(self, username):
        """Enter a New Password and Email Confirmation Code."""
        post_data = request.json

        try:
            cognito.confirm_forgot_password(
                username=username,
                confirmation_code=post_data["confirmation_code"],
                password=post_data["password"],
            )
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            return e.response["Error"]["Message"], 400
        return jsonify({"success": "User password has been reset."}), 200

    def get(self, username):
        """Trigger a Password Reset."""
        try:
            cognito.reset_password(username=username)
        except botocore.exceptions.ClientError as e:
            logging.exception(e)
            try:
                cognito.auto_verify_user_email(username=username)
                cognito.reset_password(username=username)
            except botocore.exceptions.ClientError as e:
                return e.response["Error"]["Message"], 400
        return jsonify({"success": "An email with a reset code has been sent."}), 200
