"""Test cases for logging related features."""

# Third-Party Libraries
import pytest


class TestLogging:
    """Test case for logging related views."""

    def test_logging_view(self, client):
        """Test the logging view."""
        resp = client.get("/api/logging/")
        assert resp.status_code == 200

        self.check_logging_properties(resp.json)

    @staticmethod
    def check_logging_properties(logging):
        """Check logging object for expected properties."""
        if not isinstance(logging, list):
            pytest.fail("expected a list")

        if logging:
            if not isinstance(logging[0], dict):
                pytest.fail("expected a dict")

            try:
                if not isinstance(logging[0]["error_message"], str):
                    pytest.fail("expected a str")
            except KeyError:
                pytest.fail("error_message property does not exist")
