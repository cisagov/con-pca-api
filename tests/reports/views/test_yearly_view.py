"""Reports Yearly View Tests."""
# Standard Python Libraries
from datetime import datetime, timezone
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

fake = Faker()


def subscription():
    """Sample Subscription."""
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
                "end_date": datetime(
                    2020, 10, 30, 5, 49, 2, 960000, tzinfo=timezone.utc
                ),
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
                "campaign_list": [],
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
    """Sample Customer."""
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
    """Sample DHS Contact."""
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
    """Sample Recommendation."""
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
    """Sample Stats."""
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


def template():
    """Sample Template."""
    return {
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "deception_score": 1,
        "description": "Intern Resume",
        "descriptive_words": "student resumes internship intern",
        "from_address": "<%FAKER_FIRST_NAME%> <%FAKER_LAST_NAME%> <<%FAKER_FIRST_NAME%>.<%FAKER_LAST_NAME%>@domain.com>",
        "html": "<br>Hi, sorry, I don't know exactly who this would go to. I read on the site<br>that your accepting student resumes for a summe rinternship. I'ev loaded<br>mine to our school's website. Please review and let me know if we're good to<br>go.<br><a href=\"<%URL%>\">https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdf</a><br><br><br>thx, <%FAKER_FIRST_NAME%>&nbsp;<br>",
        "name": "Intern Resume",
        "relevancy": {"organization": 0, "public_news": 0},
        "retired": False,
        "retired_description": "",
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "subject": "Intern Resume",
        "text": "Hi, sorry, I don't know exactly who this would go to. I read on the sitethat your accepting student resumes for a summe rinternship. I'ev loadedmine to our school's website. Please review and let me know if we're good togo.https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdfthx, <%FAKER_FIRST_NAME%>\u00a0",
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
@mock.patch("api.services.TemplateService.get_list", return_value=[template()])
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
    mock_template_get_list,
    mock_get_yearly_start_dates,
    mock_get_subscription_stats_for_yearly,
    mock_get_template_details,
    mock_get_relevant_recommendations,
    client,
):
    """Yearly View Report Get Test."""
    result = client.get("/reports/1234/yearly/2020-07-30T19:37:54.960Z/")

    assert result.status_code == 202
