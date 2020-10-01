import pytest
from unittest import mock
from faker import Faker

fake = Faker()


@pytest.mark.django_db
def test_campaign_list_view_get(client):
    with mock.patch("api.manager.CampaignManager.get_campaign") as mock_get:
        mock_get.return_value = []
        result = client.get("/api/v1/campaigns/")
        assert mock_get.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_campaign_detail_view_get(client):
    with mock.patch("api.manager.CampaignManager.get_campaign") as mock_get:
        mock_get.return_value = {
            "id": 2,
            "name": fake.name(),
            "created_date": fake.date_time(),
            "launch_date": fake.date_time(),
            "send_by_date": fake.date_time(),
            "completed_date": fake.date_time(),
            "status": "active",
            "url": fake.url(),
            "results": [],
            "groups": [],
            "timeline": [],
        }
        result = client.get("/api/v1/campaign/2/")
        mock_get.assert_called_with(campaign_id="2")
        assert result.status_code == 200
