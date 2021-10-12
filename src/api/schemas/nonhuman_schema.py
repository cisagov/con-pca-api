"""NonHuman Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class NonHumanSchema(BaseSchema):
    """NonHumanSchema."""

    asn_org = fields.Str(required=True)
