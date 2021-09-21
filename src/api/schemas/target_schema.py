"""Target Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField


class TimelineDetailsSchema(Schema):
    """TimelineDetails."""

    user_agent = fields.Str(required=False, allow_none=True)
    ip = fields.Str(required=False, allow_none=True)
    asn_org = fields.Str(required=False, allow_none=True)
    city = fields.Str(required=False, allow_none=True)
    country = fields.Str(required=False, allow_none=True)


class TargetTimelineSchema(Schema):
    """CycleTargetTimeline."""

    time = fields.DateTime()
    message = fields.Str(validate=validate.OneOf(["opened", "clicked"]))
    details = fields.Nested(TimelineDetailsSchema)


class TargetSchema(BaseSchema):
    """CycleTargetSchema."""

    target_uuid = fields.Str()
    cycle_uuid = fields.Str()
    subscription_uuid = fields.Str()
    template_uuid = fields.Str()
    email = fields.Email(required=True)
    first_name = fields.Str(required=False, allow_none=True)
    last_name = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, allow_none=True)
    deception_level = fields.Str(validate=validate.OneOf(["low", "moderate", "high"]))
    send_date = DateTimeField()
    sent = fields.Bool(missing=False)
    sent_date = DateTimeField()
    error = fields.Str(required=False, allow_none=True)
    timeline = fields.List(fields.Nested(TargetTimelineSchema))
