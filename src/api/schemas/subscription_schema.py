"""Subscription schema."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.customer_schema import CustomerContactSchema, CustomerSchema
from api.schemas.fields import DateTimeField
from api.schemas.target_schema import TargetTimelineSchema
from api.schemas.template_schema import TemplateSchema


class SubscriptionNotificationSchema(Schema):
    """SubscriptionNotificationSchema."""

    message_type = fields.Str()
    sent = DateTimeField()
    email_to = fields.List(fields.Str())
    email_from = fields.Str()


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

    task_uuid = fields.Str()
    task_type = fields.Str(
        validate=validate.OneOf(
            [
                "start_subscription_email",
                "status_report",
                "cycle_report",
                "yearly_report",
                "thirty_day_reminder",
                "fifteen_day_reminder",
                "five_day_reminder",
                "safelisting_reminder",
                "end_cycle",
                "start_next_cycle",
            ]
        )
    )
    scheduled_date = DateTimeField()
    executed = fields.Bool(load_default=False)
    executed_date = DateTimeField(required=False)
    error = fields.Str(required=False, allow_none=True)


class SubscriptionTestSchema(Schema):
    """SubscriptionTestSchema."""

    test_uuid = fields.Str()
    email = fields.Str()
    template = fields.Nested(TemplateSchema)
    first_name = fields.Str()
    last_name = fields.Str()
    sent = fields.Bool()
    sent_date = DateTimeField()
    opened = fields.Bool()
    clicked = fields.Bool()
    timeline = fields.List(fields.Nested(TargetTimelineSchema))
    error = fields.Str(required=False, allow_none=True)


class SubscriptionSchema(BaseSchema):
    """SubscripionSchema."""

    name = fields.Str()
    customer_id = fields.Str()
    customer_oid = fields.Raw()
    sending_profile_id = fields.Str()
    sending_profile_oid = fields.Raw()
    target_domain = fields.Str()
    customer = fields.Nested(CustomerSchema)
    start_date = DateTimeField()
    primary_contact = fields.Nested(CustomerContactSchema)
    admin_email = fields.Str()
    operator_email = fields.Str()
    status = fields.Str(
        validate=validate.OneOf(["created", "queued", "running", "stopped"])
    )
    cycle_start_date = DateTimeField(allow_none=True)
    target_email_list = fields.List(fields.Nested(SubscriptionTargetSchema))
    templates_selected = fields.List(fields.Str())
    next_templates = fields.List(fields.Str())
    continuous_subscription = fields.Bool()
    buffer_time_minutes = fields.Integer()
    cycle_length_minutes = fields.Integer()
    cooldown_minutes = fields.Integer()
    report_frequency_minutes = fields.Integer()
    tasks = fields.List(fields.Nested(SubscriptionTasksSchema))
    processing = fields.Bool()
    archived = fields.Bool()
    page = fields.String()
    page_count = fields.String()
    sortby = fields.String()
    sortorder = fields.String()
    notification_history = fields.List(fields.Nested(SubscriptionNotificationSchema))
    phish_header = fields.Str()
    reporting_password = fields.Str()
    test_results = fields.List(fields.Nested(SubscriptionTestSchema))
    landing_page_id = fields.Str(required=False, allow_none=True)
    landing_page_oid = fields.Raw(required=False, allow_none=True)
    landing_domain = fields.Str()  # The landing domain for simulated phishing URLs.
    landing_page_url = fields.Str()  # The URL to redirect to after landing domain.
