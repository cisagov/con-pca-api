"""Report Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields


class SectorIndustryReportSchema(Schema):
    """SectorIndustryReportSchema."""

    subscription_count = fields.Integer()
    cycle_count = fields.Integer()


class AggregateReportsSchema(Schema):
    """AggregateStatsSchema."""

    customers_enrolled = fields.Integer()
    monthly_reports_sent = fields.Integer()
    cycle_reports_sent = fields.Integer()
    yearly_reports_sent = fields.Integer()
    federal_stats = fields.Nested(SectorIndustryReportSchema())
    state_stats = fields.Nested(SectorIndustryReportSchema())
    local_stats = fields.Nested(SectorIndustryReportSchema())
    tribal_stats = fields.Nested(SectorIndustryReportSchema())
    private_stats = fields.Nested(SectorIndustryReportSchema())
    click_rate_across_all_customers = fields.Float()
    average_time_to_click_all_customers = fields.Str()
