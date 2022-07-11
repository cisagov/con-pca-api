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
        try:
            assert isinstance(logging, list)
        except KeyError:
            pytest.fail("expected a list")

        if len(logging) > 0:
            try:
                assert isinstance(logging[0], dict)
            except KeyError:
                pytest.fail("expected a dict")

            try:
                assert isinstance(logging[0]["error_message"], str)
            except KeyError:
                pytest.fail("expected a str")
