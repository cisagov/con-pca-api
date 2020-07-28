# Third-Party Libraries
from api.serializers.campaign_serializers import CampaignGroupTargetSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
    }

    serializer = CampaignGroupTargetSerializer(data=data)
    assert isinstance(serializer, CampaignGroupTargetSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
