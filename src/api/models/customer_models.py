"""
Customer Models.

These are not Django Models, there are created using Schematics Models
"""
# Third-Party Libraries
from database.repository.models import Model
from database.repository.types import (
    BooleanType,
    DateTimeType,
    EmailType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)


class CustomerContactModel(Model):
    """
    This is the SubscriptionContact Model.

    This is a format to hold contact information in the subscription model.
    first_name = StringType(required=True)
    last_name = StringType(required=True)
    title = StringType(required=True)
    phone = StringType()
    email = EmailType(required=True)
    notes = StringType()
    """

    first_name = StringType(required=True)
    last_name = StringType(required=True)
    title = StringType()
    office_phone = StringType()
    mobile_phone = StringType()
    email = EmailType(required=True)
    notes = StringType()
    active = BooleanType(required=True)


class CustomerModel(Model):
    """
    This is the Customer Model.

    This controls all data needed in saving the model. Current fields are:
    customer_uuid
    name,

    """

    customer_uuid = UUIDType()
    name = StringType()
    identifier = StringType()
    address_1 = StringType()
    address_2 = StringType()
    city = StringType()
    state = StringType()
    zip_code = StringType()
    customer_type = StringType()
    contact_list = ListType(ModelType(CustomerContactModel))
    sector = StringType()
    industry = StringType()
    # db tracking data added below
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()
