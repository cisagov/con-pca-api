import pytest
from unittest import mock
from faker import Faker

fake = Faker()


def get_customer():
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


@pytest.mark.django_db
def test_customer_list_view(client):
    with mock.patch("api.utils.db_utils.get_list") as mock_get:
        mock_get.return_value = [get_customer()]
        response = client.get("/api/v1/customers/")
        assert mock_get.called
        assert response.status_code == 200
        assert (
            response.json()[0]["customer_uuid"]
            == mock_get.return_value[0]["customer_uuid"]
        )


@pytest.mark.django_db
def test_customer_list_view_post(client):
    # No existing customers
    with mock.patch("api.utils.db_utils.get_list") as mock_get, mock.patch(
        "api.utils.db_utils.save_single"
    ) as mock_save:
        mock_get.return_value = []
        response = client.post("/api/v1/customers/", new_customer())
        assert mock_get.called
        assert mock_save.called
        assert response.status_code == 201

    # Existing customer with same name/identifier
    with mock.patch("api.utils.db_utils.get_list") as mock_get, mock.patch(
        "api.utils.db_utils.save_single"
    ) as mock_save:
        old = get_customer()
        old["identifier"] = "test"
        old["name"] = "test"
        new = new_customer()
        new["identifier"] = "test"
        new["name"] = "test"
        mock_get.return_value = [old]
        response = client.post("/api/v1/customers/", new)
        assert mock_get.called
        assert not mock_save.called
        assert response.status_code == 202

    with mock.patch("api.utils.db_utils.get_list") as mock_get, mock.patch(
        "api.utils.db_utils.save_single"
    ) as mock_save:
        mock_get.return_value = []
        mock_save.return_value = {"errors": "some error"}
        response = client.post("/api/v1/customers/", new_customer())
        assert mock_get.called
        assert mock_save.called
        assert response.status_code == 400


@pytest.mark.django_db
def test_customer_view_get(client):
    uuid = fake.uuid4()
    with mock.patch("api.utils.db_utils.get_single") as mock_get:
        mock_get.return_value = get_customer()
        result = client.get(f"/api/v1/customer/{uuid}/")
        assert mock_get.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_customer_view_patch(client):
    uuid = fake.uuid4()
    with mock.patch("api.utils.db_utils.update_single") as mock_update:
        mock_update.return_value = get_customer()
        result = client.patch(
            f"/api/v1/customer/{uuid}/", json={"address_1": str(fake.street_address())},
        )
        assert mock_update.called
        assert result.status_code == 202

    with mock.patch("api.utils.db_utils.update_single") as mock_update:
        mock_update.return_value = {"errors": "test error"}
        result = client.patch(
            f"/api/v1/customer/{uuid}/", json={"address_1": str(fake.street_address())},
        )
        assert mock_update.called
        assert result.status_code == 400


@pytest.mark.django_db
def test_customer_view_delete(client):
    uuid = fake.uuid4()
    with mock.patch("api.utils.db_utils.delete_single") as mock_delete:
        mock_delete.return_value = {"customer_uuid": uuid}
        result = client.delete(f"/api/v1/customer/{uuid}/")
        assert mock_delete.called
        assert result.status_code == 200

    with mock.patch("api.utils.db_utils.delete_single") as mock_delete:
        mock_delete.return_value = {"errors": "test error"}
        result = client.delete(f"/api/v1/customer/{uuid}/")
        assert mock_delete.called
        assert result.status_code == 400


@pytest.mark.django_db
def test_sector_industry_view_get(client):
    result = client.get("/api/v1/sectorindustry/")
    assert result.status_code == 200
