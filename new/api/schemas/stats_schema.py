"""Stats schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.template_schema import TemplateSchema


class CycleStatsEventMetrics(Schema):
    """CycleStatsEventMetrics."""

    count = fields.Integer()
    average = fields.Integer()
    minimum = fields.Integer()
    maximum = fields.Integer()
    median = fields.Integer()
    ratio = fields.Float()
    rank = fields.Integer()


class CycleStatsEvents(Schema):
    """CycleStatsEvents."""

    sent = fields.Nested(CycleStatsEventMetrics)
    opened = fields.Nested(CycleStatsEventMetrics)
    clicked = fields.Nested(CycleStatsEventMetrics)


class CycleStatsLevel(Schema):
    """CycleStatsLevel."""

    high = fields.Nested(CycleStatsEvents)
    moderate = fields.Nested(CycleStatsEvents)
    low = fields.Nested(CycleStatsEvents)
    all = fields.Nested(CycleStatsEvents)


class TemplateStats(CycleStatsEvents):
    """TemplateStats."""

    template_uuid = fields.Str()
    template = fields.Nested(TemplateSchema)
    deception_level = fields.Str()


class MaxmindStats(Schema):
    """MaxmindStats."""

    asn_org = fields.Str()
    is_nonhuman = fields.Bool()
    ips = fields.List(fields.Str())
    cities = fields.List(fields.Str())
    opens = fields.Integer()
    clicks = fields.Integer()


class IndicatorStats(Schema):
    """IndicatorStats."""

    indicator = fields.Str()
    subindicator = fields.Str()
    score = fields.Str()
    clicks = fields.Integer()
    percentage = fields.Float()
    name = fields.Str()
    label = fields.Str()


class CycleStats(Schema):
    """CycleStats."""

    stats = fields.Nested(CycleStatsLevel)
    template_stats = fields.List(fields.Nested(TemplateStats))
    maxmind_stats = fields.List(fields.Nested(MaxmindStats))
    indicator_stats = fields.List(fields.Nested(IndicatorStats))
