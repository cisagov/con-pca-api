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
        try:
            assert isinstance(randompassword, dict)
        except KeyError:
            pytest.fail("expected a dict")

        try:
            assert isinstance(randompassword["password"], str)
        except KeyError:
            pytest.fail("expected a str")
