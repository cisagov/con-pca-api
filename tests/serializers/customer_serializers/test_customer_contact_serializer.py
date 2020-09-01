# Third-Party Libraries
from api.serializers.customer_serializers import CustomerContactSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "office_phone": fake.phone_number(),
        "mobile_phone": fake.phone_number(),
        "email": fake.email(),
        "notes": fake.paragraph(),
        "active": fake.boolean(),
    }

    serializer = CustomerContactSerializer(data=data)
    assert serializer.is_valid() is True


def test_serializer_null_active():
    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "office_phone": fake.phone_number(),
        "mobile_phone": fake.phone_number(),
        "email": fake.email(),
        "notes": fake.paragraph(),
        "active": None,
    }

    serializer = CustomerContactSerializer(data=data)
    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("active") is not None
