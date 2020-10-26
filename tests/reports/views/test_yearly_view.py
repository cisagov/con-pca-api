from src.reports.views import yearly_view
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


def get_dhs():
    return {
        "dhs_contact_uuid": "1234",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "office_phone": fake.phone_number(),
        "mobile_phone": fake.phone_number(),
        "email": fake.email(),
        "notes": fake.paragraph(),
        "active": True,
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def get_recommendation():
    return {
        "recommendations_uuid": "1234",
        "name": "foo bar",
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "relevancy": {"organization": 0, "public_news": 0},
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def generate_subscription_stat_details():
    return {
        "campaign_results": [
            {
                "campaign_id": 1234,
                "deception_level": 1,
                "campaign_stats": {},
                "reported_override_val": -1,
                "times": {},
                "ratios": {
                    "clicked_ratio": 1,
                    "opened_ratio": 1,
                    "submitted_ratio": 1,
                    "reported_ratio": 1,
                },
                "template_name": "foo bar",
                "template_uuid": "1234",
            }
        ],
        "stats_all": {},
        "stats_low_deception": {},
        "stats_mid_deception": {},
        "stats_high_deception": {},
        "clicks_over_time": {},
    }


@pytest.mark.django_db
@mock.patch("api.services.SubscriptionService.get", return_value=subscription())
@mock.patch("api.services.SubscriptionService.get_list", return_value=[subscription()])
@mock.patch("api.services.CustomerService.get", return_value=get_customer())
@mock.patch("api.services.CustomerService.get_list", return_value=[get_customer()])
@mock.patch("api.services.DHSContactService.get", return_value=get_dhs())
@mock.patch("api.services.DHSContactService.get_list", return_value=[get_dhs()])
@mock.patch(
    "api.services.RecommendationService.get_list", return_value=[get_recommendation()]
)
@mock.patch(
    "reports.utils.get_yearly_start_dates",
    return_value=(fake.date_time(), fake.date_time()),
)
@mock.patch(
    "reports.utils.get_subscription_stats_for_yearly",
    return_value=(generate_subscription_stat_details(), []),
)
@mock.patch("reports.utils.get_template_details", return_value=None)
@mock.patch("reports.utils.get_relevant_recommendations", return_value=["1234"])
def test_year_view_get(
    mock_subscription_get,
    mock_subscription_get_list,
    mock_customer_get,
    mock_customer_get_list,
    mock_dhs_contact_get,
    mock_dhs_contact_get_list,
    mock_recommendation_get_list,
    mock_get_yearly_start_dates,
    mock_get_subscription_stats_for_yearly,
    mock_get_template_details,
    mock_get_relevant_recommendations,
    client,
):
    result = client.get("/reports/1234/yearly/2020-07-30T19:37:54.960Z/")

    assert mock_subscription_get_list.called
    assert mock_customer_get_list.called
    assert mock_dhs_contact_get.called
    assert mock_recommendation_get_list.called

    assert result.status_code == 202
