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
    # Test successful delete
    with mock.patch(
        "api.services.TemplateService.delete",
        return_value=template(),
    ) as mock_delete, mock.patch(
        "api.services.CampaignService.exists", return_value=False
    ), mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[
            {
                "templates_selected": {
                    "low": ["1", "2"],
                    "moderate": ["3, 4"],
                    "high": ["5", "6"],
                }
            }
        ],
    ), mock.patch(
        "api.services.TemplateService.get", return_value={"retired": True}
    ):
        result = client.delete("/api/v1/template/1234/")
        mock_delete.assert_called
        assert result.status_code == 200

    # Test unretired template
    with mock.patch(
        "api.services.TemplateService.get", return_value={"retired": False}
    ):
        result = client.delete("/api/v1/template/1234/")
        assert result.data == {"error": "You must retire the template first"}
        mock_delete.assert_not_called
        assert result.status_code == 400

    # Test template used in campaign
    with mock.patch(
        "api.services.TemplateService.delete",
        return_value=template(),
    ) as mock_delete, mock.patch(
        "api.services.TemplateService.get", return_value={"retired": True}
    ), mock.patch(
        "api.services.CampaignService.exists", return_value=True
    ):
        result = client.delete("/api/v1/template/1234/")
        assert result.data == {
            "error": "This template can not be deleted, it is associated with subscriptions."
        }
        mock_delete.assert_not_called
        assert result.status_code == 400

    # Test template in subscription
    with mock.patch(
        "api.services.TemplateService.delete",
        return_value=template(),
    ) as mock_delete, mock.patch(
        "api.services.CampaignService.exists", return_value=False
    ), mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[
            {
                "templates_selected": {
                    "low": ["1", "2"],
                    "moderate": ["3, 4"],
                    "high": ["1234"],
                }
            }
        ],
    ), mock.patch(
        "api.services.TemplateService.get", return_value={"retired": True}
    ):
        result = client.delete("/api/v1/template/1234/")
        assert result.data == {
            "error": "This template cannot be deleted, it is assocated with subscriptions."
        }
        mock_delete.assert_not_called
        assert result.status_code == 400
