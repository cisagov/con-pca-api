"""User Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField


class UserSchema(BaseSchema):
    """UserSchema."""

    username = fields.Str(required=True)
    last_login = DateTimeField(allow_none=True)
