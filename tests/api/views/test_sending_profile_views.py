"""SendingProfile View Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
import pytest

# cisagov Libraries
from samples import sending_profile


@pytest.mark.django_db
def test_sending_profile_get(client):
    """Test Get."""
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=sending_profile(),
    ) as mock_get_single:
        result = client.get("/api/v1/sendingprofile/1234/")
        assert mock_get_single.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sending_profile_patch(client):
    """Test Patch."""
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=sending_profile(),
    ) as mock_get_single, mock.patch(
        "api.manager.CampaignManager.put_sending_profile", return_value=None
    ):
        client.patch("/api/v1/sendingprofile/1234/", sending_profile())
        assert mock_get_single.called


@pytest.mark.django_db
def test_sending_profile_delete(client):
    """Test Delete."""
    with mock.patch(
        "api.manager.CampaignManager.delete_sending_profile", return_value={"id": 1234}
    ) as mock_delete_single:
        result = client.delete("/api/v1/sendingprofile/1234/")
        assert mock_delete_single.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sending_profiles_list_get(client):
    """Test List Get."""
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=[sending_profile()],
    ) as mock_get_list:
        result = client.get("/api/v1/sendingprofiles/")
        assert mock_get_list.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sending_profiles_list_post(client):
    """Test List Post."""
    with mock.patch(
        "api.manager.CampaignManager.create_sending_profile",
        return_value=sending_profile(),
    ) as mock_create:
        result = client.post("/api/v1/sendingprofiles/", sending_profile())
        assert mock_create.called
        assert result.status_code == 200
