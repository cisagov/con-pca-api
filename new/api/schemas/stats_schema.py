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


class CycleStats(Schema):
    """CycleStats."""

    stats = fields.Nested(CycleStatsLevel)
    template_stats = fields.List(fields.Nested(TemplateStats))
