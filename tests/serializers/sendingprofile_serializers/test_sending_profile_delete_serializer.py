# Third-Party Libraries
from api.serializers.sendingprofile_serializers import SendingProfileDeleteSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"id": fake.random_number()}
    serializer = SendingProfileDeleteSerializer(data=data)

    assert isinstance(serializer, SendingProfileDeleteSerializer)
    assert serializer.is_valid()
