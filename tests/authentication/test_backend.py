import hmac
import hashlib
import os
import time

from django.http import HttpRequest

from unittest import mock
import pytest
from rest_framework import exceptions

from src.authentication import backend


def test_gophish_authenticate():
    request = HttpRequest()
    request._body = b'{"success": true}'
    gp_sign = hmac.new(
        os.environ["LOCAL_API_KEY"].encode(), request.body, hashlib.sha256
    ).hexdigest()
    request.headers = {"X-Gophish-Signature": f"sha256={gp_sign}"}
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"username": "gophish", "groups": {"develop"}}
    assert token == "Empty token"


@mock.patch.dict(os.environ, {"COGNITO_DEPLOYMENT_MODE": "Development"})
def test_develop_auth():
    request = HttpRequest()
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)

    assert user == {"username": "developer user", "groups": {"develop"}}
    assert token == "Empty token"


@mock.patch.dict(os.environ, {"COGNITO_DEPLOYMENT_MODE": "Production"})
def test_local_auth():
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = os.environ["LOCAL_API_KEY"]
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"username": "api", "groups": {"develop"}}
    assert token == "Empty token"


@mock.patch.dict(os.environ, {"COGNITO_DEPLOYMENT_MODE": "Production"})
def test_reports_auth():
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = f"bearer {os.environ['LOCAL_API_KEY']}"
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"usuername": "reports", "groups": {"develop"}}
    assert token == "Empty token"


@mock.patch.dict(os.environ, {"COGNITO_DEPLOYMENT_MODE": "Production"})
@mock.patch(
    "authentication.validator.TokenValidator.validate",
    return_value={"exp": int(time.time()) - 1},
)
def test_expired_token(mock_validate):
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = "bearer fakejwt"
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(exceptions.AuthenticationFailed) as e:
        user, token = auth.authenticate(request)
    assert str(e.value) == "Token has expired, please log back in"


@mock.patch.dict(
    os.environ, {"COGNITO_DEPLOYMENT_MODE": "Production", "COGNITO_AUDIENCE": "good"}
)
def test_invalid_client_auth():
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = "bearer fakejwt"
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(exceptions.AuthenticationFailed) as e:
        with mock.patch(
            "authentication.validator.TokenValidator.validate",
            return_value={"exp": int(time.time()) + 10, "client_id": "bad"},
        ):
            user, token = auth.authenticate(request)
    assert str(e.value) == (
        "Client_ID does not match the applications, please"
        "ensure you are logged into the correct AWS account"
    )


@mock.patch.dict(
    os.environ, {"COGNITO_DEPLOYMENT_MODE": "Production", "COGNITO_AUDIENCE": "good"}
)
def test_cognito_group_auth():
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = "bearer fakejwt"

    with mock.patch(
        "authentication.validator.TokenValidator.validate",
        return_value={
            "exp": int(time.time()) + 10,
            "client_id": "good",
            "cognito:groups": "group",
            "username": "user",
        },
    ):
        auth = backend.JSONWebTokenAuthentication()
        user, token = auth.authenticate(request)
        assert user == {"username": "user", "groups": "group"}


def test_cognito_auth():
    os.environ["COGNITO_DEPLOYMENT_MODE"] = "Production"
    os.environ["COGNITO_AUDIENCE"] = "good"
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = "bearer fakejwt"

    with mock.patch(
        "authentication.validator.TokenValidator.validate",
        return_value={
            "exp": int(time.time()) + 10,
            "client_id": "good",
            "username": "user",
        },
    ):
        auth = backend.JSONWebTokenAuthentication()
        user, token = auth.authenticate(request)
        assert user == {"username": "user", "groups": "None"}
