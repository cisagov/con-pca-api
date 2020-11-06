from database.repository.models import Model
from database.repository.types import (
    StringType,
    EmailType,
    BooleanType,
    UUIDType,
    DateTimeType,
)


class DHSContactModel(Model):
    """
    This is the DHSContact Model.

    This is a format to hold contact information in the subscription model.
    first_name = StringType(required=True)
    last_name = StringType(required=True)
    title = StringType(required=True)
    phone = StringType()
    email = EmailType(required=True)
    notes = StringType()
    """

    dhs_contact_uuid = UUIDType()
    first_name = StringType()
    last_name = StringType()
    title = StringType()
    office_phone = StringType()
    mobile_phone = StringType()
    email = EmailType()
    notes = StringType()
    active = BooleanType()

    # db data
    created_by = StringType()
    cb_timestamp = DateTimeType()
    last_updated_by = StringType()
    lub_timestamp = DateTimeType()
