"""Cycle schema."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from api.schemas.stats_schema import CycleStatsSchema


class CycleManualReportsSchema(BaseSchema):
    """CycleReportsSchema."""

    email = fields.Str()
    report_date = DateTimeField()


class CycleTasksSchema(Schema):
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
                "start_next_cycle",
                "end_cycle",
            ]
        )
    )
    scheduled_date = DateTimeField()
    executed = fields.Bool(load_default=False)
    executed_date = DateTimeField(required=False)
    error = fields.Str(required=False, allow_none=True)


class CycleSchema(BaseSchema):
    """CycleSchema."""

    subscription_id = fields.Str()
    template_ids = fields.List(fields.Str())
    start_date = DateTimeField()
    end_date = DateTimeField()
    send_by_date = DateTimeField()
    active = fields.Bool()
    target_count = fields.Integer()
    tasks = fields.List(fields.Nested(CycleTasksSchema), required=False)
    dirty_stats = fields.Bool()
    stats = fields.Nested(CycleStatsSchema)
    nonhuman_stats = fields.Nested(CycleStatsSchema)
    phish_header = fields.Str()
    manual_reports = fields.List(fields.Nested(CycleManualReportsSchema))
