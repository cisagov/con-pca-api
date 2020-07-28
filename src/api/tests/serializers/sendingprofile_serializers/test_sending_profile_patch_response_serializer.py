# Third-Party Libraries
from api.serializers.sendingprofile_serializers import (
    SendingProfilePatchResponseSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "id": fake.random_number(),
        "name": fake.name(),
        "username": fake.user_name(),
        "password": fake.password(),
        "host": fake.hostname(),
        "interface_type": fake.word(),
        "from_address": fake.ipv4(),
        "ignore_cert_errors": fake.boolean(),
        "modified_date": fake.date(),
    }
    serializer = SendingProfilePatchResponseSerializer(data=data)
    assert isinstance(serializer, SendingProfilePatchResponseSerializer)
    assert serializer.is_valid()


def test_serializer_host_field_over_max_length():
    # host field over 255 characters in length should return an invalid serializer
    data = {
        "id": fake.random_number(),
        "name": fake.name(),
        "username": fake.user_name(),
        "password": fake.password(),
        "host": fake.random_letter() * 256,
        "interface_type": fake.word(),
        "from_address": fake.ipv4(),
        "ignore_cert_errors": fake.boolean(),
        "modified_date": fake.date(),
    }
    serializer = SendingProfilePatchResponseSerializer(data=data)

    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("host") is not None
