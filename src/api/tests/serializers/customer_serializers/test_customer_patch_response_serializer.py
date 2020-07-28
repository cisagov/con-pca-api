# Third-Party Libraries
from api.serializers.customer_serializers import CustomerPatchResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "customer_uuid": fake.uuid4(),
        "name": fake.name(),
        "identifier": fake.name(),
        "address_1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip_code": fake.zipcode(),
        "customer_type": fake.word(),
        "contact_list": [],
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }
    serializer = CustomerPatchResponseSerializer(data=data)
    valid = serializer.is_valid()
    assert valid is True
