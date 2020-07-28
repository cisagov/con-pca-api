# Third-Party Libraries
from api.serializers.sendingprofile_serializers import SendingProfileSerializer
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
    serializer = SendingProfileSerializer(data=data)

    assert isinstance(serializer, SendingProfileSerializer)
    serializer.is_valid()
    assert len(serializer.errors) == 0
