# Third-Party Libraries
from api.serializers.sendingprofile_serializers import SendingProfilePatchSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "name": fake.name(),
        "username": fake.user_name(),
        "password": fake.password(),
        "host": fake.hostname(),
        "interface_type": fake.word(),
        "from_address": fake.ipv4(),
        "ignore_cert_errors": fake.boolean(),
        "modified_date": fake.date(),
    }
    serializer = SendingProfilePatchSerializer(data=data)

    assert isinstance(serializer, SendingProfilePatchSerializer)
    assert serializer.is_valid()


def test_serializer_missing_fields():
    # missing interface type, host, password, username, and name fields should still return a valid serializer
    data = {
        "from_address": fake.ipv4(),
        "ignore_cert_errors": fake.boolean(),
        "modified_date": fake.date(),
    }
    serializer = SendingProfilePatchSerializer(data=data)

    assert serializer.is_valid()
