# Third-Party Libraries
from api.serializers.template_serializers import TemplateSenderSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "external": fake.random_number(),
        "internal": fake.random_number(),
        "authoritative": fake.random_number(),
    }
    serializer = TemplateSenderSerializer(data=data)

    assert isinstance(serializer, TemplateSenderSerializer)
    assert serializer.is_valid()
