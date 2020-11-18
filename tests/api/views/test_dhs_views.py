"""DHS Views Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

fake = Faker()


@pytest.mark.django_db
def test_dhs_contact_list_view_get(client):
    """Test List Get."""
    with mock.patch("api.services.DHSContactService.get_list") as mock_get:
        mock_get.return_value = []
        result = client.get("/api/v1/dhscontacts/")
        assert result.status_code == 200
        assert mock_get.called


@pytest.mark.django_db
def test_dhs_contact_list_view_post(client):
    """Test List Post."""
    with mock.patch("api.services.DHSContactService.save") as mock_save:
        data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
        }
        mock_save.return_value = {"dhs_contact_uuid": fake.uuid4()}
        result = client.post("/api/v1/dhscontacts/", data=data)
        assert result.status_code == 201
        assert mock_save.called


@pytest.mark.django_db
def test_dhs_contact_view_get(client):
    """Test Get."""
    with mock.patch("api.services.DHSContactService.get") as mock_get:
        uuid = fake.uuid4()
        mock_get.return_value = {
            "dhs_contact_uuid": uuid,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "created_by": fake.name(),
            "cb_timestamp": fake.date_time(),
            "last_updated_by": fake.name(),
            "lub_timestamp": fake.date_time(),
        }
        response = client.get(f"/api/v1/dhscontact/{uuid}/")
        assert response.status_code == 200
        assert mock_get.called


@pytest.mark.django_db
def test_dhs_contact_view_patch(client):
    """Test Patch."""
    with mock.patch("api.services.DHSContactService.update") as mock_update:
        uuid = fake.uuid4()
        mock_update.return_value = {
            "dhs_contact_uuid": uuid,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "created_by": fake.name(),
            "cb_timestamp": fake.date_time(),
            "last_updated_by": fake.name(),
            "lub_timestamp": fake.date_time(),
        }
        response = client.patch(
            f"/api/v1/dhscontact/{uuid}/", json={"first_name": str(fake.first_name())}
        )
        assert response.status_code == 202
        assert mock_update.called


@pytest.mark.django_db
def test_dhs_contact_view_delete(client):
    """Test Delete."""
    with mock.patch("api.services.DHSContactService.delete") as mock_delete:
        uuid = fake.uuid4()
        mock_delete.return_value = {"dhs_contact_uuid": uuid}
        response = client.delete(f"/api/v1/dhscontact/{uuid}/")
        assert response.status_code == 202
        assert mock_delete.called
