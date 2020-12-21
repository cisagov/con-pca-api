"""Template StopView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import subscription, template


@mock.patch("api.services.CampaignService.get_list", return_value=[])
@mock.patch("api.services.TemplateService.get", return_value=template())
@mock.patch("api.services.TemplateService.update", return_value=template())
@mock.patch(
    "api.utils.subscription.actions.stop_subscription", return_value=subscription()
)
@pytest.mark.django_db
def test_templates_view_stop_get(
    mock_stop, mock_update, mock_get_template, mock_get_list, client
):
    """Test Get."""
    result = client.get("/api/v1/template/stop/1234/")
    assert mock_get_list.called
    assert mock_get_template.called
    assert mock_update.called

    assert result.status_code == 202
