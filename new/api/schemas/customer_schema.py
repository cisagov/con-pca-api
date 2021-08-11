"""Customer Schemas."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class CustomerContactSchema(BaseSchema):
    """CustomerContact Schema."""

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    title = fields.Str(required=False, allow_none=True)
    office_phone = fields.Str(required=False, allow_none=True)
    mobile_phone = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=True)
    notes = fields.Str(required=False, allow_none=True)
    active = fields.Bool(default=True)


class CustomerSchema(BaseSchema):
    """Customer Schema."""

    customer_uuid = fields.Str(required=True)
    name = fields.Str(required=True)
    identifier = fields.Str(required=True)
    address_1 = fields.Str(required=False, allow_none=True)
    address_2 = fields.Str(required=False, allow_none=True)
    city = fields.Str(required=False, allow_none=True)
    state = fields.Str(required=False, allow_none=True)
    zip_code = fields.Str(required=False, allow_none=True)
    customer_type = fields.Str(required=False, allow_none=True)
    contact_list = fields.List(fields.Nested(CustomerContactSchema))
    industry = fields.Str(required=False, allow_none=True)
    sector = fields.Str(required=False, allow_none=True)
