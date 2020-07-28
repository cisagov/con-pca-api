# Third-Party Libraries
from api.serializers.campaign_serializers import CampaignGroupSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "id": fake.random_number(),
        "name": fake.name(),
        "targets": [],
        "modified_date": fake.date_time(),
    }
    serializer = CampaignGroupSerializer(data=data)
    assert isinstance(serializer, CampaignGroupSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
    assert serializer.errors.get("name") is None


def test_serializer_missing_name_field():
    data = {"id": id, "targets": [], "modified_date": "2020-03-29 10:26:23.473031"}
    serializer = CampaignGroupSerializer(data=data)

    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("name") is not None
