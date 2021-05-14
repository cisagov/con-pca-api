"""Sample Objects for Use in Tests."""
# Standard Python Libraries
from datetime import datetime, timezone

# Third-Party Libraries
from faker import Faker

fake = Faker()


def subscription():
    """Sample Subscription."""
    return {
        "subscription_uuid": "12334",
        "active": True,
        "customer_uuid": "changeme",
        "dhs_contact_uuid": "changeme",
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
                "total_targets": 7,
            }
        ],
        "campaigns": [],
        "created_by": "dev user",
        "cb_timestamp": "2020-09-08T19:37:56.881Z",
        "last_updated_by": "dev user",
        "lub_timestamp": "2020-09-15T15:58:47.701Z",
    }


def customer():
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


def campaign():
    """Sample Campaign."""
    return {
        "campaign_uuid": "629ccd2a-1b4d-4bd8-b076-32db9725674e",
        "campaign_id": 1,
        "subscription_uuid": "9e97f76f-3010-4bbf-9910-133426fad9d6",
        "cycle_uuid": "1deff1a1-a6b4-4a21-8d45-4cbc17a33741",
        "name": "Slug Coding_1.3.0.SystemTerminationRequest.2020-10-30.2020-12-29",
        "created_date": "2020-10-30T16:16:48.008Z",
        "launch_date": "2020-10-30T16:17:46.751Z",
        "send_by_date": "2020-12-29T16:17:46.751Z",
        "completed_date": None,
        "email_template": "Slug Coding_1.3.0.SystemTerminationRequest",
        "email_template_id": 1,
        "template_uuid": "d8df8bc1-ea8c-4533-9a13-3466b2da9d48",
        "deception_level": 3,
        "landing_page_template": "default",
        "status": "Queued",
        "results": [],
        "phish_results": {
            "sent": 0,
            "opened": 0,
            "clicked": 0,
            "submitted": 0,
            "reported": 0,
        },
        "phish_results_dirty": True,
        "groups": [
            {
                "id": 1,
                "name": "Slug Coding_1.Targets.3.0",
                "targets": [
                    {
                        "first_name": "one",
                        "last_name": "test",
                        "position": "ceo",
                        "email": "test1@example.com",
                    }
                ],
                "modified_date": "2020-10-30T16:16:48.805Z",
            }
        ],
        "timeline": [
            {
                "email": None,
                "time": "2020-10-30T16:16:48.008Z",
                "message": "Campaign Created",
                "details": "",
                "duplicate": None,
            },
            {
                "email": "test1@example.com",
                "time": "2020-10-30T16:17:54.008Z",
                "message": "Email Sent",
                "details": "",
                "duplicate": None,
            },
        ],
        "target_email_list": [
            {
                "first_name": "one",
                "last_name": "test",
                "position": "ceo",
                "email": "test1@example.com",
            }
        ],
        "smtp": {
            "id": 3,
            "name": "Slug Coding_1.3.0.SystemTerminationRequest.2020-10-30.2020-12-29",
            "host": "smtp.mailgun.org:465",
            "interface_type": "SMTP",
            "from_address": "IT NoReply <no-reply@inltesting.xyz>",
            "ignore_cert_errors": True,
            "modified_date": "2020-10-30T16:16:49.000Z",
            "headers": [
                {"key": "X-Gophish-Contact", "value": "vulnerability@cisa.dhs.gov"},
                {"key": "CISA-PHISH", "value": "1deff1a1-a6b4-4a21-8d45-4cbc17a33741"},
            ],
        },
        "created_by": "dev user",
        "cb_timestamp": "2020-10-30T16:16:49.870Z",
        "last_updated_by": "dev user",
        "lub_timestamp": "2020-10-30T16:17:54.927Z",
    }


def landing_page():
    """Sample LandingPage."""
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


def template():
    """Sample Template."""
    return {
        "template_uuid": "1234",
        "landing_page_uuid": "0",
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
        "created_by": "dev user",
        "cb_timestamp": "2020-09-08T19:37:56.881Z",
        "last_updated_by": "dev user",
        "lub_timestamp": "2020-09-15T15:58:47.701Z",
    }


def recommendation():
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


def sending_profile():
    """Sample Sending Profile."""
    return {
        "id": 1234,
        "name": "foo bar",
        "username": "foo.bar",
        "password": "test",
        "host": "host.com",
        "interface_type": "SMTP",
        "from_address": "from@test.com",
        "ignore_cert_errors": False,
        "modified_date": "2020-01-20T17:33:55.553906Z",
        "headers": [],
    }


def dhs_contact():
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


def cycle():
    """Sample Cycle."""
    return {
        "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
        "start_date": fake.date_time(),
        "end_date": fake.date_time(),
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
