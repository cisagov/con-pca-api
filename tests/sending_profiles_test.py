"""Test cases for sending profile related features."""

# Third-Party Libraries
import pytest


class TestSendingProfiles:
    """Test case for sending profile related views."""

    def test_sending_profiles_view(self, client):
        """Test the sending profiles view."""
        resp = client.get("/api/sendingprofiles/")
        assert resp.status_code == 200

        self.check_sending_profile_properties(resp.json[0])

    def test_get_sending_profile(self, client, sending_profile):
        """Test the sending profile view."""
        sending_profile_id = sending_profile.get("_id")
        assert sending_profile_id is not None

        resp = client.get(f"/api/sendingprofile/{sending_profile_id}/")
        assert resp.status_code == 200

        self.check_sending_profile_properties(resp.json)

    @staticmethod
    def check_sending_profile_properties(sendingprofile):
        """Check sendingprofile object for expected properties."""
        try:
            if not isinstance(sendingprofile["name"], str):
                pytest.fail("expected a string")
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            if not isinstance(sendingprofile["interface_type"], str):
                pytest.fail("expected a string")
        except KeyError:
            pytest.fail("interface_type property does not exist")

        try:
            if not isinstance(sendingprofile["from_address"], str):
                pytest.fail("expected a string")
        except KeyError:
            pytest.fail("from_address property does not exist")
