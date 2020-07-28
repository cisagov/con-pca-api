# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from api.serializers.subscriptions_serializers import GoPhishTimelineSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "email": fake.email(),
        "time": fake.date_time(),
        "message": fake.word(),
        "details": fake.word(),
    }
    serializer = GoPhishTimelineSerializer(data=data)

    assert isinstance(serializer, GoPhishTimelineSerializer)
    assert serializer.is_valid()


def test_serializer_missing_email_field():
    # missing email field should return a valid serializer
    data = {
        "time": fake.date_time(),
        "message": fake.word(),
        "details": fake.word(),
    }
    serializer = GoPhishTimelineSerializer(data=data)

    assert serializer.is_valid()
    assert len(serializer.errors) == 0
    assert serializer.errors.get("email") is None


def test_serializer_message_field_over_max_length():
    # message field over max character length should return an invalid serializer
    data = {
        "email": fake.email(),
        "time": fake.date_time(),
        "message": "".join(fake.random_letters(256)),
        "details": fake.word(),
    }
    serializer = GoPhishTimelineSerializer(data=data)

    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("message") is not None
