# Third-Party Libraries
from api.models.customer_models import CustomerModel
from api.tests.models.customer_models.test_customer_contact_model import (
    customer_contact_model_data,
)
from faker import Faker

fake = Faker()


customer_model_data = {
    "customer_uuid": fake.uuid4(),
    "name": fake.company(),
    "identifier": fake.company(),
    "address_1": fake.street_address(),
    "address_2": None,
    "city": fake.city(),
    "state": fake.state(),
    "zip_code": fake.zipcode(),
    "contact_list": [customer_contact_model_data],
    "created_by": fake.name(),
    "cb_timestamp": fake.date_time(),
    "last_updated_by": fake.name(),
    "lub_timestamp": fake.date_time(),
}


def test_creation():
    c = CustomerModel(customer_model_data)
    assert isinstance(c, CustomerModel) is True
