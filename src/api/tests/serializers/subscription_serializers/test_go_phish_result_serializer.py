# Third-Party Libraries
from api.serializers.subscriptions_serializers import GoPhishResultSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "id": fake.random_number(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
        "status": fake.word(),
        "ip": fake.ipv4(),
        "latitude": fake.latitude(),
        "longitude": fake.longitude(),
        "send_date": fake.date_time(),
        "reported": fake.boolean(),
    }
    serializer = GoPhishResultSerializer(data=data)
    assert isinstance(serializer, GoPhishResultSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0


def test_serializer_fields_over_max_length():
    # first name, last name, and status fields should return an invalid serializer if thet are over the max character limit
    data = {
        "id": fake.random_number(),
        "first_name": "".join(fake.random_letters(256)),
        "last_name": "".join(fake.random_letters(256)),
        "position": fake.job(),
        "status": "".join(fake.random_letters(256)),
        "ip": fake.ipv4(),
        "latitude": fake.latitude(),
        "longitude": fake.longitude(),
        "send_date": fake.date_time(),
        "reported": fake.boolean(),
    }
    serializer = GoPhishResultSerializer(data=data)
    assert serializer.is_valid() is False
    assert len(serializer.errors) == 3
    assert serializer.errors.get("first_name") is not None
    assert serializer.errors.get("last_name") is not None
    assert serializer.errors.get("status") is not None


def test_serializer_missing_send_date_field():
    # missing send date field should return a valid serializer
    data = {
        "id": fake.random_number(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
        "status": fake.word(),
        "ip": fake.ipv4(),
        "latitude": fake.latitude(),
        "longitude": fake.longitude(),
        "reported": fake.boolean(),
    }
    serializer = GoPhishResultSerializer(data=data)

    assert serializer.is_valid() is True
    assert len(serializer.errors) == 0
    assert serializer.errors.get("send_date") is None
