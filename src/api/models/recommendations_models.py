"""Recommendation Models."""
# cisagov Libraries
from api.models.template_models import (
    TemplateAppearanceModel,
    TemplateBehaviorModel,
    TemplateRelevancyModel,
    TemplateSenderModel,
)
from database.repository.models import Model
from database.repository.types import DateTimeType, ModelType, StringType, UUIDType


class RecommendationsModel(Model):
    """Recommendation Model."""

    recommendations_uuid = UUIDType()
    name = StringType()
    description = StringType()

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
