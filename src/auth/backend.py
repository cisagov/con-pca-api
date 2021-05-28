"""Backend Authentication."""
# Based on https://github.com/labd/django-cognito-jwt under MIT license
# Standard Python Libraries
import hashlib
import hmac
import logging

# Third-Party Libraries
import cognitojwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

# cisagov Libraries
from config import settings


class JSONWebTokenAuthentication(BaseAuthentication):
    """JSONWebTokenAuthentication."""

    def authenticate(self, request):
        """Authenticate Request."""
        # Gophish Authentication
        validate_resp = self.validate(request)
        if not validate_resp:
            raise exceptions.AuthenticationFailed()
        return validate_resp

    def validate(self, request):
        """Validate auth."""
        # Development Authentication
        if not settings.COGNITO_ENABLED:
            user = {"username": "developer user", "groups": {"develop"}}
            return (user, "Empty token")

        # Gophish Authentication
        gophish_resp = self.check_gophish(request)
        if gophish_resp:
            return gophish_resp

        # Local authentication
        local_resp = self.check_local_api_key(request)
        if local_resp:
            return local_resp

        # Reports Authentication
        report_resp = self.check_reports_auth(request)
        if report_resp:
            return report_resp

        jwt_resp = self.check_cognito_jwt(request)
        if jwt_resp:
            return jwt_resp

        return None

    def check_gophish(self, request):
        """Check gophish auth."""
        gp_sign = request.headers.get("X-Gophish-Signature")
        if gp_sign:
            gp_sign = gp_sign.split("=")[-1]
            digest = hmac.new(
                settings.LOCAL_API_KEY.encode(), request.body, hashlib.sha256
            ).hexdigest()
            if digest == gp_sign:
                user = {"username": "gophish", "groups": {"develop"}}
                return (user, "Empty token")

    def check_local_api_key(self, request):
        """Check local api key."""
        if (
            settings.LOCAL_API_KEY
            and get_authorization_header(request).decode() == settings.LOCAL_API_KEY
        ):
            user = {"username": "api", "groups": {"develop"}}
            return (user, "Empty token")

    def check_reports_auth(self, request):
        """Check if report authentication."""
        # Reports authentication with bearer
        if (
            settings.LOCAL_API_KEY
            and get_authorization_header(request).decode().split(" ")[-1]
            == settings.LOCAL_API_KEY
        ):
            user = {"username": "reports", "groups": {"develop"}}
            return (user, "Empty token")

    def check_cognito_jwt(self, request):
        """Check cognito JWT."""
        jwt = self.get_jwt_token(request)
        if not jwt:
            return None
        try:
            resp = cognitojwt.decode(
                jwt,
                settings.COGNITO_REGION,
                settings.COGNITO_USER_POOL_ID,
                app_client_id=settings.COGNITO_CLIENT_ID,
            )
            self.username = resp["cognito:username"]
            self.groups = resp.get("cognito:groups", [])
            return self.username, jwt
        except Exception as e:
            logging.exception(e)
            return None

    def get_authorization_header(self, request):
        """Get auth header."""
        return request.headers.get("Authorization", "")

    def get_jwt_token(self, request):
        """Get JWT from headers."""
        auth = self.get_authorization_header(request).split()
        if not auth or str(auth[0].lower()) != "bearer":
            return None
        if len(auth) != 2:
            return None
        return auth[1]
