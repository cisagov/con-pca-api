"""SubscriptionCustomerListView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

# cisagov Libraries
from samples import subscription

fake = Faker()


@pytest.mark.django_db
def test_subscription_view_customer_list_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ) as mock_get_list:
        result = client.get("/api/v1/subscription/customer/1234/")
        assert mock_get_list.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_subscription_view_customer_list_post(client):
    """Test Post."""
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ) as mock_get_list:
        result = client.post(
            "/api/v1/subscription/customer/1234/", {"keywords": "research"}
        )
        assert mock_get_list.called
        assert result.status_code == 200
