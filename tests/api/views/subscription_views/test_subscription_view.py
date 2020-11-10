import pytest
from unittest import mock
from faker import Faker


fake = Faker()


def campaign():
    return {"subscription_uuid": "1234", "campaign_uuid": "12334"}


def subscription():
    return {
        "subscription_uuid": "12334",
        "active": True,
        "customer_uuid": "changeme",
        "dhs_contact_uuid": "changeme",
        "keywords": "research development government work job",
        "name": "1",
        "primary_contact": {
            "active": True,
            "email": "Matt.Daemon@example.com",
            "first_name": "Matt",
            "last_name": "Daemon",
            "mobile_phone": "555-555-5555",
            "office_phone": "555-555-5555",
        },
        "sending_profile_name": "SMTP",
        "start_date": "2020-04-10T09:30:25",
        "status": "  Waiting on SRF",
        "target_email_list": [
            {
                "email": "Bat.Man@example.com",
                "first_name": "Bat",
                "last_name": "Man",
                "position": "admin",
            },
            {
                "email": "Ben.Aflex@example.com",
                "first_name": "Ben",
                "last_name": "Aflex",
                "position": "admin",
            },
            {
                "email": "David.Young@example.com",
                "first_name": "David",
                "last_name": "Young",
                "position": "intern",
            },
            {
                "email": "George.Clooney@example.com",
                "first_name": "George",
                "last_name": "Clooney",
                "position": "intern",
            },
            {
                "email": "Jane.Doe@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "position": "intern",
            },
            {
                "email": "Jane.Moore@example.com",
                "first_name": "Jane",
                "last_name": "Moore",
                "position": "manager",
            },
            {
                "email": "John.Smith@example.com",
                "first_name": "John",
                "last_name": "Smith",
                "position": "manager",
            },
        ],
        "templates_selected_uuid_list": [],
        "cycles": [],
        "campaigns": [],
        "url": "https://inl.gov",
        "created_by": "dev user",
        "cb_timestamp": "2020-09-08T19:37:56.881Z",
        "last_updated_by": "dev user",
        "lub_timestamp": "2020-09-15T15:58:47.701Z",
    }


def subscription_patch():
    return {"customer_uuid": "12345"}


@pytest.mark.django_db
def test_subscription_view_get(client):
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "reports.utils.update_phish_results",
        return_value=None,
    ) as mock_update_phish_results:
        result = client.get("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert result.status_code == 200

    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=None,
    ) as mock_get_single, mock.patch(
        "reports.utils.update_phish_results",
        return_value=None,
    ) as mock_update_phish_results:
        result = client.get("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert result.status_code == 404


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get", return_value={})
def test_subscription_view_patch(mock_get, client):
    with mock.patch(
        "api.services.SubscriptionService.update",
        return_value=subscription(),
    ) as mock_update_single:
        result = client.patch(
            "/api/v1/subscription/1234/",
            subscription_patch(),
            content_type="application/json",
        )
        assert mock_update_single.called
        assert mock_get.called
        assert result.status_code == 202


@pytest.mark.django_db
def test_subscription_view_delete(client):
    with mock.patch(
        "api.services.SubscriptionService.delete",
        return_value={"subscription_uuid": "1234"},
    ) as mock_delete_single, mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.CampaignService.get_list",
        return_value=[campaign()],
    ) as mock_campaign_list, mock.patch(
        "api.services.CampaignService.delete",
        return_value=None,
    ) as mock_campaign_list:
        result = client.delete("/api/v1/subscription/1234/")
        assert mock_get_single.called
        assert mock_delete_single.called
        assert result.status_code == 200
