from src.reports.views import system_view
import pytest
from unittest import mock
from faker import Faker
from datetime import datetime, timezone

fake = Faker()


def subscription():
    return {
        "subscription_uuid": "12334",
        "active": True,
        "customer_uuid": "changeme",
        "dhs_contact_uuid": "changeme",
        "keywords": "research development government work job",
        "email_report_history": [
            {
                "report_type": "Cycle Start Notification",
                "sent": datetime(2020, 7, 1, 5, 49, 2),
                "email_to": "test@test.com",
                "email_from": "sender@test.com",
                "bcc": None,
                "manual": False,
            },
            {
                "report_type": "Monthly",
                "sent": datetime(2020, 7, 1, 5, 49, 2),
                "email_to": "test@test.com",
                "email_from": "sender@test.com",
                "bcc": None,
                "manual": False,
            },
            {
                "report_type": "Cycle",
                "sent": datetime(2020, 7, 1, 5, 49, 2),
                "email_to": "test@test.com",
                "email_from": "sender@test.com",
                "bcc": None,
                "manual": False,
            },
            {
                "report_type": "Yearly",
                "sent": datetime(2020, 7, 1, 5, 49, 2),
                "email_to": "test@test.com",
                "email_from": "sender@test.com",
                "bcc": None,
                "manual": False,
            },
        ],
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
        "start_date": datetime(2020, 7, 1, 5, 49, 2),
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
        "cycles": [
            {
                "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
                "start_date": datetime(
                    2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc
                ),
                "end_date": datetime(2020, 10, 30, 5, 49, 2),
                "active": True,
                "campaigns_in_cycle": [1],
                "phish_results": {
                    "sent": 1,
                    "opened": 0,
                    "clicked": 0,
                    "submitted": 0,
                    "reported": 0,
                },
                "phish_results_dirty": False,
                "override_total_reported": -1,
            }
        ],
        "campaigns": [],
        "url": "https://inl.gov",
        "created_by": "dev user",
        "cb_timestamp": fake.date_time(),
        "last_updated_by": "dev user",
        "lub_timestamp": fake.date_time(),
    }


def get_customer():
    return {
        "customer_uuid": fake.uuid4(),
        "name": fake.name(),
        "identifier": fake.word(),
        "address_1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip_code": fake.zipcode(),
        "customer_type": "government",
        "industry": "feds",
        "sector": "energy",
        "contact_list": [
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "title": fake.job(),
                "office_phone": fake.phone_number(),
                "mobile_phone": fake.phone_number(),
                "email": fake.email(),
                "notes": fake.paragraph(),
                "active": True,
            }
        ],
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get_list", return_value=[subscription()])
@mock.patch("api.services.CustomerService.get_list", return_value=[get_customer()])
def test_system_view_get(mock_subscription_get_list, mock_customer_get_list, client):
    result = client.get("/reports/aggregate/")

    assert mock_subscription_get_list.called
    assert mock_customer_get_list.called

    assert result.status_code == 202


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get", return_value=subscription())
def test_subscription_report_emails_sent_view_get(mock_subscription_get, client):
    result = client.get("/reports/subscription_report_emails_sent/1234/")

    assert mock_subscription_get.called

    assert result.status_code == 202
