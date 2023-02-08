"""Template Schemas."""
# Third-Party Libraries
from marshmallow import Schema, fields, validate

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

    name = fields.Str(required=True)
    landing_page_id = fields.Str(required=False, allow_none=True)
    landing_page_oid = fields.Raw(required=False, allow_none=True)
    sending_profile_id = fields.Str(required=False, allow_none=True)
    sending_profile_oid = fields.Raw(required=False, allow_none=True)
    deception_score = fields.Int(validate=validate.Range(min=1, max=6))
    from_address = fields.Str(required=True)
    retired = fields.Bool(load_default=False)
    retired_description = fields.Str(dump_default="", allow_none=True)
    sophisticated = fields.List(fields.Str(), allow_none=True)
    red_flag = fields.List(fields.Str(), allow_none=True)
    subject = fields.Str()
    text = fields.Str()
    html = fields.Str()
    indicators = fields.Nested(TemplateIndicatorSchema)
