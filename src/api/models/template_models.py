"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    IntType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)


class TemplateAppearanceModel(Model):
    """
    This is the Template Appearance Model.

    This holds values for template Appearance Score.
    """

    grammar = IntType()
    link_domain = IntType()
    logo_graphics = IntType()


class TemplateSenderModel(Model):
    """
    This is the Template Sender Model.

    This holds values for template Sender Score.
    """

    external = IntType()
    internal = IntType()
    authoritative = IntType()


class TemplateRelevancyModel(Model):
    """
    This is the Template Relevancy Model.

    This holds values for template Relevancy Score.
    """

    organization = IntType()
    public_news = IntType()


class TemplateBehaviorModel(Model):
    """
    This is the Template Behavior Model.

    This holds values for template Behavior Score.
    """

    fear = IntType()
    duty_obligation = IntType()
    curiosity = IntType()
    greed = IntType()


class TemplateModel(Model):
    # Created via service
    template_uuid = UUIDType()

    # User Created
    name = StringType()
    landing_page_uuid = UUIDType(required=False)
    deception_score = IntType()
    descriptive_words = StringType()
    description = StringType()
    from_address = StringType()
    retired = BooleanType(default=False)
    retired_description = StringType()
    subject = StringType()
    text = StringType()
    html = StringType()
    # Score data
    appearance = ModelType(TemplateAppearanceModel)
    sender = ModelType(TemplateSenderModel)
    relevancy = ModelType(TemplateRelevancyModel)
    behavior = ModelType(TemplateBehaviorModel)

    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_template(data_object):
    """
    This validates templates data.

    This shows basic validation for the model.
    """
    return TemplateModel(data_object).validate()


class DeceptionLevelStatsModel:
    """Statistics for a deception level."""

    level = StringType()
    level_number = IntType()
    sent = IntType()
    total = IntType()
    opened = IntType()
    clicked = IntType()
    submitted_data = IntType()
    email_reported = IntType()

    def __init__(self, level, level_number):
        """Init.

        Args:
            level (string): level type
            level_number (int): level number
        """
        self.level = level
        self.level_number = level_number
        self.sent = 0
        self.total = 0
        self.opened = 0
        self.clicked = 0
        self.submitted_data = 0
        self.email_reported = 0
