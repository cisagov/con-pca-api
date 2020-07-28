# Third-Party Libraries
from api.serializers.reports_serializers import ReportsGetSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "customer_name": fake.name(),
        "templates": fake.pydict(),
        "start_date": fake.date_time(),
        "end_date": fake.date_time(),
        "sent": fake.random_number(),
        "opened": fake.random_number(),
        "clicked": fake.random_number(),
        "target_count": fake.random_number(),
    }
    serializer = ReportsGetSerializer(data=data)

    assert isinstance(serializer, ReportsGetSerializer)
    assert serializer.is_valid()
