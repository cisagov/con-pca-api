# Third-Party Libraries
from api.serializers.customer_serializers import CustomerPostResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"customer_uuid": fake.uuid4()}
    serializer = CustomerPostResponseSerializer(data=data)
    assert serializer.is_valid() is True
