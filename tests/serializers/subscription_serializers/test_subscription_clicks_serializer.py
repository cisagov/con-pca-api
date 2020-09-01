# Third-Party Libraries
from api.serializers.subscriptions_serializers import SubscriptionClicksSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "source_ip": fake.ipv4(),
        "timestamp": fake.date_time(),
        "target_uuid": fake.uuid4(),
    }
    serializer = SubscriptionClicksSerializer(data=data)
    assert isinstance(serializer, SubscriptionClicksSerializer)
    assert serializer.is_valid()
