"""Test cases for config related features."""

# Third-Party Libraries
import pytest


class TestConfig:
    """Test case for config related views."""

    def test_config_view(self, client):
        """Test the config view."""
        resp = client.get("/api/config/")
        assert resp.status_code == 200

        self.check_config_properties(resp.json)

    @staticmethod
    def check_config_properties(config):
        """Check config object for expected properties."""
        if not isinstance(config, dict):
            pytest.fail("expected a dict")
