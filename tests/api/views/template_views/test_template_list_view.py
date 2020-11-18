"""TemplateListView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import template


def template_post_response():
    """Sample Post Response."""
    return {"template_uuid": "1234"}


@pytest.mark.django_db
def test_templates_view_list_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ) as mock_get_list:
        result = client.get("/api/v1/templates/")
        assert mock_get_list.called
        assert result.status_code == 200

        result = client.get("/api/v1/templates/", {"subject": "foo bar"})
        assert mock_get_list.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_templates_view_list_post(client):
    """Test Post."""
    with mock.patch(
        "api.services.TemplateService.save",
        return_value=template_post_response(),
    ) as mock_post, mock.patch(
        "api.services.TemplateService.exists",
        return_value=False,
    ) as mock_exists:
        result = client.post("/api/v1/templates/", template())
        assert mock_post.called
        assert mock_exists.called
        assert result.status_code == 201

    with mock.patch(
        "api.services.TemplateService.save",
        return_value=template_post_response(),
    ) as mock_post, mock.patch(
        "api.services.TemplateService.exists",
        return_value=True,
    ) as mock_exists:
        result = client.post("/api/v1/templates/", template())
        assert not mock_post.called
        assert mock_exists.called
        assert result.status_code == 409
