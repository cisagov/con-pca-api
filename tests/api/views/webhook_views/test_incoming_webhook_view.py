"""IncomingWebhookView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

# cisagov Libraries
from src.api.views.webhook_views import IncomingWebhookView

fake = Faker()


def web_hook_data_campaign_created():
    """Get CampaignCreated Event."""
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Campaign Created",
        "details": "",
    }


def web_hook_data_email_sent():
    """Get EmailSent Event."""
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Email Sent",
        "details": "",
    }


def web_hook_data_clicked_link():
    """Get Clicked Link Event."""
    return {
        "campaign_id": 1234,
        "email": "foo.bar@example.com",
        "time": "2020-01-20T17:33:55.553906Z",
        "message": "Clicked Link",
        "details": "",
    }


def get_campaign_data():
    """Get Campaign Data."""
    return {
        "campaign_id": 1234,
        "subscription_uuid": "12345",
        "campaign_uuid": "1234",
        "cycle_uuid": "123456",
        "template_uuid": "432451",
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
    """Get Subscription Data."""
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
    """Test Post."""
    result = client.post("/api/v1/inboundwebhook/", web_hook_data_campaign_created())
    assert result.status_code == 200


@pytest.mark.django_db
@mock.patch("api.services.CampaignService.get_single", return_value=get_campaign_data())
@mock.patch("api.services.CampaignService.push_nested")
@mock.patch("api.services.CampaignService.update")
@mock.patch("api.services.SubscriptionService.update_nested")
@mock.patch("api.utils.template.templates.update_target_history", return_value=None)
def test_inbound_webhook_view_post_email_sent(
    mock_update_target_history,
    mock_subscription_update_nested,
    mock_campaign_update,
    mock_webhook_push,
    mock_campaign_get_list,
    client,
):
    """Test Post Email Sent."""
    result = client.post("/api/v1/inboundwebhook/", web_hook_data_email_sent())

    assert mock_campaign_get_list.called
    assert mock_webhook_push.called
    assert mock_campaign_update.called
    assert mock_subscription_update_nested.called
    assert mock_update_target_history.called

    assert result.status_code == 202


@pytest.mark.django_db
@mock.patch("api.services.CampaignService.get_single", return_value=get_campaign_data())
@mock.patch("api.services.CampaignService.push_nested")
@mock.patch("api.services.CampaignService.update")
@mock.patch("api.services.SubscriptionService.update_nested")
@mock.patch("api.utils.template.templates.update_target_history", return_value=None)
def test_inbound_webhook_view_post_clicked_link(
    mock_update_target_history,
    mock_subscription_update_nested,
    mock_campaign_update,
    mock_webhook_push,
    mock_campaign_get_list,
    client,
):
    """Test Clicked Link."""
    result = client.post("/api/v1/inboundwebhook/", web_hook_data_clicked_link())

    assert mock_campaign_get_list.called
    assert mock_webhook_push.called
    assert mock_campaign_update.called
    assert mock_subscription_update_nested.called
    assert not mock_update_target_history.called

    assert result.status_code == 202


@pytest.mark.django_db
def test_inbound_webhook_view_post_no_data(client):
    """Test Post No Data."""
    result = client.post("/api/v1/inboundwebhook/", {})

    assert result.status_code == 200


def test_inbound_webhook_is_duplicate_timeline_entry():
    """Test Duplicates."""
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
    assert result is False

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
    assert result is True


def test_inbound_webhook_has_corresponding_opened_event():
    """Test duplicate opened."""
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
    assert result is False

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
    assert result is True


def test_inbound_webhook_mark_phishing_results_dirty():
    """Test phish results dirty."""
    subscription = {
        "cycles": [{"campaigns_in_cycle": [1234], "phish_results_dirty": False}]
    }
    campaign = {
        "campaign_id": 1234,
    }
    IncomingWebhookView().mark_phishing_results_dirty(subscription, campaign)
    assert subscription["cycles"][0]["phish_results_dirty"] is True
