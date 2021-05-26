"""Backend Authentication Tests."""
# Standard Python Libraries
import hashlib
import hmac
import os
from unittest import mock

# Third-Party Libraries
from django.http import HttpRequest

# cisagov Libraries
from src.auth import backend

# Throughout the tests, there are "nosec" defined on multiple assertions
# This is because bandit throws B105: hardcoded_password_string error
# https://bandit.readthedocs.io/en/latest/plugins/b105_hardcoded_password_string.html
# As these are tests and these tokens are not actually hardcoded, it is fine.


def test_gophish_authenticate():
    """Test Gophish Auth."""
    request = HttpRequest()
    request._body = b'{"success": true}'
    gp_sign = hmac.new(
        os.environ["LOCAL_API_KEY"].encode(), request.body, hashlib.sha256
    ).hexdigest()
    request.headers = {"X-Gophish-Signature": f"sha256={gp_sign}"}
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"username": "gophish", "groups": {"develop"}}
    assert token == "Empty token"  # nosec


@mock.patch("config.settings.COGNITO_ENABLED", False)
def test_develop_auth():
    """Test Dev Auth."""
    request = HttpRequest()
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)

    assert user == {"username": "developer user", "groups": {"develop"}}
    assert token == "Empty token"  # nosec


@mock.patch("config.settings.COGNITO_ENABLED", True)
def test_local_auth():
    """Test Local Auth."""
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = os.environ["LOCAL_API_KEY"]
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"username": "api", "groups": {"develop"}}
    assert token == "Empty token"  # nosec


@mock.patch("config.settings.COGNITO_ENABLED", True)
def test_reports_auth():
    """Test Reports Auth."""
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = f"bearer {os.environ['LOCAL_API_KEY']}"
    auth = backend.JSONWebTokenAuthentication()
    user, token = auth.authenticate(request)
    assert user == {"username": "reports", "groups": {"develop"}}
    assert token == "Empty token"  # nosec
