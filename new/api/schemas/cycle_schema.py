"""Cycle schema."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from api.schemas.subscription_schema import SubscriptionTargetSchema


class TimelineDetails(Schema):
    """TimelineDetails."""

    user_agent = fields.Str(required=False, allow_none=True)
    ip = fields.Str(required=False, allow_none=True)
    asn_org = fields.Str(required=False, allow_none=True)
    city = fields.Str(required=False, allow_none=True)


class CycleTargetTimeline(Schema):
    """CycleTargetTimeline."""

    time = fields.DateTime()
    message = fields.Str(validate=validate.OneOf(["opened", "clicked"]))
    details = fields.Nested(TimelineDetails)


class CycleTargetSchema(SubscriptionTargetSchema):
    """CycleTargetSchema."""

    target_uuid = fields.Str()
    template_uuid = fields.Str()
    deception_level = fields.Str(validate=validate.OneOf(["low", "moderate", "high"]))
    send_date = DateTimeField()
    sent = fields.Bool(missing=False)
    sent_date = DateTimeField()
    error = fields.Str(required=False, allow_none=True)
    timeline = fields.List(fields.Nested(CycleTargetTimeline))


class CycleSchema(BaseSchema):
    """CycleSchema."""

    cycle_uuid = fields.Str()
    subscription_uuid = fields.Str()
    template_uuids = fields.List(fields.Str())
    start_date = DateTimeField()
    end_date = DateTimeField()
    send_by_date = DateTimeField()
    active = fields.Bool()
    target_count = fields.Integer()
    targets = fields.List(fields.Nested(CycleTargetSchema))
    processing = fields.Bool()
