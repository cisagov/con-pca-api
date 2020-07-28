# Third-Party Libraries
from api.serializers.template_serializers import (
    TEMPLATE_TYPE_CHOICES,
    TemplateStopResponseSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    image_data = {"file_name": fake.file_name(), "file_url": fake.url()}
    appearance_data = {
        "grammar": fake.random_number(),
        "link_domain": fake.random_number(),
        "logo_graphics": fake.random_number(),
    }
    sender_data = {
        "external": fake.random_number(),
        "internal": fake.random_number(),
        "authoritative": fake.random_number(),
    }
    relevancy_data = {
        "organization": fake.random_number(),
        "public_news": fake.random_number(),
    }
    behavior_data = {
        "fear": fake.random_number(),
        "duty_obligation": fake.random_number(),
        "curiosity": fake.random_number(),
        "greed": fake.random_number(),
    }
    template_patch_data = {
        "template_uuid": fake.uuid4(),
        "gophish_template_id": fake.random_number(),
        "name": fake.name(),
        "template_type": TEMPLATE_TYPE_CHOICES[0][0],
        "deception_score": fake.random_number(),
        "descriptive_words": fake.word(),
        "description": fake.paragraph(),
        "image_list": [image_data],
        "from_address": fake.email(),
        "retired": fake.boolean(),
        "retired_description": fake.paragraph(),
        "subject": fake.word(),
        "text": fake.paragraph(),
        "html": fake.paragraph(),
        "topic_list": [fake.word()],
        "appearance": appearance_data,
        "sender": sender_data,
        "relevancy": relevancy_data,
        "behavior": behavior_data,
        "complexity": fake.random_number(),
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }
    customer_data = {
        "first_name": fake.name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "office_phone": fake.phone_number(),
        "mobile_phone": fake.phone_number(),
        "email": fake.email(),
        "notes": fake.paragraph(),
        "active": fake.boolean(),
    }
    subscription_patch_data = {
        "customer_uuid": fake.uuid4(),
        "name": fake.name(),
        "url": fake.url(),
        "keywords": fake.word(),
        "start_date": fake.date_time(),
        "gophish_campaign_list": [],
        "primary_contact": customer_data,
        "status": fake.word(),
        "target_email_list": [],
        "templates_selected_uuid_list": [],
        "active": fake.boolean(),
        "archived": fake.boolean(),
        "manually_stopped": fake.boolean(),
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
        "end_date": fake.date_time(),
    }
    data = {"template": template_patch_data, "subscriptions": [subscription_patch_data]}
    serializer = TemplateStopResponseSerializer(data=data)

    assert isinstance(serializer, TemplateStopResponseSerializer)
    assert serializer.is_valid()
