"""Report Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.stats_schema import CycleStatsLevelSchema


class SectorIndustryReportSchema(Schema):
    """SectorIndustryReportSchema."""

    subscription_count = fields.Integer()
    cycle_count = fields.Integer()
    emails_sent = fields.Integer()
    emails_clicked = fields.Integer()
    emails_clicked_ratio = fields.Float()


class EmailSendingReportSchema(Schema):
    """EmailSendingReportSchema."""

    emails_sent_24_hours = fields.Integer()
    emails_scheduled_24_hours = fields.Integer()
    emails_sent_on_time_24_hours_ratio = fields.Float()
    emails_clicked_24_hours = fields.Integer()
    emails_sent_7_days = fields.Integer()
    emails_scheduled_7_days = fields.Integer()
    emails_sent_on_time_7_days_ratio = fields.Float()
    emails_clicked_7_days = fields.Integer()
    emails_sent_30_days = fields.Integer()
    emails_scheduled_30_days = fields.Integer()
    emails_sent_on_time_30_days_ratio = fields.Float()
    emails_clicked_30_days = fields.Integer()


class TaskReportSchema(Schema):
    """TaskReportSchema."""

    tasks_succeeded_24_hours = fields.Integer()
    tasks_scheduled_24_hours = fields.Integer()
    tasks_succeeded_24_hours_ratio = fields.Float()
    tasks_succeeded_7_days = fields.Integer()
    tasks_scheduled_7_days = fields.Integer()
    tasks_succeeded_7_days_ratio = fields.Float()
    tasks_succeeded_30_days = fields.Integer()
    tasks_scheduled_30_days = fields.Integer()
    tasks_succeeded_30_days_ratio = fields.Float()


class AggregateReportsSchema(Schema):
    """AggregateStatsSchema."""

    customers_enrolled = fields.Integer()
    customers_active = fields.Integer()
    status_reports_sent = fields.Integer()
    cycle_reports_sent = fields.Integer()
    yearly_reports_sent = fields.Integer()
    email_sending_stats = fields.Nested(EmailSendingReportSchema())
    task_stats = fields.Nested(TaskReportSchema())
    new_subscriptions = fields.Integer()
    ongoing_subscriptions = fields.Integer()
    stopped_subscriptions = fields.Integer()
    federal_stats = fields.Nested(SectorIndustryReportSchema())
    state_stats = fields.Nested(SectorIndustryReportSchema())
    local_stats = fields.Nested(SectorIndustryReportSchema())
    tribal_stats = fields.Nested(SectorIndustryReportSchema())
    private_stats = fields.Nested(SectorIndustryReportSchema())
    all_customer_stats = fields.Nested(CycleStatsLevelSchema)
