"""Test cases for template related features."""

# Third-Party Libraries
import pytest

class TestTemplates:
    """Test case for template related views."""

    def test_templates_view(self, client):
        """Test the templates view."""
        resp = client.get("/api/templates/")
        assert resp.status_code == 200

        self.check_template_properties(resp.json[0])

    def test_get_template(self, client, template):
        """Test the template view."""
        template_id = template.get("_id")
        assert template_id is not None

        resp = client.get(f"/api/template/{template_id}")
        assert resp.status_code == 200

        self.check_template_properties(resp.json)

    @staticmethod
    def check_template_properties(template):
        """Check template object for expected properties."""
        try:
            assert isinstance(template["name"], str)
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            assert template["created_by"] == "bot"
        except KeyError:
            pytest.fail("created_by property does not exist")

        try:
            assert isinstance(template["retired"], bool)
        except KeyError:
            pytest.fail("retired property does not exist")

        try:
            assert isinstance(template["indicators"], dict)
            assert len(template["indicators"]) == 4
        except KeyError:
            pytest.fail("indicators property does not exist")
