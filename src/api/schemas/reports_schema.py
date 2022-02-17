"""Report Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.stats_schema import CycleStatsLevelSchema


class SectorIndustryReportSchema(Schema):
    """SectorIndustryReportSchema."""

    subscription_count = fields.Integer()
    cycle_count = fields.Integer()


class SendingProfileMetrics(Schema):
    """Sending Profile Metrics."""

    domain = fields.Str()
    customers = fields.Int()


class AggregateReportsSchema(Schema):
    """AggregateStatsSchema."""

    customers_enrolled = fields.Integer()
    status_reports_sent = fields.Integer()
    cycle_reports_sent = fields.Integer()
    yearly_reports_sent = fields.Integer()
    new_subscriptions = fields.Integer()
    ongoing_subscriptions = fields.Integer()
    stopped_subscriptions = fields.Integer()
    sending_profile_metrics = fields.List(fields.Nested(SendingProfileMetrics()))
    federal_stats = fields.Nested(SectorIndustryReportSchema())
    state_stats = fields.Nested(SectorIndustryReportSchema())
    local_stats = fields.Nested(SectorIndustryReportSchema())
    tribal_stats = fields.Nested(SectorIndustryReportSchema())
    private_stats = fields.Nested(SectorIndustryReportSchema())
    all_customer_stats = fields.Nested(CycleStatsLevelSchema)
