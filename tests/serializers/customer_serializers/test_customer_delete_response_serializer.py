# Third-Party Libraries
from api.serializers.customer_serializers import CustomerDeleteResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"customer_uuid": fake.uuid4()}
    assert CustomerDeleteResponseSerializer(data=data).is_valid() is True
