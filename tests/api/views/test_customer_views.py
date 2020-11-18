"""CustomerView Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

# cisagov Libraries
from samples import customer

fake = Faker()


@pytest.mark.django_db
def test_customer_list_view(client):
    """Test List."""
    with mock.patch("api.services.CustomerService.get_list") as mock_get:
        mock_get.return_value = [customer()]
        response = client.get("/api/v1/customers/")
        assert mock_get.called
        assert response.status_code == 200
        assert (
            response.json()[0]["customer_uuid"]
            == mock_get.return_value[0]["customer_uuid"]
        )


@pytest.mark.django_db
def test_customer_list_view_post(client):
    """Test Post."""
    # No existing customers
    with mock.patch(
        "api.services.CustomerService.save", return_value={"customer_uuid": "test"}
    ) as mock_save, mock.patch(
        "api.services.CustomerService.exists", return_value=False
    ) as mock_exists:
        response = client.post("/api/v1/customers/", customer())
        assert mock_exists.called
        assert mock_save.called
        assert response.status_code == 201

    # Existing customer with same name/identifier
    with mock.patch("api.services.CustomerService.save") as mock_save, mock.patch(
        "api.services.CustomerService.exists", return_value=True
    ) as mock_exists:
        response = client.post("/api/v1/customers/", customer())
        assert mock_exists.called
        assert not mock_save.called
        assert response.status_code == 202


@pytest.mark.django_db
def test_customer_view_get(client):
    """Test Get."""
    uuid = fake.uuid4()
    with mock.patch("api.services.CustomerService.get") as mock_get:
        mock_get.return_value = customer()
        result = client.get(f"/api/v1/customer/{uuid}/")
        assert mock_get.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_customer_view_patch(client):
    """Test Patch."""
    uuid = fake.uuid4()
    with mock.patch("api.services.CustomerService.update") as mock_update:
        mock_update.return_value = customer()
        result = client.patch(
            f"/api/v1/customer/{uuid}/",
            json={"address_1": str(fake.street_address())},
        )
        assert mock_update.called
        assert result.status_code == 202


@pytest.mark.django_db
def test_customer_view_delete(client):
    """Test Delete."""
    uuid = fake.uuid4()
    with mock.patch("api.services.CustomerService.delete") as mock_delete:
        mock_delete.return_value = {"customer_uuid": uuid}
        result = client.delete(f"/api/v1/customer/{uuid}/")
        assert mock_delete.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_sector_industry_view_get(client):
    """Test SectoryIndustry."""
    result = client.get("/api/v1/sectorindustry/")
    assert result.status_code == 200
