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
        if not isinstance(tags, list):
            pytest.fail("expected a list")

        if tags:
            if not isinstance(tags[0], dict):
                pytest.fail("expected a dict")

            try:
                if not isinstance(tags[0]["description"], str):
                    pytest.fail("expected a string")
            except KeyError:
                pytest.fail("description property does not exist")
