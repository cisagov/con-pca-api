# Third-Party Libraries
from api.serializers.sendingprofile_serializers import (
    SendingProfileDeleteResponseSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"id": fake.random_number()}
    serializer = SendingProfileDeleteResponseSerializer(data=data)

    assert isinstance(serializer, SendingProfileDeleteResponseSerializer)
    assert serializer.is_valid()
