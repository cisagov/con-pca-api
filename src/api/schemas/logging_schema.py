"""Logging schema."""
# Third-Party Libraries
from marshmallow import fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class LoggingSchema(BaseSchema):
    """LoggingSchema."""

    error_message = fields.Str()
    file = fields.Str(required=False, allow_none=True)
    source = fields.Str(required=False, allow_none=True)
    source_type = fields.Str(
        validate=validate.OneOf(["subscription", "cycle", "target"]),
        required=False,
        allow_none=True,
    )
