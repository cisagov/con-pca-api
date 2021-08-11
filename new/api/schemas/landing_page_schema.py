"""Landing page schemas."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class LandingPageSchema(BaseSchema):
    """LandingPageSchema."""

    landing_page_uuid = fields.Str(required=True)
    name = fields.Str(required=True)
    is_default_template = fields.Bool(default=False)
    html = fields.Str()
