import pytest
from unittest import mock
from faker import Faker


fake = Faker()


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


@pytest.mark.django_db
def test_subscription_stop_view_get(client):
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.SubscriptionService.update",
        return_value=subscription(),
    ) as mock_update_single, mock.patch(
        "api.utils.subscription.actions.stop_subscription",
        return_value=subscription(),
    ) as mock_stop_subs, mock.patch(
        "api.utils.subscription.subscriptions.send_stop_notification",
        return_value=None,
    ) as mock_stop_noti:
        result = client.get("/api/v1/subscription/stop/1234/")
        assert mock_get_single.called
        assert result.status_code == 202
