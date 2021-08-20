"""Decorator utils."""
# Standard Python Libraries
from functools import wraps
from http import HTTPStatus

# Third-Party Libraries
import cognitojwt
from flask import abort, g, request

# cisagov Libraries
from api.config import (
    AWS_REGION,
    COGNITO_CLIENT_ID,
    COGNITO_USER_POOL_ID,
    COGNTIO_ENABLED,
)


class RequestAuth:
    """Authorization class for requests."""

    def __init__(self, request):
        """Initialize class with cognito settings and associated request."""
        self.request = request
        self.username = ""

    def validate(self):
        """Validate request."""
        if not COGNTIO_ENABLED:
            return True
        try:
            if self.check_cognito_jwt(request):
                return True
        except cognitojwt.exceptions.CognitoJWTException:
            return False

        return False

    def get_authorization_header(self, request):
        """Get auth header."""
        return request.headers.get("Authorization", "")

    def get_jwt_token(self, request):
        """Get JWT Token."""
        auth = self.get_authorization_header(request).split()
        if not auth or str(auth[0].lower()) != "bearer":
            return None
        if len(auth) != 2:
            return None
        return auth[1]

    def check_cognito_jwt(self, request):
        """Check if valid cognito jwt."""
        jwt = self.get_jwt_token(request)
        if not jwt:
            return False
        try:
            resp = cognitojwt.decode(
                jwt,
                AWS_REGION,
                COGNITO_USER_POOL_ID,
                app_client_id=COGNITO_CLIENT_ID,
            )
            self.username = resp["cognito:username"]
            self.groups = resp.get("cognito:groups", [])
            return self.username, jwt
        except cognitojwt.exceptions.CognitoJWTException:
            return None
        except Exception:
            return None


def auth_required(view):
    """Authorize requests."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Decorate."""
        auth = RequestAuth(request)
        if auth.validate():
            g.username = auth.username
            return view(*args, **kwargs)
        else:
            abort(HTTPStatus.UNAUTHORIZED.value)

    return decorated
