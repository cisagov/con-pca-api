# Third-Party Libraries
from api.serializers.subscriptions_serializers import SubscriptionPostResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"subscription_uuid": fake.uuid4()}
    serializer = SubscriptionPostResponseSerializer(data=data)
    assert isinstance(serializer, SubscriptionPostResponseSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
