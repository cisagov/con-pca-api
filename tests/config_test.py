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
        try:
            assert isinstance(config, dict)
        except KeyError:
            pytest.fail("expected a dict")
            
        try:
            assert isinstance(config["REPORTING_FROM_ADDRESS"], str)
        except KeyError:
            pytest.fail("expected a str")


