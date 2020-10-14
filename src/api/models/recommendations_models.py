"""
Models.

These are not Django Models, there are created using Schematics Models
"""
# Local Libraries
from database.repository.models import Model
from database.repository.types import (
    DateTimeType,
    IntType,
    ModelType,
    StringType,
    UUIDType,
)
from api.models.template_models import (
    TemplateAppearanceModel,
    TemplateSenderModel,
    TemplateRelevancyModel,
    TemplateBehaviorModel,
)


class RecommendationsModel(Model):
    """
    This is the Recommendation Model.

    This holds the values and recommendation text.
    """

    recommendations_uuid = UUIDType()
    name = StringType()
    description = StringType()
    deception_level = IntType()

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


def validate_recommendations(data_object):
    """
    This validates recommendations data.

    This shows basic validation for the model.
    """
    return RecommendationsModel(data_object).validate()
