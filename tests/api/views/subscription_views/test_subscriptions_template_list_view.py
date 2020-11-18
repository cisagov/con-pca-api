"""SubscriptionTemplateListView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import subscription


@pytest.mark.django_db
def test_subscription_view_template_list_get(client):
    """Test Get."""
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ) as mock_get_list:
        result = client.get("/api/v1/subscription/template/1234/")
        assert mock_get_list.called
        assert result.status_code == 200
