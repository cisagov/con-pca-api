"""TargetCache View Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

# cisagov Libraries
from samples import subscription

fake = Faker()


@pytest.mark.django_db
def test_subscription_view_target_cache_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.update",
        return_value=subscription(),
    ) as mock_update:
        result = client.post("/api/v1/subscription/targetcache/1234/", {})
        assert mock_update.called
        assert result.status_code == 202
