# Third-Party Libraries
from api.serializers.campaign_serializers import CampaignEventSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "email": fake.email(),
        "time": fake.date_time(),
        "message": fake.paragraph(),
        "details": fake.paragraph(),
    }

    serializer = CampaignEventSerializer(data=data)
    assert isinstance(serializer, CampaignEventSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
