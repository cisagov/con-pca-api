"""Stats schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class CycleStatsEventMetrics(Schema):
    """CycleStatsEventMetrics."""

    count = fields.Integer()
    average = fields.Integer()
    minimum = fields.Integer()
    maximum = fields.Integer()
    median = fields.Integer()


class CycleStatsEvents(Schema):
    """CycleStatsEvents."""

    sent = fields.Nested(CycleStatsEventMetrics)
    opened = fields.Nested(CycleStatsEventMetrics)
    clicked = fields.Nested(CycleStatsEventMetrics)


class CycleStats(Schema):
    """CycleStats."""

    high = fields.Nested(CycleStatsEvents)
    moderate = fields.Nested(CycleStatsEvents)
    low = fields.Nested(CycleStatsEvents)
    all = fields.Nested(CycleStatsEvents)
