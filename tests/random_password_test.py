"""Test cases for random password related features."""

# Third-Party Libraries
import pytest


class TestRandomPassword:
    """Test case for random password related views."""

    def test_random_password_view(self, client):
        """Test the randompassword view."""
        resp = client.get("/api/util/randompassword/")
        assert resp.status_code == 200

        self.check_random_password_properties(resp.json)

    @staticmethod
    def check_random_password_properties(randompassword):
        """Check random password object for expected properties."""
        if not isinstance(randompassword, dict):
            pytest.fail("expected a dict")

        try:
            if not isinstance(randompassword["password"], str):
                pytest.fail("expected a str")
        except KeyError:
            pytest.fail("password property does not exist")
