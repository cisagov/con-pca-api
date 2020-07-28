# Third-Party Libraries
from api.serializers.subscriptions_serializers import (
    SubscriptionPatchResponseSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "customer_uuid": fake.uuid4(),
        "name": fake.name(),
        "url": fake.url(),
        "keywords": " ".join(fake.words()),
        "start_date": fake.date_time(),
        "end_date": fake.date_time(),
        "gophish_campaign_list": [],
        "primary_contact": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "title": fake.job(),
            "office_phone": fake.phone_number(),
            "mobile_phone": fake.phone_number(),
            "email": fake.email(),
            "notes": fake.paragraph(),
            "active": fake.boolean(),
        },
        "status": fake.word(),
        "target_email_list": [
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "position": fake.job(),
            }
        ],
        "templates_selected_uuid_list": [],
        "active": fake.boolean(),
        "archived": fake.boolean(),
        "manually_stopped": fake.boolean(),
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }

    serializer = SubscriptionPatchResponseSerializer(data=data)
    assert isinstance(serializer, SubscriptionPatchResponseSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0


def test_serializer_missing_fields():
    data = {
        "customer_uuid": fake.uuid4(),
        # missing name field should return an invalid serializer
        "url": fake.url(),
        "keywords": " ".join(fake.words()),
        "start_date": fake.date_time(),
        "end_date": fake.date_time(),
        "gophish_campaign_list": [],
        "primary_contact": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "title": fake.job(),
            "office_phone": fake.phone_number(),
            "mobile_phone": fake.phone_number(),
            "email": fake.email(),
            "notes": fake.paragraph(),
            "active": fake.boolean(),
        },
        "status": fake.word(),
        "target_email_list": [
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "position": fake.job(),
            }
        ],
        # missing templates_selected_uuid_list fields should not result in an error
        "active": fake.boolean(),
        "archived": fake.boolean(),
        "manually_stopped": fake.boolean(),
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }
    serializer = SubscriptionPatchResponseSerializer(data=data)
    assert serializer.is_valid() is False
    assert len(serializer.errors) == 1
    assert serializer.errors.get("name") is not None
    assert serializer.errors.get("templates_selected_uuid_list") is None
