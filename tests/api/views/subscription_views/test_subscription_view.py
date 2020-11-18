"""SubscriptionView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import campaign, subscription


@pytest.mark.django_db
def test_subscription_view_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "reports.utils.update_phish_results",
        return_value=None,
    ):
        result = client.get("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert result.status_code == 200

    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=None,
    ) as mock_get_single, mock.patch(
        "reports.utils.update_phish_results",
        return_value=None,
    ):
        result = client.get("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert result.status_code == 404


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get", return_value={})
def test_subscription_view_patch(mock_get, client):
    """Test Patch."""
    with mock.patch(
        "api.services.SubscriptionService.update",
        return_value=subscription(),
    ) as mock_update_single:
        result = client.patch(
            "/api/v1/subscription/1234/",
            {"customer_uuid": "12345"},
            content_type="application/json",
        )
        assert mock_update_single.called
        assert mock_get.called
        assert result.status_code == 202


@pytest.mark.django_db
def test_subscription_view_delete(client):
    """Test Delete."""
    with mock.patch(
        "api.services.SubscriptionService.delete",
        return_value={"subscription_uuid": "1234"},
    ) as mock_delete_single, mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.CampaignService.get_list",
        return_value=[campaign()],
    ), mock.patch(
        "api.services.CampaignService.delete",
        return_value=None,
    ):
        result = client.delete("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert mock_delete_single.called
        assert result.status_code == 200
