"""Cycle schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from api.schemas.stats_schema import CycleStatsSchema


class CycleSchema(BaseSchema):
    """CycleSchema."""

    subscription_id = fields.Str()
    template_ids = fields.List(fields.Str())
    start_date = DateTimeField()
    end_date = DateTimeField()
    send_by_date = DateTimeField()
    active = fields.Bool()
    target_count = fields.Integer()
    dirty_stats = fields.Bool()
    stats = fields.Nested(CycleStatsSchema)
    nonhuman_stats = fields.Nested(CycleStatsSchema)
    phish_header = fields.Str()
