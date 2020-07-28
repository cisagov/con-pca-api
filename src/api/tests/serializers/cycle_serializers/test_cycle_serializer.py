"""Cycle Serializer Tests."""
# Third-Party Libraries
from api.serializers.cycle_serializers import CycleEmailReportedListPostSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    """Test Cycle Serializer."""
    data = {
        "start_date": fake.date_time(),
        "end_date": fake.date_time(),
        "override_total_reported": 420,
        "update_list": [
            {"campaign_id": None, "email": fake.email(), "datetime": fake.date_time()},
            {"campaign_id": 1, "email": fake.email(), "datetime": fake.date_time()},
        ],
        "delete_list": [
            {{"campaign_id": 2, "email": fake.email(), "datetime": fake.date_time()}}
        ],
    }

    serializer = CycleEmailReportedListPostSerializer(data=data)
    assert isinstance(serializer, CycleEmailReportedListPostSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0
