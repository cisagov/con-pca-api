import pytest
from unittest import mock
from faker import Faker


fake = Faker()


def sending_profiles():
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


@pytest.mark.django_db
def test_sendingProfiles_list_get(client):
    with mock.patch(
        "api.manager.CampaignManager.get_sending_profile",
        return_value=[sending_profiles()],
    ) as mock_get_list:
        result = client.get("/api/v1/sendingprofiles/")
        assert mock_get_list.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sendingProfiles_list_post(client):
    with mock.patch(
        "api.manager.CampaignManager.create_sending_profile",
        return_value=sending_profiles(),
    ) as mock_create:
        result = client.post("/api/v1/sendingprofiles/", sending_profiles())
        assert mock_create.called
        assert result.status_code == 200
