"""Customer Schemas."""
# Third-Party Libraries
from marshmallow import fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField


class CustomerContactSchema(BaseSchema):
    """CustomerContact Schema."""

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    title = fields.Str(required=False, allow_none=True)
    office_phone = fields.Str(required=False, allow_none=True)
    mobile_phone = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=True)
    notes = fields.Str(required=False, allow_none=True)
    active = fields.Bool(missing=True)


class CustomerSchema(BaseSchema):
    """Customer Schema."""

    name = fields.Str(required=True)
    identifier = fields.Str(required=True)
    address_1 = fields.Str(required=False, allow_none=True)
    address_2 = fields.Str(required=False, allow_none=True)
    city = fields.Str(required=False, allow_none=True)
    state = fields.Str(required=False, allow_none=True)
    zip_code = fields.Str(required=False, allow_none=True)
    customer_type = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Federal", "State", "Local", "Tribal", "Private"]),
    )
    contact_list = fields.List(fields.Nested(CustomerContactSchema))
    industry = fields.Str(required=False, allow_none=True)
    sector = fields.Str(required=False, allow_none=True)
    domain = fields.Str(required=False, allow_none=True)
    appendix_a_date = DateTimeField()
    archived = fields.Bool(missing=False)
    archived_description = fields.Str(dump_default="", allow_none=True)
