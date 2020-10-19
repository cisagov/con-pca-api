import pytest
from unittest import mock
from faker import Faker

fake = Faker()


def web_hook_data_campaign_created():
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Campaign Created",
        "details": "",
    }


def web_hook_data_email_sent():
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Email Sent",
        "details": "",
    }


def get_campaign_data():
    return {"campaign_id": 1234, "subscription_uuid": "12345", "campaign_uuid": "1234"}


def get_subscription_data():
    return {
        "status": "Queued",
        "subscription_uuid": "12345",
        "campaign_uuid": "1234",
        "cycles": [
            {
                "cycle_uuid": "1234",
                "campaigns_in_cycle": [1234],
                "phish_results_dirty": True,
            }
        ],
    }


@pytest.mark.django_db
def test_inbound_webhook_view_post_campaign_created(client):
    result = client.post("/api/v1/inboundwebhook/", web_hook_data_campaign_created())
    assert result.status_code == 200


@pytest.mark.django_db
def test_inbound_webhook_view_post_email_sent_not_found(client):
    with mock.patch(
        "api.services.CampaignService.get_list", return_value=[get_campaign_data()]
    ) as mock_get_list, mock.patch(
        "api.services.SubscriptionService.get", return_value=None
    ) as mock_sub_data:
        result = client.post("/api/v1/inboundwebhook/", web_hook_data_email_sent())
        assert mock_get_list.called
        assert mock_sub_data.called
        assert result.status_code == 404


@pytest.mark.django_db
def test_inbound_webhook_view_post_email_sent(client):
    with mock.patch(
        "api.services.CampaignService.get_list", return_value=[get_campaign_data()]
    ) as mock_campaign_get_list, mock.patch(
        "api.services.SubscriptionService.get", return_value=get_subscription_data()
    ) as mock_subscription_data, mock.patch(
        "api.services.SubscriptionService.update", return_value=None
    ) as mock_subscription_update, mock.patch(
        "api.utils.webhooks.push_webhook", return_value=None
    ) as mock_webhook_push, mock.patch(
        "api.services.CampaignService.update", return_value=None
    ) as mock_campaign_update, mock.patch(
        "api.services.SubscriptionService.update_nested", return_value=None
    ) as mock_subscription_update_nested, mock.patch(
        "api.utils.template.templates.update_target_history", return_value=None
    ) as mock_update_target_history:

        result = client.post("/api/v1/inboundwebhook/", web_hook_data_email_sent())

        assert mock_campaign_get_list.called
        assert mock_subscription_data.called
        assert mock_subscription_update.called
        assert mock_webhook_push.called
        assert mock_campaign_update.called
        assert mock_subscription_update_nested.called
        assert mock_update_target_history.called

        assert result.status_code == 202
