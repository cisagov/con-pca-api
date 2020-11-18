"""Template StopView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import subscription, template


@pytest.mark.django_db
def test_templates_view_stop_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[],
    ) as mock_get_sub_list, mock.patch(
        "api.services.TemplateService.get",
        return_value=template(),
    ) as mock_get_template, mock.patch(
        "api.services.TemplateService.update",
        return_value=template(),
    ) as mock_update_template, mock.patch(
        "api.utils.subscription.actions.stop_subscription",
        return_value=subscription(),
    ):
        result = client.get("/api/v1/template/stop/1234/")
        assert mock_get_sub_list.called
        assert mock_get_template.called
        assert mock_update_template.called

        assert result.status_code == 202
