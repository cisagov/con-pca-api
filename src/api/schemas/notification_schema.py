"""Notifiation Schemas."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class NotificationSchema(BaseSchema):
    """NotificationSchema."""

    name = fields.Str(required=True)
    task_name = fields.Str(required=True)
    has_attachment = fields.Bool(load_default=False)
    subject = fields.Str()
    text = fields.Str()
    html = fields.Str()
