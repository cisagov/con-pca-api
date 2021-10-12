"""Recommendation schema."""
# Third-Party Libraries
from marshmallow import fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class RecommendationsSchema(BaseSchema):
    """
    RecommendationsSchema.

    This is the schema on how the recommendations are stored in the database.
    """

    type = fields.Str(validate=validate.OneOf(["indicator", "level"]))
    value = fields.Str()
    recommendation = fields.Str()
    group = fields.Str()
    indicator = fields.Str()
