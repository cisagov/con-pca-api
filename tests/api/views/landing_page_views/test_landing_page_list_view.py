"""Test Landing Page List View."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from gophish.models import Page
import pytest

# cisagov Libraries
from samples import landing_page


def get_landing_page_object():
    """Sample gophish landing page object."""
    landing_page = Page(
        name="landing page",
        html="etest",
        capture_credentials=False,
        capture_passwords=False,
    )
    return landing_page


@mock.patch("api.services.LandingPageService.get_list", return_value=[landing_page()])
@pytest.mark.django_db
def test_landing_page_list_view_get(mock_get_list, client):
    """Test LandingPage ListView Get."""
    response = client.get("/api/v1/landingpages/")
    assert mock_get_list.called
    assert response.status_code == 200


@mock.patch("api.services.LandingPageService.exists", return_value=False)
@mock.patch(
    "api.manager.CampaignManager.create_landing_page",
    return_value=get_landing_page_object(),
)
@mock.patch("api.services.LandingPageService.save", return_value=landing_page())
@mock.patch("api.services.LandingPageService.clear_and_set_default")
@pytest.mark.django_db
def test_landing_page_list_view_post(
    mock_exists, mock_create_landing_page, mock_landing_save, mock_default, client
):
    """Test LandingPage ListView Post."""
    response = client.post("/api/v1/landingpages/", landing_page())
    assert mock_exists.called
    assert mock_create_landing_page.called
    assert mock_landing_save.called
    assert mock_default.called

    assert response.status_code == 201
