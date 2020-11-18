"""SubscriptionListView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import campaign, subscription


@pytest.mark.django_db
def test_subscription_view_list_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ) as mock_get_list, mock.patch(
        "api.services.CampaignService.get_list",
        return_value=[campaign()],
    ) as mock_get_campaigns_list:
        result = client.get("/api/v1/subscriptions/")
        assert mock_get_list.called
        assert result.status_code == 200

        result = client.get(
            "/api/v1/subscriptions/",
            {"archived": "true", "template": "1234", "dhs_contact": "1234"},
        )
        assert mock_get_list.called
        assert mock_get_campaigns_list.called
        assert result.status_code == 200
