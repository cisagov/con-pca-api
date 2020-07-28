# Third-Party Libraries
from api.serializers.webhook_serializers import InboundWebhookSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "campaign_id": fake.random_number(),
        "email": fake.email(),
        "time": fake.date_time(),
        "message": fake.paragraph(),
        "details": fake.paragraph(),
    }
    serializer = InboundWebhookSerializer(data=data)
    assert isinstance(serializer, InboundWebhookSerializer)
    serializer.is_valid()
    assert len(serializer.errors) == 0
