# Third-Party Libraries
from api.serializers.subscriptions_serializers import SubscriptionTargetSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
        "email": fake.email(),
    }
    serializer = SubscriptionTargetSerializer(data=data)
    assert isinstance(serializer, SubscriptionTargetSerializer)
    assert serializer.is_valid()


def test_serializer_fields_over_max_length():
    # first name, last name, and position fields should return an invalid serializer if they are over the max character length
    data = {
        "first_name": "".join(fake.random_letters(101)),
        "last_name": "".join(fake.random_letters(101)),
        "position": "".join(fake.random_letters(101)),
        "email": fake.email(),
    }
    serializer = SubscriptionTargetSerializer(data=data)
    assert serializer.is_valid() is False
    assert len(serializer.errors) == 3
    assert serializer.errors.get("first_name") is not None
    assert serializer.errors.get("last_name") is not None
    assert serializer.errors.get("position") is not None
