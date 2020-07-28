# Third-Party Libraries
from api.serializers.subscriptions_serializers import (
    SubscriptionDeleteResponseSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"subscription_uuid": fake.uuid4()}

    serializer = SubscriptionDeleteResponseSerializer(data=data)
    assert isinstance(serializer, SubscriptionDeleteResponseSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
