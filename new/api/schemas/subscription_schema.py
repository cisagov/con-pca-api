"""Subscription schema."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.customer_schema import CustomerContactSchema


class SubscriptionTargetSchema(Schema):
    """SubscriptionTargetSerializer."""

    email = fields.Email(required=True)
    first_name = fields.Str(required=False, allow_none=True)
    last_name = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, allow_none=True)


class SubscriptionTemplatesSelectedSchema(Schema):
    """SubscriptionTemplatesSelectedSchema."""

    low = fields.List(fields.Str())
    moderate = fields.List(fields.Str())
    high = fields.List(fields.Str())


class SubscriptionSchema(BaseSchema):
    """SubscripionSchema."""

    subscription_uuid = fields.Str()
    name = fields.Str()
    customer_uuid = fields.Str()
    target_domain = fields.Str()
    start_date = fields.DateTime()
    primary_contact = fields.Nested(CustomerContactSchema)
    admin_email = fields.Str()
    status = fields.Str(
        validate=validate.OneOf(["created", "queued", "running", "stopped"])
    )
    target_email_list = fields.List(fields.Nested(SubscriptionTargetSchema))
    target_email_list_cached_copy = fields.List(fields.Nested(SubscriptionTargetSchema))
    templates_selected = fields.Nested(SubscriptionTemplatesSelectedSchema)
    sending_profile_uuid = fields.Str()
    active = fields.Bool()
    continuous_subscription = fields.Bool()
    cycle_length_minutes = fields.Integer()
    cooldown_minutes = fields.Integer()
    report_frequency_minutes = fields.Integer()
