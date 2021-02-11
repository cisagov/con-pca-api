"""TemplateView Test."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import template


@pytest.mark.django_db
def test_templates_view_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.TemplateService.get",
        return_value=template(),
    ) as mock_get_single:
        result = client.get("/api/v1/template/1234/")
        assert mock_get_single.called
        assert result.status_code == 200


# def test_templates_view_patch(client, mocker):
#     """Test Patch."""
#     mocker.patch("api.services.TemplateService.update", return_value=template())
#     mocker.patch("api.services.TemplateService.get", return_value=template())
#     mocker.patch("api.utils.template.templates.validate_template", return_value=None)
#     result = client.patch(
#         "/api/v1/template/1234/", template(), content_type="application/json"
#     )
#     assert result.status_code == 202


def test_templates_view_delete(client):
    """Test Delete."""
    with mock.patch(
        "api.services.TemplateService.delete",
        return_value=template(),
    ) as mock_delete:
        result = client.delete("/api/v1/template/1234/")
        assert mock_delete.called
        assert result.status_code == 200
