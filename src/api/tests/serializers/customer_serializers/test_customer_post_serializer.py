# Third-Party Libraries
from api.serializers.customer_serializers import CustomerPostSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "name": fake.name(),
        "identifier": fake.name(),
        "address_1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "customer_type": fake.word(),
        "zip_code": fake.zipcode(),
        "contact_list": [],
    }

    serializer = CustomerPostSerializer(data=data)

    assert serializer.is_valid() is True
