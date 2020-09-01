# Third-Party Libraries
from api.serializers.template_serializers import (
    TEMPLATE_TYPE_CHOICES,
    TemplatePatchSerializer,
)
from faker import Faker

fake = Faker()


def test_serializer():
    image_data = {"file_name": fake.file_name(), "file_url": fake.image_url()}
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
    data = {
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
    }
    serializer = TemplatePatchSerializer(data=data)

    assert isinstance(serializer, TemplatePatchSerializer)
    assert serializer.is_valid()


def test_serializer_missing_fields():
    # missing name, template type, deception score, descriptive words, description, appearance, sender, relevancy, behavior, complexity,
    # and image list fields should return a valid serializer
    data = {
        "from_address": fake.email(),
        "retired": fake.boolean(),
        "retired_description": fake.paragraph(),
        "subject": fake.word(),
        "text": fake.paragraph(),
        "html": fake.paragraph(),
        "topic_list": [fake.word()],
    }
    serializer = TemplatePatchSerializer(data=data)
    assert serializer.is_valid()
