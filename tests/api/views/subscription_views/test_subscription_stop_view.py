"""Subscription Stop View Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import subscription


@pytest.mark.django_db
def test_subscription_stop_view_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.SubscriptionService.update",
        return_value=subscription(),
    ), mock.patch(
        "api.utils.subscription.actions.stop_subscription",
        return_value=subscription(),
    ), mock.patch(
        "api.utils.subscription.subscriptions.send_stop_notification",
        return_value=None,
    ):
        result = client.get("/api/v1/subscription/stop/1234/")
        assert mock_get_single.called
        assert result.status_code == 202
