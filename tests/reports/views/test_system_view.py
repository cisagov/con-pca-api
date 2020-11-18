"""Reports System View Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import campaign, customer, subscription


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get_list", return_value=[subscription()])
@mock.patch("api.services.CustomerService.get_list", return_value=[customer()])
@mock.patch("api.services.CampaignService.get_list", return_value=[campaign()])
def test_system_view_get(
    mock_subscription_get_list, mock_customer_get_list, mock_campaign_get_list, client
):
    """Test SystemView Get."""
    result = client.get("/reports/aggregate/")

    assert mock_subscription_get_list.called
    assert mock_customer_get_list.called

    assert result.status_code == 202


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get", return_value=subscription())
def test_subscription_report_emails_sent_view_get(mock_subscription_get, client):
    """Test Report Emails Sent."""
    result = client.get("/reports/subscription_report_emails_sent/1234/")

    assert mock_subscription_get.called

    assert result.status_code == 202
