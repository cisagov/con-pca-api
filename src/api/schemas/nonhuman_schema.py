"""NonHuman Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class NonHumanSchema(BaseSchema):
    """NonHumanSchema."""

    nonhuman_uuid = fields.Str(required=True)
    asn_org = fields.Str(required=True)
