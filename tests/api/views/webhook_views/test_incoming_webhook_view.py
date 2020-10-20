import pytest
from unittest import mock
from faker import Faker

from src.api.views.webhook_views import IncomingWebhookView

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


def web_hook_data_clicked_link():
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Clicked Link",
        "details": "",
    }


def get_campaign_data():
    return {
        "campaign_id": 1234,
        "subscription_uuid": "12345",
        "campaign_uuid": "1234",
        "timeline": [
            {
                "email": None,
                "time": {"$date": "2020-09-08T19:37:56.008Z"},
                "message": "Campaign Created",
                "details": "",
                "duplicate": None,
            }
        ],
    }


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


@pytest.mark.django_db
def test_inbound_webhook_view_post_clicked_link(client):
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

        result = client.post("/api/v1/inboundwebhook/", web_hook_data_clicked_link())

        assert mock_campaign_get_list.called
        assert mock_subscription_data.called
        assert not mock_subscription_update.called
        assert mock_webhook_push.called
        assert mock_campaign_update.called
        assert mock_subscription_update_nested.called
        assert not mock_update_target_history.called

        assert result.status_code == 202


@pytest.mark.django_db
def test_inbound_webhook_view_post_no_data(client):
    result = client.post("/api/v1/inboundwebhook/", {})

    assert result.status_code == 200


def test_inbound_webhook_is_duplicate_timeline_entry():
    timeline_non_match = [
        {
            "email": None,
            "time": {"$date": "2020-09-08T19:37:56.008Z"},
            "message": "Campaign Created",
            "details": "",
            "duplicate": None,
        }
    ]
    webhook_data_non_match = {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Campaign Created",
        "details": "",
    }
    result = IncomingWebhookView().is_duplicate_timeline_entry(
        timeline_non_match, webhook_data_non_match
    )
    assert result == False

    timeline_match = [
        {
            "email": "foo.bar@example.com",
            "time": {"$date": "2020-09-08T19:37:56.008Z"},
            "message": "Email Sent",
            "details": "",
            "duplicate": None,
        }
    ]
    webhook_data_match = {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Email Sent",
        "details": "",
    }

    result = IncomingWebhookView().is_duplicate_timeline_entry(
        timeline_match, webhook_data_match
    )
    assert result == True


def test_inbound_webhook_has_corresponding_opened_event():
    timeline_non_match = [
        {
            "email": None,
            "time": {"$date": "2020-09-08T19:37:56.008Z"},
            "message": "Campaign Created",
            "details": "",
            "duplicate": None,
        }
    ]
    webhook_data_non_match = {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Campaign Created",
        "details": "",
    }
    result = IncomingWebhookView().has_corresponding_opened_event(
        timeline_non_match, webhook_data_non_match
    )
    assert result == False

    timeline_match = [
        {
            "email": "foo.bar@example.com",
            "time": {"$date": "2020-09-08T19:37:56.008Z"},
            "message": "Email Opened",
            "details": "",
            "duplicate": None,
        }
    ]
    webhook_data_match = {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Email Opened",
        "details": "",
    }

    result = IncomingWebhookView().has_corresponding_opened_event(
        timeline_match, webhook_data_match
    )
    assert result == True


def test_inbound_webhook_mark_phishing_results_dirty():
    subscription = {
        "cycles": [{"campaigns_in_cycle": [1234], "phish_results_dirty": False}]
    }
    campaign = {
        "campaign_id": 1234,
    }
    IncomingWebhookView().mark_phishing_results_dirty(subscription, campaign)
    assert subscription["cycles"][0]["phish_results_dirty"] == True
