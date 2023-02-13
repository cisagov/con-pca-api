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

    time = DateTimeField()
    message = fields.Str(validate=validate.OneOf(["opened", "clicked"]))
    details = fields.Nested(TimelineDetailsSchema)


class TargetSchema(BaseSchema):
    """CycleTargetSchema."""

    cycle_id = fields.Str()
    subscription_id = fields.Str()
    template_id = fields.Str()
    email = fields.Email(required=True)
    first_name = fields.Str(required=False, allow_none=True)
    last_name = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, allow_none=True)
    deception_level = fields.Str(validate=validate.OneOf(["low", "moderate", "high"]))
    deception_level_int = fields.Integer()
    send_date = DateTimeField()
    sent = fields.Bool(load_default=False)
    sent_date = DateTimeField()
    error = fields.Str(required=False, allow_none=True)
    timeline = fields.List(fields.Nested(TargetTimelineSchema))
