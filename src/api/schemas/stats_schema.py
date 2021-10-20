"""Stats schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.template_schema import TemplateSchema


class CycleStatsEventMetricsSchema(Schema):
    """CycleStatsEventMetrics."""

    count = fields.Integer()
    average = fields.Integer()
    minimum = fields.Integer()
    maximum = fields.Integer()
    median = fields.Integer()
    ratio = fields.Float()
    rank = fields.Integer()


class CycleStatsEventsSchema(Schema):
    """CycleStatsEvents."""

    sent = fields.Nested(CycleStatsEventMetricsSchema)
    opened = fields.Nested(CycleStatsEventMetricsSchema)
    clicked = fields.Nested(CycleStatsEventMetricsSchema)


class CycleStatsLevelSchema(Schema):
    """CycleStatsLevel."""

    high = fields.Nested(CycleStatsEventsSchema)
    moderate = fields.Nested(CycleStatsEventsSchema)
    low = fields.Nested(CycleStatsEventsSchema)
    all = fields.Nested(CycleStatsEventsSchema)


class TemplateStatsSchema(CycleStatsEventsSchema):
    """TemplateStats."""

    template_id = fields.Str()
    template = fields.Nested(TemplateSchema)
    deception_level = fields.Str()


class MaxmindStatsSchema(Schema):
    """MaxmindStats."""

    asn_org = fields.Str()
    is_nonhuman = fields.Bool()
    ips = fields.List(fields.Str())
    cities = fields.List(fields.Str())
    opens = fields.Integer()
    clicks = fields.Integer()


class IndicatorStatsSchema(CycleStatsEventsSchema):
    """IndicatorStats."""

    group = fields.Str()
    indicator = fields.Str()
    value = fields.Integer()
    label = fields.Str()


class TimeStatsSchema(Schema):
    """TimeStatsSchema."""

    one_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    three_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    five_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    fifteen_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    thirty_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    sixty_minutes = fields.Nested(CycleStatsEventMetricsSchema)
    two_hours = fields.Nested(CycleStatsEventMetricsSchema)
    three_hours = fields.Nested(CycleStatsEventMetricsSchema)
    four_hours = fields.Nested(CycleStatsEventMetricsSchema)
    one_day = fields.Nested(CycleStatsEventMetricsSchema)


class CycleStatsSchema(Schema):
    """CycleStats."""

    stats = fields.Nested(CycleStatsLevelSchema)
    template_stats = fields.List(fields.Nested(TemplateStatsSchema))
    maxmind_stats = fields.List(fields.Nested(MaxmindStatsSchema))
    indicator_stats = fields.List(fields.Nested(IndicatorStatsSchema))
    time_stats = fields.Nested(TimeStatsSchema)
