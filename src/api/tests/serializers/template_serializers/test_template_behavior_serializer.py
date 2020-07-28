# Third-Party Libraries
from api.serializers.template_serializers import TemplateBehaviorSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "fear": fake.random_number(),
        "duty_obligation": fake.random_number(),
        "curiosity": fake.random_number(),
        "greed": fake.random_number(),
    }
    serializer = TemplateBehaviorSerializer(data=data)

    assert isinstance(serializer, TemplateBehaviorSerializer)
    assert serializer.is_valid()
