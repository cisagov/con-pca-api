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
        "cycles": [
            {
                "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
                "start_date": "2020-09-08T19:38:54.960Z",
                "end_date": "2020-12-07T19:37:54.960Z",
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
        "cb_timestamp": "2020-09-08T19:37:56.881Z",
        "last_updated_by": "dev user",
        "lub_timestamp": "2020-09-15T15:58:47.701Z",
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


@pytest.mark.django_db
def test_subscription_stop_view_get(client):
    with mock.patch(
        "api.services.SubscriptionService.get",
        return_value=subscription(),
    ) as mock_get_single, mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[subscription()],
    ) as mock_get_single_list, mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ) as mock_get_template_list, mock.patch(
        "api.services.CustomerService.get",
        return_value=get_customer(),
    ) as mock_get_customer, mock.patch(
        "api.services.CustomerService.get_list",
        return_value=[get_customer()],
    ) as mock_get_customer_list, mock.patch(
        "api.services.RecommendationService.get_list",
        return_value=[get_recommendation()],
    ) as mock_get_single_list:
        result = client.get("/api/v1/reports/1234/")
        assert mock_get_single.called
        assert mock_get_template_list.called

        assert result.status_code == 200
