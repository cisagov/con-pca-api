"""Template Models."""
# cisagov Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    IntType,
    ModelType,
    StringType,
    UUIDType,
)


class TemplateAppearanceModel(Model):
    """TemplateAppearanceModel."""

    grammar = IntType()
    link_domain = IntType()
    logo_graphics = IntType()


class TemplateSenderModel(Model):
    """TemplateSenderModel."""

    external = IntType()
    internal = IntType()
    authoritative = IntType()


class TemplateRelevancyModel(Model):
    """TemplateRelevancyModel."""

    organization = IntType()
    public_news = IntType()


class TemplateBehaviorModel(Model):
    """TemplateBehaviorModel."""

    fear = IntType()
    duty_obligation = IntType()
    curiosity = IntType()
    greed = IntType()


class TemplateModel(Model):
    """TemplateModel."""

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


class DeceptionLevelStatsModel:
    """DeceptionLevelStatsModel."""

    level = StringType()
    level_number = IntType()
    sent = IntType()
    total = IntType()
    opened = IntType()
    clicked = IntType()
    submitted_data = IntType()
    email_reported = IntType()

    def __init__(self, level, level_number):
        """Create Model."""
        self.level = level
        self.level_number = level_number
        self.sent = 0
        self.total = 0
        self.opened = 0
        self.clicked = 0
        self.submitted_data = 0
        self.email_reported = 0
