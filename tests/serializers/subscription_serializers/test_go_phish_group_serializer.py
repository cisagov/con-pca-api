# Third-Party Libraries
from api.serializers.subscriptions_serializers import GoPhishGroupSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "id": fake.random_number(),
        "name": fake.name(),
        "targets": [],
        "modified_date": fake.date_time(),
    }
    serializer = GoPhishGroupSerializer(data=data)

    assert isinstance(serializer, GoPhishGroupSerializer)
    assert serializer.is_valid()


def test_serializer_missing_id_field():
    # missing id field should return a valid serializer since it is not required
    data = {"name": fake.name(), "targets": [], "modified_date": fake.date_time()}
    serializer = GoPhishGroupSerializer(data=data)

    assert serializer.is_valid()
    assert len(serializer.errors) == 0
    assert serializer.errors.get("id") is None


def test_serializer_name_field_over_max_length():
    # name field over max character length should return an invalid serializer
    data = {
        "id": fake.random_number(),
        "name": "".join(fake.random_letters(256)),
        "targets": [],
        "modified_date": fake.date_time(),
    }

    serializer = GoPhishGroupSerializer(data=data)

    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("name") is not None
