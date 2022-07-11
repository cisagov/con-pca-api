"""Test cases for tags related features."""

# Third-Party Libraries
import pytest


class TestTags:
    """Test case for tags related views."""

    def test_tags_view(self, client):
        """Test the tags view."""
        resp = client.get("/api/tags/")
        assert resp.status_code == 200

        self.check_tags_properties(resp.json)

    @staticmethod
    def check_tags_properties(tags):
        """Check tags object for expected properties."""
        try:
            assert isinstance(tags, list)
        except KeyError:
            pytest.fail("expected a list")

        try:
            assert isinstance(tags[0], dict)
        except KeyError:
            pytest.fail("expected a dict")

        try:
            assert isinstance(tags[0]["description"], str)
        except KeyError:
            pytest.fail("expected a str")
