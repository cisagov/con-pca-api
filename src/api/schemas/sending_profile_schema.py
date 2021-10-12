"""Sending Profile Schemas."""

# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class HeaderSchema(Schema):
    """HeaderSchema."""

    key = fields.Str()
    value = fields.Str()


class SendingProfileSchema(BaseSchema):
    """SendingProfileSchema."""

    name = fields.Str(required=True)
    username = fields.Str()
    password = fields.Str()
    host = fields.Str()
    interface_type = fields.Str(default="SMTP")
    from_address = fields.Str()
    ignore_cert_errors = fields.Bool()
    headers = fields.List(fields.Nested(HeaderSchema))
