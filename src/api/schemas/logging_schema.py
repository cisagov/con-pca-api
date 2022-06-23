"""Logging schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class LoggingSchema(BaseSchema):
    """LoggingSchema."""

    error_message = fields.Str()
