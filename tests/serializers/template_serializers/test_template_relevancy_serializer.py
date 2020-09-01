# Third-Party Libraries
from api.serializers.template_serializers import TemplateRelevancySerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {"organization": fake.random_number(), "public_news": fake.random_number()}
    serializer = TemplateRelevancySerializer(data=data)

    assert isinstance(serializer, TemplateRelevancySerializer)
    assert serializer.is_valid()
