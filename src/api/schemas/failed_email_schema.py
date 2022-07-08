"""Failed Email Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField


class FailedEmailSchema(BaseSchema):
    """FailedEmailSchema."""

    recipient = fields.Str()
    sent_time = DateTimeField()
    reason = fields.Str()
    message_id = fields.Str()
    delivery_status = fields.Str()
