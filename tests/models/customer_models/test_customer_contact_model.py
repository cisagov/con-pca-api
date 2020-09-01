# Third-Party Libraries
from api.models.customer_models import CustomerContactModel
from faker import Faker

fake = Faker()

customer_contact_model_data = {
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "title": fake.job(),
    "office_phone": fake.phone_number(),
    "mobile_phone": fake.phone_number(),
    "email": fake.email(),
    "notes": fake.paragraph(),
}


def test_creation():
    cc = CustomerContactModel(customer_contact_model_data)
    assert isinstance(cc, CustomerContactModel) is True
