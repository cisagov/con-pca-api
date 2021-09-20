"""Template Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class TemplateAppearanceSchema(Schema):
    """TemplateAppearanceSchema."""

    grammar = fields.Integer()
    link_domain = fields.Integer()
    logo_graphics = fields.Integer()


class TemplateSenderSchema(Schema):
    """TemplateSenderSchema."""

    external = fields.Integer()
    internal = fields.Integer()
    authoritative = fields.Integer()


class TemplateRelevancySchema(Schema):
    """TemplateRelevancySchema."""

    organization = fields.Integer()
    public_news = fields.Integer()


class TemplateBehaviorSchema(Schema):
    """TemplateBehaviorSchema."""

    fear = fields.Integer()
    duty_obligation = fields.Integer()
    curiosity = fields.Integer()
    greed = fields.Integer()


class TemplateIndicatorSchema(Schema):
    """TemplateIndicatorSchema."""

    appearance = fields.Nested(TemplateAppearanceSchema)
    sender = fields.Nested(TemplateSenderSchema)
    relevancy = fields.Nested(TemplateRelevancySchema)
    behavior = fields.Nested(TemplateBehaviorSchema)


class TemplateSchema(BaseSchema):
    """TemplateSchema."""

    template_uuid = fields.Str(required=True)
    name = fields.Str(required=True)
    landing_page_uuid = fields.Str(required=False, allow_none=True)
    sending_profile_uuid = fields.Str(required=False, allow_none=True)
    deception_score = fields.Integer()
    from_address = fields.Str(required=True)
    retired = fields.Bool(missing=False)
    retired_description = fields.Str(default="", allow_none=True)
    subject = fields.Str()
    text = fields.Str()
    html = fields.Str()
    indicators = fields.Nested(TemplateIndicatorSchema)
