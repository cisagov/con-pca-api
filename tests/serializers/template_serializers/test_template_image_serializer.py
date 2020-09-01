# Third-Party Libraries
from api.serializers.template_serializers import TemplateImageSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"file_name": fake.file_name(), "file_url": fake.image_url()}
    serializer = TemplateImageSerializer(data=data)

    assert isinstance(serializer, TemplateImageSerializer)
    assert serializer.is_valid()
