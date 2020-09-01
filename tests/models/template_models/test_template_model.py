# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from api.models.template_models import (
    TemplateAppearanceModel,
    TemplateBehaviorModel,
    TemplateModel,
    TemplateRelevancyModel,
    TemplateSenderModel,
    validate_template,
)
from api.tests.models.template_models.test_template_appearance_model import (
    template_appearance_model_data,
)
from api.tests.models.template_models.test_template_behavior_model import (
    template_behavior_model_data,
)
from api.tests.models.template_models.test_template_image_model import (
    template_image_model_data,
)
from api.tests.models.template_models.test_template_relevancy_model import (
    template_relevancy_model_data,
)
from api.tests.models.template_models.test_template_sender_model import (
    template_sender_model_data,
)
from faker import Faker

fake = Faker()


template_model_data = {
    "template_uuid": fake.uuid4(),
    "gophish_template_id": fake.random_number(),
    "name": fake.name(),
    "template_type": fake.word(),
    "deception_score": fake.random_number(),
    "descriptive_words": " ".join(fake.words()),
    "description": fake.paragraph(),
    "image_list": [template_image_model_data],
    "from_address": fake.email(),
    "retired": fake.boolean(),
    "retired_description": fake.paragraph(),
    "subject": fake.word(),
    "text": fake.paragraph(),
    "html": fake.paragraph(),
    "topic_list": fake.words(),
    "appearance": template_appearance_model_data,
    "sender": template_sender_model_data,
    "relevancy": template_relevancy_model_data,
    "behavior": template_behavior_model_data,
    "complexity": fake.random_number(),
    "created_by": fake.name(),
    "cb_timestamp": fake.date_time(),
    "last_updated_by": fake.name(),
    "lub_timestamp": fake.date_time(),
}


def test_creation():
    template_model = TemplateModel(template_model_data)

    # Check Model Type
    assert isinstance(template_model, TemplateModel)

    # Check Model Attributes
    assert isinstance(template_model.template_uuid, str)
    assert isinstance(template_model.gophish_template_id, int)
    assert isinstance(template_model.name, str)
    assert isinstance(template_model.template_type, str)
    assert isinstance(template_model.deception_score, int)
    assert isinstance(template_model.descriptive_words, str)
    assert isinstance(template_model.description, str)
    assert isinstance(template_model.image_list, list)
    assert isinstance(template_model.from_address, str)
    assert isinstance(template_model.retired, bool)
    assert isinstance(template_model.retired_description, str)
    assert isinstance(template_model.subject, str)
    assert isinstance(template_model.text, str)
    assert isinstance(template_model.html, str)
    assert isinstance(template_model.topic_list, list)
    assert isinstance(template_model.appearance, TemplateAppearanceModel)
    assert isinstance(template_model.sender, TemplateSenderModel)
    assert isinstance(template_model.relevancy, TemplateRelevancyModel)
    assert isinstance(template_model.behavior, TemplateBehaviorModel)
    assert isinstance(template_model.complexity, int)
    assert isinstance(template_model.created_by, str)
    assert isinstance(template_model.cb_timestamp, datetime)
    assert isinstance(template_model.last_updated_by, str)
    assert isinstance(template_model.lub_timestamp, datetime)

    # Test Validation
    validation = validate_template(template_model)

    assert validation is not None
