"""Test cases for user related features."""

# Third-Party Libraries
import pytest


class TestUsers:
    """Test case for user related views."""

    def test_users_view(self, client):
        """Test the users view."""
        resp = client.get("/api/users/")
        assert resp.status_code == 200

        self.check_user_properties(resp.json[0])

    @staticmethod
    def check_user_properties(user):
        """Check user object for expected properties."""
        try:
            assert isinstance(user["username"], str)
        except KeyError:
            pytest.fail("username property does not exist")

        try:
            assert isinstance(user["email"], str)
        except KeyError:
            pytest.fail("email property does not exist")

        try:
            assert isinstance(user["enabled"], bool)
        except KeyError:
            pytest.fail("enabled property does not exist")
