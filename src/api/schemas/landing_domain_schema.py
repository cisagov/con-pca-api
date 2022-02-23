"""Landing domain schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class LandingDomainSchema(BaseSchema):
    """LandingDomainSchema."""

    domain = fields.Str(required=True)
