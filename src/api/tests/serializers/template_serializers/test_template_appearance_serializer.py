# Third-Party Libraries
from api.serializers.template_serializers import TemplateAppearanceSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "grammar": fake.random_number(),
        "link_domain": fake.random_number(),
        "logo_graphics": fake.random_number(),
    }
    serializer = TemplateAppearanceSerializer(data=data)

    assert isinstance(serializer, TemplateAppearanceSerializer)
    assert serializer.is_valid()
