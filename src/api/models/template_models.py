"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    EmailType,
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


class TemplateImageModel(Model):
    """
    This is the Template Image Model.

    This holds values for template Image Data.
    """

    file_name = StringType()
    file_url = StringType()


class TemplateModel(Model):
    """
    This is the Template Model.

    This controls all data needed in saving the model. Current fields are:
    template_uuid
    name,
    deception_score,
    descriptive_words
    description [string]
    display_link [string]
    from_address [string]
    retired [bool]
    retired_description [string]
    subject [string]
    text [string]
    topic [list] [string]
    appearance [TemplateAppearanceModel]
    sender [TemplateSenderModel]
    relevancy [TemplateRelevancyModel]
    behavior [TemplateBehaviorModel]
    complexity [int]
    """

    # Created via service
    template_uuid = UUIDType()
    # Created by Gophish
    gophish_template_id = IntType()
    # User Creataed
    name = StringType()
    template_type = StringType()
    deception_score = IntType()
    descriptive_words = StringType()
    description = StringType()
    image_list = ListType(ModelType(TemplateImageModel))
    from_address = StringType()
    retired = BooleanType(default=False)
    retired_description = StringType()
    subject = StringType()
    text = StringType()
    html = StringType()
    topic_list = ListType(StringType)
    # Score data
    appearance = ModelType(TemplateAppearanceModel)
    sender = ModelType(TemplateSenderModel)
    relevancy = ModelType(TemplateRelevancyModel)
    behavior = ModelType(TemplateBehaviorModel)
    complexity = IntType()

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


class TagModel(Model):
    """
    Tag Model.

    A Tag is a replaceable string in a
    Template that is replaced by a real value.
    """

    # created by mongodb
    tag_definition_uuid = UUIDType()
    # User Defined
    tag = StringType()
    description = StringType()
    data_source = StringType()
    tag_type = StringType()
    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_tag(data_object):
    """
    This is an the validate_tag.

    This shows basic validation for the model.
    """
    return TagModel(data_object).validate()


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


class TemplateStatusModel(Model):
    """
    Template Status Model.

    This tracks the template uuid and timestamp of being sent.
    """

    template_uuid = UUIDType()
    sent_timestamp = DateTimeType()


class TargetHistoryModel(Model):
    """
    Template History Model.

    This tracks the history of tempaltes sent to a user.
    """

    # created by mongodb
    target_uuid = UUIDType()
    # User Defined
    email = EmailType(required=True)
    history_list = ListType(ModelType(TemplateStatusModel))
    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()


def validate_history(data_object):
    """
    This is an the validate_tag.

    This shows basic validation for the model.
    """
    return TargetHistoryModel(data_object).validate()
