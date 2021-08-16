"""Subscription schema."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.customer_schema import CustomerContactSchema
from api.schemas.fields import DateTimeField


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


class SubscriptionTasksSchema(Schema):
    """SubscriptionTasksSchema."""

    task_type = fields.Str(
        validate=validate.OneOf(
            [
                "start_subscription_email",
                "monthly_report",
                "cycle_report",
                "yearly_report",
                "start_new_cycle",
                "stop_subscription",
            ]
        )
    )
    scheduled_date = DateTimeField()
    executed = fields.Bool(missing=False)
    executed_date = DateTimeField(required=False)
    error = fields.Str(required=False, allow_none=True)


class SubscriptionSchema(BaseSchema):
    """SubscripionSchema."""

    subscription_uuid = fields.Str()
    name = fields.Str()
    customer_uuid = fields.Str()
    target_domain = fields.Str()
    start_date = DateTimeField()
    primary_contact = fields.Nested(CustomerContactSchema)
    admin_email = fields.Str()
    status = fields.Str(
        validate=validate.OneOf(["created", "queued", "running", "stopped"])
    )
    target_email_list = fields.List(fields.Nested(SubscriptionTargetSchema))
    templates_selected = fields.Nested(SubscriptionTemplatesSelectedSchema)
    sending_profile_uuid = fields.Str()
    continuous_subscription = fields.Bool()
    cycle_length_minutes = fields.Integer()
    cooldown_minutes = fields.Integer()
    report_frequency_minutes = fields.Integer()
    tasks = fields.List(fields.Nested(SubscriptionTasksSchema))
