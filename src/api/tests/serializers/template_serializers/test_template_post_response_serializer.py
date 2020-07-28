# Third-Party Libraries
from api.serializers.template_serializers import TemplatePostResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"template_uuid": fake.uuid4()}
    serializer = TemplatePostResponseSerializer(data=data)

    assert isinstance(serializer, TemplatePostResponseSerializer)
    assert serializer.is_valid()
