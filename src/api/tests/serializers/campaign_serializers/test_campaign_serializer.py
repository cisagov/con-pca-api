# Third-Party Libraries
from api.serializers.campaign_serializers import CampaignSerializer
from faker import Faker

fake = Faker()


def test_creation():
    data = {
        "id": fake.random_number(),
        "name": fake.name(),
        "created_date": fake.date_time(),
        "launch_date": fake.date_time(),
        "send_by_date": fake.date_time(),
        "completed_date": fake.date_time(),
        "status": fake.word(),
        "url": fake.url(),
        "results": [],
        "groups": [],
        "timeline": [],
    }
    serializer = CampaignSerializer(data=data)
    assert isinstance(serializer, CampaignSerializer)
    serializer.is_valid()
    assert len(serializer.errors) == 0


def test_serializer_missing_name_field():
    data = {
        "id": fake.random_number(),
        "created_date": fake.date_time(),
        "launch_date": fake.date_time(),
        "send_by_date": fake.date_time(),
        "completed_date": fake.date_time(),
        "status": fake.word(),
        "url": fake.url(),
        "results": [],
        "groups": [],
        "timeline": [],
    }
    serializer = CampaignSerializer(data=data)
    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("name") is not None
