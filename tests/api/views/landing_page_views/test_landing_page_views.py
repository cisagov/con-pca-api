"""Landing Page View Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
from gophish.models import Page
import pytest

fake = Faker()


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


def new_customer():
    """Sample Customer."""
    return {
        "name": fake.name(),
        "identifier": fake.word(),
        "address_1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip_code": fake.zipcode(),
        "customer_type": "government",
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
        "industry": "feds",
        "sector": "energy",
    }


def get_landing_page_object():
    """Sample Landing Page Object."""
    landing_page = Page(
        name="landing page",
        html="etest",
        capture_credentials=False,
        capture_passwords=False,
    )
    return landing_page


def get_landing_page():
    """Sample Landing Page."""
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


def get_landing_page_query():
    """Sample Landing Page Query."""
    return {
        "gophish_template_id": 1234,
        "name": "landing page",
        "is_default_template": True,
        "html": "test",
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def get_landing_page_patch():
    """Sample Landing Page Patch Response."""
    return {
        "gophish_template_id": 1234,
        "name": "landing page",
        "is_default_template": True,
        "html": "test",
    }


def get_landing_page_delete():
    """Sample Landing Page Delete Response."""
    return {"gophish_template_id": 1234}


@mock.patch("api.services.LandingPageService.get", return_value=get_landing_page())
@mock.patch("api.services.LandingPageService.clear_and_set_default", return_value=None)
@mock.patch("api.manager.CampaignManager.put_landing_page", return_value=None)
@mock.patch("api.services.LandingPageService.update", return_value=get_landing_page())
@pytest.mark.django_db
def test_landing_page_view_get(
    mock_get_single,
    mock_clear_and_set_default,
    mock_put_landing_page,
    mock_udpate,
    client,
):
    """Landing Page View Get Test."""
    response = client.patch(
        "/api/v1/landingpage/1234/",
        get_landing_page_patch(),
        content_type="application/json",
    )
    assert mock_get_single.called
    assert mock_put_landing_page.called
    assert mock_clear_and_set_default.called
    assert mock_udpate.called
    assert response.status_code == 202


@mock.patch(
    "api.services.LandingPageService.delete", return_value=get_landing_page_delete()
)
@pytest.mark.django_db
def test_landing_page_list_view_post(mock_delete, client):
    """Landing Page List View Post Test."""
    response = client.delete("/api/v1/landingpage/1234/")
    assert mock_delete.called
    assert response.status_code == 200
