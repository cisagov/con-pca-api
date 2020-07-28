# Third-Party Libraries
from api.serializers.campaign_serializers import CampaignResultSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "id": fake.random_number(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
        "status": fake.word(),
        "ip": fake.ipv4(),
        "latitude": fake.latitude(),
        "longitude": fake.longitude(),
        "send_date": fake.date_time(),
        "reported": fake.boolean(),
    }
    serializer = CampaignResultSerializer(data=data)
    assert isinstance(serializer, CampaignResultSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
    assert serializer.errors.get("active") is None
