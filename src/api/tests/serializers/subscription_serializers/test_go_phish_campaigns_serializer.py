# Third-Party Libraries
from api.serializers.subscriptions_serializers import GoPhishCampaignsSerializer
from faker import Faker

fake = Faker()


def test_serializer():
    data = {
        "campaign_id": fake.random_number(),
        "name": fake.name(),
        "created_date": fake.date_time(),
        "launch_date": fake.date_time(),
        "send_by_date": fake.date_time(),
        "completed_date": fake.date_time(),
        "email_template": fake.word(),
        "landing_page_template": fake.word(),
        "status": fake.word(),
        "results": [],
        "groups": [],
        "timeline": [],
        "target_email_list": [],
    }
    serializer = GoPhishCampaignsSerializer(data=data)

    assert isinstance(serializer, GoPhishCampaignsSerializer)
    assert serializer.is_valid()
    assert len(serializer.errors) == 0


def test_serializer_fields_over_max_length():
    # name and status fields over character max length should return an invalid serializer
    data = {
        "campaign_id": fake.random_number(),
        "name": "".join(fake.random_letters(256)),
        "created_date": fake.date_time(),
        "launch_date": fake.date_time(),
        "send_by_date": fake.date_time(),
        "completed_date": fake.date_time(),
        "email_template": fake.word(),
        "landing_page_template": fake.word(),
        "status": "".join(fake.random_letters(256)),
        "results": [],
        "groups": [],
        "timeline": [],
        "target_email_list": [],
    }

    serializer = GoPhishCampaignsSerializer(data=data)

    assert serializer.is_valid() is False
    assert len(serializer.errors) == 2
    assert serializer.errors.get("name") is not None
    assert serializer.errors.get("status") is not None


def test_serializer_missing_fields():
    # missing campaign id, send by date, completed date, email template, and etc. fields should return a valid serializer since they are not required
    data = {
        "name": fake.name(),
        "created_date": fake.date_time(),
        "launch_date": fake.date_time(),
        "status": fake.word(),
        "results": [],
        "groups": [],
        "timeline": [],
    }
    serializer = GoPhishCampaignsSerializer(data=data)

    assert serializer.is_valid()
    assert len(serializer.errors) == 0
