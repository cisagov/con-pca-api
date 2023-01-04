"""Failed Email Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField


class FailedEmailSchema(BaseSchema):
    """FailedEmailSchema."""

    recipient = fields.Str()
    recipient_address = fields.Str()
    recipient_domain = fields.Str()
    sent_time = DateTimeField()
    error_type = fields.Str()
    message_id = fields.Str()
    reason = fields.Str()
    removed = fields.Bool(load_default=False)
