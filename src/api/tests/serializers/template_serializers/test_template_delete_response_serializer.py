# Third-Party Libraries
from api.serializers.template_serializers import TemplateDeleteResponseSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"template_uuid": fake.uuid4()}
    serializer = TemplateDeleteResponseSerializer(data=data)

    assert isinstance(serializer, TemplateDeleteResponseSerializer)
    assert serializer.is_valid()
