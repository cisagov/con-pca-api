import pytest
from unittest import mock
from faker import Faker

from src.api.views.sendingprofile_views import SendingProfileView


fake = Faker()


def sending_profile():
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


def sending_profile_patch():
    return {
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


@pytest.mark.django_db
def test_sendingProfile_get(client):
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=sending_profile(),
    ) as mock_get_single:
        result = client.get("/api/v1/sendingprofile/1234/")
        assert mock_get_single.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sendingProfile_patch(client):
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=sending_profile(),
    ) as mock_get_single, mock.patch(
        "api.manager.CampaignManager.put_sending_profile", return_value=None
    ) as mock_update_single:
        result = client.patch("/api/v1/sendingprofile/1234/", sending_profile_patch())
        assert mock_get_single.called
        # assert mock_update_single.called
        # assert result.status_code == 200


@pytest.mark.django_db
def test_sendingProfile_delete(client):
    with mock.patch(
        "api.manager.CampaignManager.delete_sending_profile", return_value={"id": 1234}
    ) as mock_delete_single:
        result = client.delete("/api/v1/sendingprofile/1234/")
        assert mock_delete_single.called
        assert result.status_code == 200


def test_setAttribute():
    patch_data = {
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
    result = SendingProfileView().testing__setAttribute(patch_data)
    assert result == "foo.bar"
