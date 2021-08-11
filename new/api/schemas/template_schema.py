"""Template Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class TemplateAppearanceSchema(Schema):
    """TemplateAppearanceSchema."""

    grammar = fields.Number()
    link_domain = fields.Number()
    logo_graphics = fields.Number()


class TemplateSenderSchema(Schema):
    """TemplateSenderSchema."""

    external = fields.Number()
    internal = fields.Number()
    authoritative = fields.Number()


class TemplateRelevancySchema(Schema):
    """TemplateRelevancySchema."""

    organization = fields.Number()
    public_news = fields.Number()


class TemplateBehaviorSchema(Schema):
    """TemplateBehaviorSchema."""

    fear = fields.Number()
    duty_obligation = fields.Number()
    curiosity = fields.Number()
    greed = fields.Number()


class TemplateSchema(BaseSchema):
    """TemplateSchema."""

    template_uuid = fields.Str(required=True)
    name = fields.Str(required=True)
    landing_page_uuid = fields.Str(required=False, allow_none=True)
    sending_profile_uuid = fields.Str(required=False, allow_none=True)
    deception_score = fields.Number()
    from_address = fields.Str(required=True)
    retired = fields.Bool(default=False)
    retired_description = fields.Str(default="", allow_none=True)
    subject = fields.Str()
    text = fields.Str()
    html = fields.Str()

    # Score data
    appearance = fields.Nested(TemplateAppearanceSchema)
    sender = fields.Nested(TemplateSenderSchema)
    relevancy = fields.Nested(TemplateRelevancySchema)
    behavior = fields.Nested(TemplateBehaviorSchema)
