"""Test cases for nonhuman related features."""

# Third-Party Libraries
import pytest


class TestNonhumans:
    """Test case for nonhuman related views."""

    def test_nonhumans_view(self, client):
        """Test the nonhumans view."""
        resp = client.get("/api/nonhumans/")
        assert resp.status_code == 200

        self.check_nonhuman_properties(resp.json)

    @staticmethod
    def check_nonhuman_properties(nonhuman):
        """Check nonhuman object for expected properties."""
        if not isinstance(nonhuman, list):
            pytest.fail("expected a list")

        if nonhuman:
            if not isinstance(nonhuman[0], str):
                pytest.fail("expected a string")

            assert len(nonhuman) >= 3
