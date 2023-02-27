"""Notifiation Schemas."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class NotificationSchema(BaseSchema):
    """NotificationSchema."""

    name = fields.Str(required=True)
    task_name = fields.Str(required=True)
    retired = fields.Bool(load_default=False)
    retired_description = fields.Str(dump_default="", allow_none=True)
    subject = fields.Str()
    text = fields.Str()
    html = fields.Str()
