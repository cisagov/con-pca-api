from src.api import manager
import pytest
from unittest import mock
from faker import Faker
from datetime import datetime, timezone
from gophish import Gophish


fake = Faker()


class MockGoPhish(object):
    def __init__(self):
        self.campaigns = campaign()


def campaign():
    return {
        "id": 1,
        "name": "campaign",
        "created_date": "2020-07-30T19:37:54.960Z",
        "launch_date": "2020-07-30T19:37:54.960Z",
        "send_by_date": "2020-07-30T19:37:54.960Z",
        "completed_date": "2020-07-30T19:37:54.960Z",
        "template": {},
        "page": {},
        "status": "ready",
        "results": [],
        "groups": [],
        "timeline": [],
        "smtp": {},
        "url": "google",
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


class TestCampaignManager:
    def test_create(self):
        return

    def test_delte(self):
        return

    def test_put(self):
        return

    def test_generate_campaign(self):
        return

    def test_generate_sending_profile(self):
        return

    def test_create_sending_profile(self):
        return

    def test_put_sending_profile(self):
        return

    def test_generate_email_template(self):
        return

    def test_generate_landing_page(self):
        return

    def test_put_landing_page(self):
        return

    def test_generate_user_group(self):
        return

    def test_get_campaign(self):
        return

    def test_get_campaign_summary(self):
        return

    def test_get_sending_profile(self):
        return

    def test_get_email_template(self):
        return

    def test_get_landing_page(self):
        return

    def test_get_user_group(self):
        return

    def test_delete_campaign(self):
        return

    def test_delete_sending_profile(self):
        return

    def test_delete_email_template(self):
        return

    def test_delete_landing_page(self):
        return

    def test_delete_user_group(self):
        return

    def test_send_test_email(self):
        return

    def test_complete_campaign(self):
        return
