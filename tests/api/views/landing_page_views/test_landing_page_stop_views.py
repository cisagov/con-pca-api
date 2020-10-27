import pytest
from unittest import mock
from faker import Faker
from datetime import datetime, timezone
from gophish.models import SMTP


fake = Faker()


def subscription():
    return {
        "subscription_uuid": "12334",
        "active": True,
        "customer_uuid": "1234",
        "dhs_contact_uuid": "1234",
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


def get_landing_page():
    return {
        "landing_page_uuid": "1234",
        "gophish_template_id": 1234,
        "name": "landing page",
        "is_default_template": True,
        "html": "test",
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


def template():
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


def get_sending_profile_object():
    sending_profile = SMTP(
        id=123,
        name="name",
        username="username",
        password="password",
        host="host",
        interface_type="interface_type",
        from_address="from_address",
        ignore_cert_errors=False,
        headers=[],
    )
    return sending_profile


@mock.patch("api.services.SubscriptionService.get_list", return_value=[subscription()])
@mock.patch(
    "api.utils.subscription.actions.stop_subscription", return_value=subscription()
)
@mock.patch(
    "api.utils.subscription.subscriptions.send_stop_notification", return_value=None
)
@mock.patch("api.services.LandingPageService.get", return_value=get_landing_page())
@mock.patch("api.services.LandingPageService.update", return_value=get_landing_page())
@mock.patch("api.services.DHSContactService.get", return_value=get_dhs())
@mock.patch("api.services.TemplateService.get_list", return_value=[template()])
@mock.patch(
    "api.manager.CampaignManager.get_sending_profile",
    return_value=[get_sending_profile_object()],
)
@pytest.mark.django_db
def test_landing_page_stop_view_get(
    mock_get_sub_list,
    mock_stop_subscription,
    mock_send_stop_notification,
    mock_landing_get,
    mock_landing_update,
    mock_get_dhs,
    mock_get_template_list,
    mock_get_sending_profile_object,
    client,
):
    response = client.get("/api/v1/landingpage/stop/1234/")
    print(response)
    assert response is not None
